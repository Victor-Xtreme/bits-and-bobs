"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SidebarProvider = void 0;
const vscode = __importStar(require("vscode"));
const node_fetch_1 = __importDefault(require("node-fetch"));
const config_1 = require("./config");
class SidebarProvider {
    constructor(_extensionUri, _statusBarItem) {
        this._extensionUri = _extensionUri;
        this._statusBarItem = _statusBarItem;
        this._retryCount = 0;
        this._maxRetries = 3;
    }
    /**
     * Public method to trigger analysis (called from extension.ts)
     */
    triggerAnalysis() {
        this._analyzeWorkspace();
    }
    resolveWebviewView(webviewView) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'analyzeWorkspace':
                    await this._analyzeWorkspace();
                    break;
            }
        });
    }
    revive(panel) {
        this._view = panel;
    }
    async _analyzeWorkspace() {
        // Get workspace folder path
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            this._statusBarItem.text = '$(error) RepoSense: Error';
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'error',
                    message: 'No workspace folder open'
                });
            }
            return;
        }
        const workspacePath = workspaceFolders[0].uri.fsPath;
        try {
            // Update status bar to analyzing
            this._statusBarItem.text = '$(sync~spin) RepoSense: Analyzing...';
            // Send initial status to webview if available
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'status',
                    message: 'Starting analysis...'
                });
            }
            const config = (0, config_1.getConfig)();
            // Send POST request to start analysis
            const response = await (0, node_fetch_1.default)(`${config.backendUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ local_path: workspacePath }),
                timeout: config.requestTimeoutMs
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }
            const data = await response.json();
            const jobId = data.job_id;
            // Send initial progress update
            this._updateProgress(data.progress);
            // Start polling for results
            this._startPolling(jobId);
        }
        catch (error) {
            this._statusBarItem.text = '$(error) RepoSense: Error';
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'error',
                    message: `Failed to start analysis: ${error instanceof Error ? error.message : String(error)}`
                });
            }
        }
    }
    _startPolling(jobId) {
        // Clear any existing polling interval
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
        }
        // Reset retry count for new polling session
        this._retryCount = 0;
        const config = (0, config_1.getConfig)();
        // Poll at configured interval
        this._pollingInterval = setInterval(async () => {
            await this._checkResults(jobId);
        }, config.pollingIntervalMs);
        // Also check immediately
        this._checkResults(jobId);
    }
    async _checkResults(jobId) {
        if (!this._view) {
            return;
        }
        try {
            const config = (0, config_1.getConfig)();
            const response = await (0, node_fetch_1.default)(`${config.backendUrl}/jobs/${jobId}`, {
                timeout: config.requestTimeoutMs
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const apiResponse = await response.json();
            // Reset retry count on successful response
            this._retryCount = 0;
            // Update progress display
            this._updateProgress(apiResponse.progress);
            // Handle different response types based on 'type' field
            if (apiResponse.type === 'result' && apiResponse.payload) {
                // Analysis completed successfully
                const result = apiResponse.payload;
                // Stop polling
                if (this._pollingInterval) {
                    clearInterval(this._pollingInterval);
                    this._pollingInterval = undefined;
                }
                // Update status bar with score
                this._statusBarItem.text = `$(graph) RepoSense: Score ${result.score.score}/100`;
                // Show completion notification
                vscode.window.showInformationMessage(`RepoSense: Analysis complete — Score ${result.score.score}/100`, 'View Details').then(selection => {
                    if (selection === 'View Details') {
                        vscode.commands.executeCommand('reposense-sidebar.focus');
                    }
                });
                // Send completion message with health score from payload.score.score
                if (this._view) {
                    this._view.webview.postMessage({
                        type: 'complete',
                        healthScore: result.score.score,
                        grade: result.score.grade,
                        summary: result.score.summary,
                        result: result
                    });
                }
            }
            else if (apiResponse.type === 'error' && apiResponse.payload) {
                // Analysis failed
                const error = apiResponse.payload;
                // Stop polling
                if (this._pollingInterval) {
                    clearInterval(this._pollingInterval);
                    this._pollingInterval = undefined;
                }
                // Update status bar to error
                this._statusBarItem.text = '$(error) RepoSense: Error';
                if (this._view) {
                    this._view.webview.postMessage({
                        type: 'error',
                        message: `${error.stage}: ${error.message} (${error.code})`
                    });
                }
            }
            // If type is 'request', continue polling (analysis still in progress)
        }
        catch (error) {
            // Retry logic: don't stop immediately, retry up to maxRetries times
            this._retryCount++;
            if (this._retryCount >= this._maxRetries) {
                // Stop polling after max retries
                if (this._pollingInterval) {
                    clearInterval(this._pollingInterval);
                    this._pollingInterval = undefined;
                }
                // Update status bar to error
                this._statusBarItem.text = '$(error) RepoSense: Error';
                if (this._view) {
                    this._view.webview.postMessage({
                        type: 'error',
                        message: `Failed to check results after ${this._maxRetries} retries: ${error instanceof Error ? error.message : String(error)}`
                    });
                }
            }
            // Otherwise, continue polling and retry
        }
    }
    _updateProgress(steps) {
        if (!this._view) {
            return;
        }
        const progressLines = [];
        for (const step of steps) {
            let icon = '';
            switch (step.status) {
                case 'done':
                    icon = '✓';
                    break;
                case 'active':
                    icon = '⟳';
                    break;
                case 'pending':
                    icon = '○';
                    break;
            }
            let line = `${icon} ${step.name}`;
            if (step.files_processed !== undefined && step.files_total !== undefined) {
                line += ` (${step.files_processed}/${step.files_total})`;
            }
            if (step.current_file) {
                line += `\n  → ${step.current_file}`;
            }
            progressLines.push(line);
        }
        this._view.webview.postMessage({
            type: 'progress',
            message: progressLines.join('\n')
        });
    }
    _getHtmlForWebview(webview) {
        const nonce = this._getNonce();
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>RepoSense</title>
    <style>
        body {
            padding: 20px;
            color: var(--vscode-foreground);
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
        }
        h1 {
            font-size: 1.5em;
            margin-bottom: 20px;
        }
        button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            cursor: pointer;
            border-radius: 2px;
            width: 100%;
            margin-bottom: 20px;
        }
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        #status {
            margin-top: 20px;
            padding: 15px;
            background-color: var(--vscode-editor-background);
            border-radius: 4px;
            white-space: pre-line;
            line-height: 1.6;
        }
        .health-score {
            font-size: 2em;
            font-weight: bold;
            color: var(--vscode-charts-green);
            margin: 20px 0;
        }
        .error {
            color: var(--vscode-errorForeground);
        }
        .progress {
            color: var(--vscode-charts-blue);
        }
    </style>
</head>
<body>
    <h1>RepoSense</h1>
    <button id="analyzeBtn">Analyze Workspace</button>
    <div id="status"></div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        const analyzeBtn = document.getElementById('analyzeBtn');
        const statusDiv = document.getElementById('status');

        analyzeBtn.addEventListener('click', () => {
            analyzeBtn.disabled = true;
            statusDiv.innerHTML = '';
            vscode.postMessage({ type: 'analyzeWorkspace' });
        });

        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.type) {
                case 'status':
                    statusDiv.innerHTML = '<div class="progress">' + message.message + '</div>';
                    break;
                
                case 'progress':
                    statusDiv.innerHTML = '<div class="progress">' + message.message + '</div>';
                    break;
                
                case 'complete':
                    analyzeBtn.disabled = false;
                    let resultHtml = '<div>✓ Analysis Complete!</div>';
                    resultHtml += '<div class="health-score">Score: ' + message.healthScore + ' (Grade: ' + message.grade + ')</div>';
                    
                    if (message.result) {
                        const result = message.result;
                        
                        // Show breakdown
                        if (result.score && result.score.breakdown) {
                            resultHtml += '<div style="margin-top: 15px;"><strong>Breakdown:</strong></div>';
                            resultHtml += '<div style="margin-left: 10px;">';
                            resultHtml += '• Quality: ' + result.score.breakdown.quality + '<br>';
                            resultHtml += '• Security: ' + result.score.breakdown.security + '<br>';
                            resultHtml += '• Documentation: ' + result.score.breakdown.documentation + '<br>';
                            resultHtml += '• Architecture: ' + result.score.breakdown.architecture;
                            resultHtml += '</div>';
                        }
                        
                        // Show top priorities
                        if (result.score && result.score.top_priorities && result.score.top_priorities.length > 0) {
                            resultHtml += '<div style="margin-top: 15px;"><strong>Top Priorities:</strong></div>';
                            resultHtml += '<div style="margin-left: 10px;">';
                            result.score.top_priorities.forEach((priority, idx) => {
                                resultHtml += (idx + 1) + '. ' + priority + '<br>';
                            });
                            resultHtml += '</div>';
                        }
                        
                        // Show summary
                        if (result.score && result.score.summary) {
                            resultHtml += '<div style="margin-top: 15px;"><strong>Summary:</strong></div>';
                            resultHtml += '<div style="margin-left: 10px;">' + result.score.summary + '</div>';
                        }
                        
                        // Show counts
                        resultHtml += '<div style="margin-top: 15px;"><strong>Analysis Details:</strong></div>';
                        resultHtml += '<div style="margin-left: 10px;">';
                        if (result.review && result.review.findings) {
                            resultHtml += '• Code Review Findings: ' + result.review.findings.length + '<br>';
                        }
                        if (result.security && result.security.security) {
                            resultHtml += '• Security Issues: ' + result.security.security.length + '<br>';
                        }
                        if (result.security && result.security.modernization) {
                            resultHtml += '• Modernization Items: ' + result.security.modernization.length + '<br>';
                        }
                        if (result.architecture && result.architecture.nodes) {
                            resultHtml += '• Architecture Nodes: ' + result.architecture.nodes.length + '<br>';
                        }
                        resultHtml += '</div>';
                    }
                    
                    statusDiv.innerHTML = resultHtml;
                    break;
                
                case 'error':
                    analyzeBtn.disabled = false;
                    statusDiv.innerHTML = '<div class="error">Error: ' + message.message + '</div>';
                    break;
            }
        });
    </script>
</body>
</html>`;
    }
    _getNonce() {
        let text = '';
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (let i = 0; i < 32; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }
    dispose() {
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
        }
    }
}
exports.SidebarProvider = SidebarProvider;
// Made with Bob
//# sourceMappingURL=SidebarProvider.js.map
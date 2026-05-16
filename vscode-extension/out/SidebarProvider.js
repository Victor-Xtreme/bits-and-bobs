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
class SidebarProvider {
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
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
        if (!this._view) {
            return;
        }
        // Get workspace folder path
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            this._view.webview.postMessage({
                type: 'error',
                message: 'No workspace folder open'
            });
            return;
        }
        const workspacePath = workspaceFolders[0].uri.fsPath;
        try {
            // Send initial status
            this._view.webview.postMessage({
                type: 'status',
                message: 'Starting analysis...'
            });
            // Send POST request to start analysis
            const response = await (0, node_fetch_1.default)('http://localhost:8000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ local_path: workspacePath })
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const jobId = data.job_id;
            // Start polling for results
            this._startPolling(jobId);
        }
        catch (error) {
            this._view.webview.postMessage({
                type: 'error',
                message: `Failed to start analysis: ${error instanceof Error ? error.message : String(error)}`
            });
        }
    }
    _startPolling(jobId) {
        // Clear any existing polling interval
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
        }
        // Poll every 3 seconds
        this._pollingInterval = setInterval(async () => {
            await this._checkResults(jobId);
        }, 3000);
        // Also check immediately
        this._checkResults(jobId);
    }
    async _checkResults(jobId) {
        if (!this._view) {
            return;
        }
        try {
            const response = await (0, node_fetch_1.default)(`http://localhost:8000/results/${jobId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            // Send progress update
            if (result.status === 'in_progress' || result.status === 'processing') {
                let progressMessage = 'Analyzing...';
                if (result.progress) {
                    const completedSteps = Object.entries(result.progress)
                        .filter(([_, completed]) => completed)
                        .map(([step, _]) => `✓ ${step} complete`);
                    if (completedSteps.length > 0) {
                        progressMessage = completedSteps.join('\n');
                    }
                }
                this._view.webview.postMessage({
                    type: 'progress',
                    message: progressMessage
                });
            }
            else if (result.status === 'completed' || result.status === 'complete') {
                // Stop polling
                if (this._pollingInterval) {
                    clearInterval(this._pollingInterval);
                    this._pollingInterval = undefined;
                }
                // Send completion message with health score
                this._view.webview.postMessage({
                    type: 'complete',
                    healthScore: result.health_score || 0
                });
            }
            else if (result.status === 'failed' || result.status === 'error') {
                // Stop polling
                if (this._pollingInterval) {
                    clearInterval(this._pollingInterval);
                    this._pollingInterval = undefined;
                }
                this._view.webview.postMessage({
                    type: 'error',
                    message: result.error || 'Analysis failed'
                });
            }
        }
        catch (error) {
            // Stop polling on error
            if (this._pollingInterval) {
                clearInterval(this._pollingInterval);
                this._pollingInterval = undefined;
            }
            this._view.webview.postMessage({
                type: 'error',
                message: `Failed to check results: ${error instanceof Error ? error.message : String(error)}`
            });
        }
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
                    statusDiv.innerHTML = 
                        '<div>Analysis Complete!</div>' +
                        '<div class="health-score">Health Score: ' + message.healthScore + '</div>';
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
import * as vscode from 'vscode';
import fetch from 'node-fetch';

interface AnalysisResult {
    job_id: string;
    status: string;
    progress?: {
        architect?: boolean;
        [key: string]: boolean | undefined;
    };
    health_score?: number;
    error?: string;
}

export class SidebarProvider implements vscode.WebviewViewProvider {
    _view?: vscode.WebviewView;
    _doc?: vscode.TextDocument;
    private _pollingInterval?: ReturnType<typeof setInterval>;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (data: { type: string }) => {
            switch (data.type) {
                case 'analyzeWorkspace':
                    await this._analyzeWorkspace();
                    break;
            }
        });
    }

    public revive(panel: vscode.WebviewView) {
        this._view = panel;
    }

    private async _analyzeWorkspace() {
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
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ local_path: workspacePath })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json() as { job_id: string };
            const jobId = data.job_id;

            // Start polling for results
            this._startPolling(jobId);

        } catch (error) {
            this._view.webview.postMessage({
                type: 'error',
                message: `Failed to start analysis: ${error instanceof Error ? error.message : String(error)}`
            });
        }
    }

    private _startPolling(jobId: string) {
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

    private async _checkResults(jobId: string) {
        if (!this._view) {
            return;
        }

        try {
            const response = await fetch(`http://localhost:8000/results/${jobId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json() as AnalysisResult;

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
            } else if (result.status === 'completed' || result.status === 'complete') {
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
            } else if (result.status === 'failed' || result.status === 'error') {
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

        } catch (error) {
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

    private _getHtmlForWebview(webview: vscode.Webview) {
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

    private _getNonce() {
        let text = '';
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (let i = 0; i < 32; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }

    public dispose() {
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
        }
    }
}

// Made with Bob

import * as vscode from 'vscode';
import fetch from 'node-fetch';
import { getConfig } from './config';

// Backend API Models (matching models.py)
type PayloadType = 'request' | 'result' | 'error';
type StepStatus = 'done' | 'active' | 'pending';
type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
type NodeType = 'entry' | 'service' | 'util' | 'config' | 'test';
type EdgeRelationship = 'imports' | 'extends' | 'calls';
type Effort = 'LOW' | 'MEDIUM' | 'HIGH';
type Grade = 'A' | 'B' | 'C' | 'D' | 'F';
type ErrorCode = 'PARSE_FAILED' | 'AGENT_TIMEOUT' | 'AGENT_INVALID_JSON' | 'WATSONX_UNAVAILABLE' | 'UNKNOWN';

interface ProgressStep {
    name: string;
    status: StepStatus;
    files_processed?: number;
    files_total?: number;
    current_file?: string;
}

interface GraphNode {
    id: string;
    label: string;
    type: NodeType;
    description: string;
}

interface GraphEdge {
    source: string;
    target: string;
    relationship: EdgeRelationship;
}

interface ArchitectureGraph {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

interface CodeReviewFinding {
    file: string;
    line: number;
    severity: Severity;
    issue: string;
    suggestion: string;
}

interface CodeReview {
    findings: CodeReviewFinding[];
}

interface DocParam {
    name: string;
    type: string;
    description: string;
}

interface DocEntry {
    function_name: string;
    description: string;
    params: DocParam[];
    returns: string;
    example: string;
}

interface TestCase {
    description: string;
    input: string;
    expected: string;
}

interface TestEntry {
    function_name: string;
    test_cases: TestCase[];
}

interface Documentation {
    docs: DocEntry[];
    tests: TestEntry[];
}

interface SecurityIssue {
    issue: string;
    severity: Severity;
    file: string;
    fix: string;
}

interface ModernizationItem {
    pattern: string;
    suggestion: string;
    effort: Effort;
}

interface SecurityReport {
    security: SecurityIssue[];
    modernization: ModernizationItem[];
}

interface ScoreBreakdown {
    quality: number;
    security: number;
    documentation: number;
    architecture: number;
}

interface HealthScore {
    score: number;
    grade: Grade;
    breakdown: ScoreBreakdown;
    summary: string;
    top_priorities: string[];
}

interface AnalysisResult {
    score: HealthScore;
    architecture: ArchitectureGraph;
    review: CodeReview;
    docs: Documentation;
    security: SecurityReport;
}

interface AnalysisError {
    code: ErrorCode;
    message: string;
    stage: string;
}

interface ApiResponse {
    type: PayloadType;
    job_id: string;
    progress: ProgressStep[];
    payload?: AnalysisResult | AnalysisError | null;
}

export class SidebarProvider implements vscode.WebviewViewProvider {
    _view?: vscode.WebviewView;
    _doc?: vscode.TextDocument;
    private _pollingInterval?: ReturnType<typeof setInterval>;
    private _retryCount: number = 0;
    private readonly _maxRetries: number = 3;

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

            const config = getConfig();
            
            // Send POST request to start analysis
            const response = await fetch(`${config.backendUrl}/analyze`, {
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

            const data = await response.json() as ApiResponse;
            const jobId = data.job_id;

            // Send initial progress update
            this._updateProgress(data.progress);

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

        // Reset retry count for new polling session
        this._retryCount = 0;

        const config = getConfig();
        
        // Poll at configured interval
        this._pollingInterval = setInterval(async () => {
            await this._checkResults(jobId);
        }, config.pollingIntervalMs);

        // Also check immediately
        this._checkResults(jobId);
    }

    private async _checkResults(jobId: string) {
        if (!this._view) {
            return;
        }

        try {
            const config = getConfig();
            const response = await fetch(`${config.backendUrl}/jobs/${jobId}`, {
                timeout: config.requestTimeoutMs
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const apiResponse = await response.json() as ApiResponse;

            // Reset retry count on successful response
            this._retryCount = 0;

            // Update progress display
            this._updateProgress(apiResponse.progress);

            // Handle different response types based on 'type' field
            if (apiResponse.type === 'result' && apiResponse.payload) {
                // Analysis completed successfully
                const result = apiResponse.payload as AnalysisResult;
                
                // Stop polling
                if (this._pollingInterval) {
                    clearInterval(this._pollingInterval);
                    this._pollingInterval = undefined;
                }

                // Send completion message with health score from payload.score.score
                this._view.webview.postMessage({
                    type: 'complete',
                    healthScore: result.score.score,
                    grade: result.score.grade,
                    summary: result.score.summary,
                    result: result
                });
            } else if (apiResponse.type === 'error' && apiResponse.payload) {
                // Analysis failed
                const error = apiResponse.payload as AnalysisError;
                
                // Stop polling
                if (this._pollingInterval) {
                    clearInterval(this._pollingInterval);
                    this._pollingInterval = undefined;
                }

                this._view.webview.postMessage({
                    type: 'error',
                    message: `${error.stage}: ${error.message} (${error.code})`
                });
            }
            // If type is 'request', continue polling (analysis still in progress)

        } catch (error) {
            // Retry logic: don't stop immediately, retry up to maxRetries times
            this._retryCount++;
            
            if (this._retryCount >= this._maxRetries) {
                // Stop polling after max retries
                if (this._pollingInterval) {
                    clearInterval(this._pollingInterval);
                    this._pollingInterval = undefined;
                }

                this._view.webview.postMessage({
                    type: 'error',
                    message: `Failed to check results after ${this._maxRetries} retries: ${error instanceof Error ? error.message : String(error)}`
                });
            }
            // Otherwise, continue polling and retry
        }
    }

    private _updateProgress(steps: ProgressStep[]) {
        if (!this._view) {
            return;
        }

        const progressLines: string[] = [];
        
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

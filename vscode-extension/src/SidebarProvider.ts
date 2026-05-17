import * as vscode from 'vscode';
import fetch from 'node-fetch';
import { getConfig } from './config';
import * as fs from 'fs';
import * as path from 'path';

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
                case 'retry':
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
                type: 'loading',
                step: 'Starting analysis...'
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

                this._view.webview.postMessage({
                    type: 'results',
                    data: result
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

        const activeStep = steps.find(s => s.status === 'active') || steps[steps.length - 1];
        const completed = steps.filter(s => s.status === 'done').length;
        const percentage = steps.length > 0 ? Math.round((completed / steps.length) * 100) : 0;
        const stepName = activeStep ? activeStep.name : 'Processing...';

        this._view.webview.postMessage({
            type: 'progress',
            data: {
                percentage: percentage,
                step: stepName
            }
        });
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        // Get paths to resources
        const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'main.html');
        const cssPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'styles.css');
        const jsPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'main.js');
        
        // Convert to webview URIs
        const cssUri = webview.asWebviewUri(cssPath);
        const jsUri = webview.asWebviewUri(jsPath);
        
        // Read HTML file
        let html = fs.readFileSync(htmlPath.fsPath, 'utf8');
        
        // Replace resource paths with webview URIs
        html = html.replace('href="styles.css"', `href="${cssUri}"`);
        html = html.replace('src="main.js"', `src="${jsUri}"`);

        return html;
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

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

    // Cache — keyed per workspace folder path
    private _cachedResult: AnalysisResult | null = null;
    private _cachedWorkspacePath: string | null = null;
    private _activeAnalysisPath: string | null = null;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _statusBarItem: vscode.StatusBarItem
    ) {}

    public triggerAnalysis(force: boolean = false) {
        this._analyzeWorkspace(force);
    }

    public openFullView() {
        this._openEditorPanel();
    }

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
                case 'ready': {
                    const status = await this._checkBackendConfig();
                    // If the backend is not configured or unavailable, show setup/dashboard
                    if (status !== 'configured') {
                        webviewView.webview.postMessage({ type: 'setup' });
                        return;
                    }
                    const currentPath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
                    if (currentPath && this._cachedWorkspacePath === currentPath && this._cachedResult) {
                        this._handleResult(this._cachedResult);
                    } else if (currentPath) {
                        await this._analyzeWorkspace(false);
                    } else {
                        webviewView.webview.postMessage({ type: 'idle' });
                    }
                    break;
                }
                case 'analyzeWorkspace':
                case 'retry':
                    await this._analyzeWorkspace(true);
                    break;
                case 'openFullView':
                    this._openEditorPanel();
                    break;
                case 'saveConfig': {
                    const msgData = data as { type: string; data: Record<string, string> };
                    try {
                        await this._saveConfig(msgData.data);
                        const status = await this._checkBackendConfig();
                        if (status === 'configured') {
                            const currentPath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
                            if (currentPath) {
                                await this._analyzeWorkspace(false);
                            } else {
                                webviewView.webview.postMessage({ type: 'idle' });
                            }
                        } else {
                            webviewView.webview.postMessage({ type: 'setup' });
                        }
                    } catch (error) {
                        webviewView.webview.postMessage({
                            type: 'error',
                            message: `Failed to save configuration: ${error instanceof Error ? error.message : String(error)}`
                        });
                    }
                    break;
                }
            }
        });
    }

    public revive(panel: vscode.WebviewView) {
        this._view = panel;
    }

    private _openEditorPanel() {
        if (!this._cachedResult) { return; }

        const panel = vscode.window.createWebviewPanel(
            'reposenseFullView',
            'RepoSense — Full Report',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [this._extensionUri],
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = this._getHtmlForWebview(panel.webview);

        const result = this._cachedResult;
        panel.webview.onDidReceiveMessage((data: { type: string }) => {
            if (data.type === 'ready') {
                panel.webview.postMessage({ type: 'results', data: result });
            }
        });
    }

    private async _checkBackendConfig(): Promise<'configured' | 'not_configured' | 'unavailable'> {
        try {
            const config = getConfig();
            const response = await fetch(`${config.backendUrl}/config/status`, {
                timeout: config.requestTimeoutMs
            });
            if (!response.ok) { return 'unavailable'; }
            const data = await response.json() as { configured: boolean };
            return data.configured ? 'configured' : 'not_configured';
        } catch {
            return 'unavailable';
        }
    }

    private async _saveConfig(configData: Record<string, string>) {
        const config = getConfig();
        const response = await fetch(`${config.backendUrl}/config/setup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(configData),
            timeout: config.requestTimeoutMs
        });
        if (!response.ok) {
            const text = await response.text();
            throw new Error(`HTTP ${response.status}: ${text}`);
        }
    }

    private async _analyzeWorkspace(force: boolean = false) {
        const analysisPath = await this._resolveAnalysisPath();
        if (!analysisPath) {
            this._statusBarItem.text = '$(error) RepoSense: Error';
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'error',
                    message: 'No valid folder selected for analysis'
                });
            }
            return;
        }

        // Clear cache when switching folders
        if (analysisPath !== this._cachedWorkspacePath) {
            this._cachedResult = null;
        }

        this._activeAnalysisPath = analysisPath;

        try {
            const config = getConfig();
            this._ensureBackendCanAccessPath(config.backendUrl, analysisPath);

            // Send initial status
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'loading',
                    step: 'Starting analysis...'
                });
            }
            // Update status bar to analyzing
            this._statusBarItem.text = '$(sync~spin) RepoSense: Analyzing...';

            // Send initial status to webview if available
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'status',
                    message: 'Starting analysis...'
                });
            }

            // Send POST request to start analysis
            const response = await fetch(`${config.backendUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ local_path: analysisPath }),
                timeout: config.requestTimeoutMs
            });

            if (!response.ok) {
                const errorText = await response.text();
                // Provide more actionable error for 404s (likely wrong backend URL or missing endpoint)
                if (response.status === 404) {
                    throw new Error(`HTTP 404: Endpoint not found. Check that the backend URL is correct and the server exposes /analyze.`);
                }
                if (response.status === 400 && errorText.includes('Path does not exist')) {
                    throw new Error(`HTTP 400: Selected analysis path does not exist on this machine (${analysisPath}). Please choose an existing folder and retry.`);
                }
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const data = await response.json() as ApiResponse;
            const jobId = data.job_id;

            // Send initial progress update
            this._updateProgress(data.progress);

            // Start polling for results
            this._startPolling(jobId);

        } catch (error) {
            this._statusBarItem.text = '$(error) RepoSense: Error';
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'error',
                    message: `Failed to start analysis: ${error instanceof Error ? error.message : String(error)}`
                });
            }
        }
    }

    private async _resolveAnalysisPath(): Promise<string | null> {
        const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (workspacePath && this._isExistingDirectory(workspacePath)) {
            return workspacePath;
        }

        const activeEditorPath = vscode.window.activeTextEditor?.document.uri.fsPath;
        if (activeEditorPath) {
            const fallbackFolder = this._isExistingDirectory(activeEditorPath)
                ? activeEditorPath
                : path.dirname(activeEditorPath);
            if (this._isExistingDirectory(fallbackFolder)) {
                return fallbackFolder;
            }
        }

        const picked = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            openLabel: 'Select Folder to Analyze'
        });

        return picked?.[0]?.fsPath ?? null;
    }

    private _isExistingDirectory(targetPath: string): boolean {
        try {
            return fs.existsSync(targetPath) && fs.statSync(targetPath).isDirectory();
        } catch {
            return false;
        }
    }

    private _ensureBackendCanAccessPath(backendUrl: string, analysisPath: string): void {
        const host = this._getBackendHost(backendUrl);
        if (!host) {
            return;
        }

        const isLocalBackend = host === 'localhost' || host === '127.0.0.1' || host === '::1';
        if (isLocalBackend) {
            return;
        }

        const isLikelyLocalFilesystemPath = path.isAbsolute(analysisPath);
        if (isLikelyLocalFilesystemPath) {
            throw new Error(
                `Backend URL ${backendUrl} is remote and cannot access local path ${analysisPath}. ` +
                'Set reposense.backendUrl to http://localhost:8000 (or run the backend where this path exists).'
            );
        }
    }

    private _getBackendHost(backendUrl: string): string | null {
        try {
            return new URL(backendUrl).hostname.toLowerCase();
        } catch {
            return null;
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
            const apiResponse = await this._fetchJobResult(jobId);

            // Reset retry count on successful response
            this._retryCount = 0;

            // Update progress display
            this._updateProgress(apiResponse.progress);

            this._processApiResponse(apiResponse);
        } catch (error) {
            this._handleCheckResultsError(error);
        }
    }

    private async _fetchJobResult(jobId: string): Promise<ApiResponse> {
        const config = getConfig();
        const response = await fetch(`${config.backendUrl}/jobs/${jobId}`, {
            timeout: config.requestTimeoutMs
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json() as ApiResponse;
    }

    private _processApiResponse(apiResponse: ApiResponse) {
        if (apiResponse.type === 'result' && apiResponse.payload) {
            this._handleResult(apiResponse.payload as AnalysisResult);
            return;
        }

        if (apiResponse.type === 'error' && apiResponse.payload) 
            this._handleAnalysisError(apiResponse.payload as AnalysisError);
    }

    private _handleCheckResultsError(error: unknown) {
        // Retry logic: don't stop immediately, retry up to maxRetries times
        this._retryCount++;

        if (this._retryCount < this._maxRetries) {
            return;
        }

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

    private _handleResult(result: AnalysisResult) {
        // Stop polling
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
            this._pollingInterval = undefined;
        }

        // Store in cache
        this._cachedResult = result;
        this._cachedWorkspacePath = this._activeAnalysisPath;

        this._view!.webview.postMessage({ type: 'results', data: result });
        this._statusBarItem.text = `$(graph) RepoSense: Score ${result.score.score}/100`;

        vscode.window.showInformationMessage(
            `RepoSense: Analysis complete — Score ${result.score.score}/100`,
            'View Details'
        ).then((selection: string | undefined) => {
            if (selection === 'View Details') {
                vscode.commands.executeCommand('reposense-sidebar.focus');
            }
        });

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

    private _handleAnalysisError(error: AnalysisError) {
        // Stop polling
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
            this._pollingInterval = undefined;
        }

        this._statusBarItem.text = '$(error) RepoSense: Error';

        if (this._view) {
            this._view.webview.postMessage({
                type: 'error',
                message: `${error.stage}: ${error.message} (${error.code})`
            });
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

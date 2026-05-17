import * as vscode from 'vscode';
import fetch from 'node-fetch';
import { getConfig } from './config';
import * as fs from 'fs';
import * as path from 'path';

// USE_MOCK flag - set to true to use mock data instead of real API
const USE_MOCK = true;

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

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _statusBarItem: vscode.StatusBarItem
    ) {}

    /**
     * Public method to trigger analysis (called from extension.ts)
     */
    public triggerAnalysis() {
        this._analyzeWorkspace();
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
                case 'analyzeWorkspace':
                case 'retry':
                    await this._analyzeWorkspace();
                    break;
            }
        });

        // Auto-start analysis when USE_MOCK is true
        if (USE_MOCK) {
            setTimeout(() => {
                this._analyzeWorkspace();
            }, 100);
        }
    }

    public revive(panel: vscode.WebviewView) {
        this._view = panel;
    }
    private _generateMockData(): AnalysisResult {
        return {
            score: {
                score: 74,
                grade: 'B',
                breakdown: {
                    quality: 72,
                    security: 68,
                    documentation: 75,
                    architecture: 81
                },
                summary: 'Codebase is moderately healthy with some areas for improvement',
                top_priorities: [
                    'Add input validation',
                    'Document 12 functions',
                    'Update Werkzeug imports'
                ]
            },
            architecture: {
                nodes: [
                    { id: 'main.py', label: 'main.py', type: 'entry', description: 'Main application entry point' },
                    { id: 'config.py', label: 'config.py', type: 'config', description: 'Configuration module' },
                    { id: 'parser.py', label: 'parser.py', type: 'service', description: 'Code parser service' },
                    { id: 'orchestrate.py', label: 'orchestrate.py', type: 'service', description: 'Agent orchestration' },
                    { id: 'watsonx.py', label: 'watsonx.py', type: 'service', description: 'WatsonX integration' },
                    { id: 'utils/logger.py', label: 'logger.py', type: 'util', description: 'Logging utilities' }
                ],
                edges: [
                    { source: 'main.py', target: 'config.py', relationship: 'imports' },
                    { source: 'main.py', target: 'orchestrate.py', relationship: 'calls' },
                    { source: 'orchestrate.py', target: 'parser.py', relationship: 'calls' },
                    { source: 'orchestrate.py', target: 'watsonx.py', relationship: 'calls' },
                    { source: 'parser.py', target: 'utils/logger.py', relationship: 'imports' }
                ]
            },
            review: {
                findings: [
                    {
                        file: 'src/main.py',
                        line: 45,
                        severity: 'HIGH',
                        issue: 'Missing input validation for user-provided path',
                        suggestion: 'Add path validation to prevent directory traversal attacks'
                    },
                    {
                        file: 'src/parser.py',
                        line: 123,
                        severity: 'MEDIUM',
                        issue: 'Exception handling too broad',
                        suggestion: 'Catch specific exceptions instead of bare except'
                    },
                    {
                        file: 'src/watsonx.py',
                        line: 67,
                        severity: 'LOW',
                        issue: 'Magic number used without explanation',
                        suggestion: 'Extract magic number to named constant'
                    }
                ]
            },
            docs: {
                docs: [
                    {
                        function_name: 'parse_file',
                        description: 'Parses a Python file and extracts its AST structure',
                        params: [
                            { name: 'file_path', type: 'str', description: 'Path to the file to parse' },
                            { name: 'encoding', type: 'str', description: 'File encoding (default: utf-8)' }
                        ],
                        returns: 'Dict containing parsed AST nodes and metadata',
                        example: 'result = parse_file("main.py", encoding="utf-8")'
                    },
                    {
                        function_name: 'analyze_dependencies',
                        description: 'Analyzes import dependencies in the codebase',
                        params: [
                            { name: 'root_path', type: 'str', description: 'Root directory to analyze' }
                        ],
                        returns: 'Graph of dependencies between modules',
                        example: 'deps = analyze_dependencies("/path/to/project")'
                    }
                ],
                tests: [
                    {
                        function_name: 'parse_file',
                        test_cases: [
                            {
                                description: 'Should parse valid Python file',
                                input: 'valid_file.py',
                                expected: 'AST with function definitions'
                            },
                            {
                                description: 'Should handle syntax errors gracefully',
                                input: 'invalid_syntax.py',
                                expected: 'Error with line number'
                            }
                        ]
                    }
                ]
            },
            security: {
                security: [
                    {
                        issue: 'Deprecated Werkzeug imports detected',
                        severity: 'MEDIUM',
                        file: 'src/main.py',
                        fix: 'Update to use werkzeug.security instead of werkzeug.contrib'
                    },
                    {
                        issue: 'Hardcoded credentials in configuration',
                        severity: 'CRITICAL',
                        file: 'src/config.py',
                        fix: 'Move credentials to environment variables'
                    }
                ],
                modernization: [
                    {
                        pattern: 'Using % string formatting',
                        suggestion: 'Migrate to f-strings for better readability',
                        effort: 'LOW'
                    },
                    {
                        pattern: 'Type hints missing on 15 functions',
                        suggestion: 'Add type hints for better IDE support',
                        effort: 'MEDIUM'
                    }
                ]
            }
        };
    }

    private async _simulateMockProgress() {
        const steps = [
            'Reading workspace files',
            'Parsing code structure',
            'Architect agent running',
            'Architect agent complete',
            'Reviewer agent complete',
            'Documenter agent complete',
            'Hardener agent complete'
        ];

        for (let i = 0; i < steps.length; i++) {
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'loading',
                    step: steps[i]
                });

                this._view.webview.postMessage({
                    type: 'progress',
                    data: {
                        percentage: ((i + 1) / steps.length) * 100,
                        step: steps[i]
                    }
                });
            }

            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        const mockData = this._generateMockData();
        if (this._view) {
            this._view.webview.postMessage({
                type: 'results',
                data: {
                    health: {
                        score: mockData.score.score,
                        grade: mockData.score.grade,
                        summary: mockData.score.summary,
                        priorities: mockData.score.top_priorities
                    },
                    architecture: mockData.architecture,
                    review: mockData.review,
                    documentation: mockData.docs,
                    security: {
                        issues: mockData.security.security,
                        modernization: mockData.security.modernization
                    }
                }
            });
        }

        this._statusBarItem.text = `$(graph) RepoSense: Score ${mockData.score.score}/100`;
    }


    private async _analyzeWorkspace() {
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

        // Check if USE_MOCK is enabled
        if (USE_MOCK) {
            this._statusBarItem.text = '$(sync~spin) RepoSense: Analyzing...';
            await this._simulateMockProgress();
            return;
        }

        try {
            // Update status bar to analyzing
            this._statusBarItem.text = '$(sync~spin) RepoSense: Analyzing...';

            // Send initial status to webview if available
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'loading',
                    step: 'Starting analysis...'
                });
            }

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
            this._statusBarItem.text = '$(error) RepoSense: Error';
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'error',
                    message: `Failed to start analysis: ${error instanceof Error ? error.message : String(error)}`
                });
            }
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

                // Update status bar with score
                this._statusBarItem.text = `$(graph) RepoSense: Score ${result.score.score}/100`;

                // Show completion notification
                vscode.window.showInformationMessage(
                    `RepoSense: Analysis complete — Score ${result.score.score}/100`,
                    'View Details'
                ).then(selection => {
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
            } else if (apiResponse.type === 'error' && apiResponse.payload) {
                // Analysis failed
                const error = apiResponse.payload as AnalysisError;
                
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

        } catch (error) {
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

    private _updateProgress(steps: ProgressStep[]) {
        if (!this._view) {
            return;
        }

        // Send progress data to webview
        if (this._view) {
            this._view.webview.postMessage({
                type: 'progress',
                data: steps
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        // Read the webview HTML file
        const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'main.html');
        const cssPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'styles.css');
        const jsPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'main.js');

        // Convert to webview URIs
        const cssUri = webview.asWebviewUri(cssPath);
        const jsUri = webview.asWebviewUri(jsPath);

        let html = fs.readFileSync(htmlPath.fsPath, 'utf8');

        // Replace relative paths with webview URIs
        html = html.replace('href="styles.css"', `href="${cssUri}"`);
        html = html.replace('src="main.js"', `src="${jsUri}"`);

        // Update CSP to allow the webview resources
        const nonce = this._getNonce();
        html = html.replace(
            /<meta http-equiv="Content-Security-Policy"[^>]*>/,
            `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'nonce-${nonce}' https://cdn.jsdelivr.net; img-src ${webview.cspSource} https: data:; connect-src https:;">`
        );

        // Add nonce to script tags
        html = html.replace(/<script/g, `<script nonce="${nonce}"`);

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

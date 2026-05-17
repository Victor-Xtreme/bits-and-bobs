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
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const cp = __importStar(require("child_process"));
class SidebarProvider {
    constructor(_extensionUri, _statusBarItem) {
        this._extensionUri = _extensionUri;
        this._statusBarItem = _statusBarItem;
        this._retryCount = 0;
        this._maxRetries = 3;
        // Cache — keyed per workspace folder path
        this._cachedResult = null;
        this._cachedWorkspacePath = null;
        this._activeAnalysisPath = null;
    }
    triggerAnalysis(force = false) {
        this._analyzeWorkspace(force);
    }
    openFullView() {
        this._openEditorPanel();
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
                case 'ready': {
                    const currentPath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
                    if (currentPath && this._cachedWorkspacePath === currentPath && this._cachedResult) {
                        this._handleResult(this._cachedResult);
                    }
                    else if (currentPath) {
                        await this._analyzeWorkspace(false);
                    }
                    else {
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
            }
        });
    }
    revive(panel) {
        this._view = panel;
    }
    _openEditorPanel() {
        if (!this._cachedResult) {
            return;
        }
        const panel = vscode.window.createWebviewPanel('reposenseFullView', 'RepoSense — Full Report', vscode.ViewColumn.One, {
            enableScripts: true,
            localResourceRoots: [this._extensionUri],
            retainContextWhenHidden: true
        });
        panel.webview.html = this._getHtmlForWebview(panel.webview);
        const result = this._cachedResult;
        panel.webview.onDidReceiveMessage((data) => {
            if (data.type === 'ready') {
                panel.webview.postMessage({ type: 'results', data: result });
            }
        });
    }
    async _analyzeWorkspace(force = false) {
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
            const config = (0, config_1.getConfig)();
            const analyzeRequestBody = await this._buildAnalyzeRequestBody(config.backendUrl, config.remoteRepoUrl, analysisPath);
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
            const response = await (0, node_fetch_1.default)(`${config.backendUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(analyzeRequestBody),
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
    async _resolveAnalysisPath() {
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
    _isExistingDirectory(targetPath) {
        try {
            return fs.existsSync(targetPath) && fs.statSync(targetPath).isDirectory();
        }
        catch {
            return false;
        }
    }
    async _buildAnalyzeRequestBody(backendUrl, configuredRemoteRepoUrl, analysisPath) {
        if (this._isLocalBackend(backendUrl)) {
            return { local_path: analysisPath };
        }
        const explicitRepoUrl = configuredRemoteRepoUrl.trim();
        if (explicitRepoUrl) {
            return { repo_url: explicitRepoUrl };
        }
        const detectedRepoUrl = this._tryGetWorkspaceGitRemote(analysisPath);
        if (detectedRepoUrl) {
            return { repo_url: detectedRepoUrl };
        }
        throw new Error(`Backend URL ${backendUrl} is remote. Set reposense.remoteRepoUrl to your Git repository URL ` +
            '(for example, https://github.com/org/repo.git) so Render can clone and analyze it.');
    }
    _tryGetWorkspaceGitRemote(analysisPath) {
        try {
            const output = cp.execFileSync('git', ['-C', analysisPath, 'remote', 'get-url', 'origin'], {
                encoding: 'utf8',
                timeout: 5000,
                stdio: ['ignore', 'pipe', 'ignore']
            }).trim();
            if (!output) {
                return null;
            }
            return this._normalizeGitRemoteUrl(output);
        }
        catch {
            return null;
        }
    }
    _normalizeGitRemoteUrl(remoteUrl) {
        const trimmed = remoteUrl.trim();
        const sshMatch = /^git@([^:]+):(.+)$/.exec(trimmed);
        if (sshMatch) {
            const host = sshMatch[1];
            const repoPath = sshMatch[2];
            return `https://${host}/${repoPath}`;
        }
        return trimmed;
    }
    _isLocalBackend(backendUrl) {
        const host = this._getBackendHost(backendUrl);
        return !!host && (host === 'localhost' || host === '127.0.0.1' || host === '::1');
    }
    _getBackendHost(backendUrl) {
        try {
            return new URL(backendUrl).hostname.toLowerCase();
        }
        catch {
            return null;
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
            const apiResponse = await this._fetchJobResult(jobId);
            // Reset retry count on successful response
            this._retryCount = 0;
            // Update progress display
            this._updateProgress(apiResponse.progress);
            this._processApiResponse(apiResponse);
        }
        catch (error) {
            this._handleCheckResultsError(error);
        }
    }
    async _fetchJobResult(jobId) {
        const config = (0, config_1.getConfig)();
        const response = await (0, node_fetch_1.default)(`${config.backendUrl}/jobs/${jobId}`, {
            timeout: config.requestTimeoutMs
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
    _processApiResponse(apiResponse) {
        if (apiResponse.type === 'result' && apiResponse.payload) {
            this._handleResult(apiResponse.payload);
            return;
        }
        if (apiResponse.type === 'error' && apiResponse.payload)
            this._handleAnalysisError(apiResponse.payload);
    }
    _handleCheckResultsError(error) {
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
    _handleResult(result) {
        // Stop polling
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
            this._pollingInterval = undefined;
        }
        // Store in cache
        this._cachedResult = result;
        this._cachedWorkspacePath = this._activeAnalysisPath;
        this._view.webview.postMessage({ type: 'results', data: result });
        this._statusBarItem.text = `$(graph) RepoSense: Score ${result.score.score}/100`;
        vscode.window.showInformationMessage(`RepoSense: Analysis complete — Score ${result.score.score}/100`, 'View Details').then((selection) => {
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
    _handleAnalysisError(error) {
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
    _updateProgress(steps) {
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
    _getHtmlForWebview(webview) {
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
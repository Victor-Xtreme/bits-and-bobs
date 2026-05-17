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
class SidebarProvider {
    constructor(_extensionUri, _statusBarItem) {
        this._extensionUri = _extensionUri;
        this._statusBarItem = _statusBarItem;
        this._retryCount = 0;
        this._maxRetries = 3;
        // Cache — keyed per workspace folder path
        this._cachedResult = null;
        this._cachedWorkspacePath = null;
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
                    const status = await this._checkBackendConfig();
                    if (status === 'not_configured') {
                        webviewView.webview.postMessage({ type: 'setup' });
                        return;
                    }
                    if (status === 'unavailable') {
                        webviewView.webview.postMessage({
                            type: 'error',
                            message: 'Cannot reach the RepoSense backend. Make sure it is running.'
                        });
                        return;
                    }
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
                case 'retry': {
                    const status = await this._checkBackendConfig();
                    if (status === 'not_configured') {
                        webviewView.webview.postMessage({ type: 'setup' });
                        return;
                    }
                    if (status === 'unavailable') {
                        webviewView.webview.postMessage({
                            type: 'error',
                            message: 'Cannot reach the RepoSense backend. Make sure it is running.'
                        });
                        return;
                    }
                    await this._analyzeWorkspace(true);
                    break;
                }
                case 'openFullView':
                    this._openEditorPanel();
                    break;
                case 'saveConfig': {
                    const msgData = data;
                    try {
                        await this._saveConfig(msgData.data);
                        // After saving, do a real IAM validation to catch bad keys
                        // before we attempt an analysis.
                        const valid = await this._validateCredentials();
                        if (!valid) {
                            webviewView.webview.postMessage({
                                type: 'error',
                                message: 'Credentials saved but API key validation failed. Please check your Orchestrate API key.'
                            });
                            return;
                        }
                        const status = await this._checkBackendConfig();
                        if (status === 'configured') {
                            const currentPath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
                            if (currentPath) {
                                await this._analyzeWorkspace(false);
                            }
                            else {
                                webviewView.webview.postMessage({ type: 'idle' });
                            }
                        }
                        else {
                            webviewView.webview.postMessage({ type: 'setup' });
                        }
                    }
                    catch (error) {
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
    async _checkBackendConfig() {
        try {
            const config = (0, config_1.getConfig)();
            const response = await (0, node_fetch_1.default)(`${config.backendUrl}/config/status`, {
                timeout: config.requestTimeoutMs
            });
            if (!response.ok) {
                return 'unavailable';
            }
            const data = await response.json();
            return data.configured ? 'configured' : 'not_configured';
        }
        catch {
            return 'unavailable';
        }
    }
    async _validateCredentials() {
        try {
            const config = (0, config_1.getConfig)();
            const response = await (0, node_fetch_1.default)(`${config.backendUrl}/config/validate`, {
                timeout: config.requestTimeoutMs
            });
            if (!response.ok) {
                return false;
            }
            const data = await response.json();
            return data.valid === true;
        }
        catch {
            return false;
        }
    }
    async _saveConfig(configData) {
        const config = (0, config_1.getConfig)();
        const response = await (0, node_fetch_1.default)(`${config.backendUrl}/config/setup`, {
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
    async _analyzeWorkspace(force = false) {
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
        // Clear cache when switching folders
        if (workspacePath !== this._cachedWorkspacePath) {
            this._cachedResult = null;
        }
        try {
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
        this._cachedWorkspacePath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? null;
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
        // IAM token failures mean the stored credentials are invalid — send
        // the user back to the setup screen instead of showing a raw error.
        const isAuthFailure = error.message.includes('IAM token') ||
            error.message.includes('apikey') ||
            error.message.includes('Authentication failed') ||
            error.message.includes('BXNIM');
        if (isAuthFailure && this._view) {
            this._view.webview.postMessage({ type: 'setup' });
            return;
        }
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
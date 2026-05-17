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
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const SidebarProvider_1 = require("./SidebarProvider");
function activate(context) {
    console.log('RepoSense extension is now active');
    // Create status bar item (left side, priority 100)
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.command = 'reposense.focusSidebar';
    statusBarItem.text = '$(check) RepoSense: Ready';
    statusBarItem.show();
    // Register the sidebar provider with status bar item
    const sidebarProvider = new SidebarProvider_1.SidebarProvider(context.extensionUri, statusBarItem);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider('reposense-sidebar', sidebarProvider), 
    // Register the provider itself so dispose() gets called on deactivation
    sidebarProvider, statusBarItem);
    // Register command to focus sidebar
    context.subscriptions.push(vscode.commands.registerCommand('reposense.focusSidebar', () => {
        vscode.commands.executeCommand('reposense-sidebar.focus');
    }));
    // Register refresh command
    context.subscriptions.push(vscode.commands.registerCommand('reposense.refresh', () => {
        sidebarProvider.triggerAnalysis(true);
    }));
    // Open full report in editor tab
    context.subscriptions.push(vscode.commands.registerCommand('reposense.openInBrowser', () => {
        sidebarProvider.openFullView();
    }));
    // Listen to workspace folder changes — always force fresh analysis
    context.subscriptions.push(vscode.workspace.onDidChangeWorkspaceFolders(() => {
        sidebarProvider.triggerAnalysis(true);
    }));
}
exports.activate = activate;
function deactivate() {
    console.log('RepoSense extension is now deactivated');
}
exports.deactivate = deactivate;
// Made with Bob
//# sourceMappingURL=extension.js.map
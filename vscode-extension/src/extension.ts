import * as vscode from 'vscode';
import { SidebarProvider } from './SidebarProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('RepoSense extension is now active');

    // Create status bar item (left side, priority 100)
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );
    statusBarItem.command = 'reposense.focusSidebar';
    statusBarItem.text = '$(check) RepoSense: Ready';
    statusBarItem.show();

    // Register the sidebar provider with status bar item
    const sidebarProvider = new SidebarProvider(context.extensionUri, statusBarItem);
    
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            'reposense-sidebar',
            sidebarProvider
        ),
        // Register the provider itself so dispose() gets called on deactivation
        sidebarProvider,
        statusBarItem
    );

    // Register command to focus sidebar
    context.subscriptions.push(
        vscode.commands.registerCommand('reposense.focusSidebar', () => {
            vscode.commands.executeCommand('reposense-sidebar.focus');
        })
    );

    // Register refresh command
    context.subscriptions.push(
        vscode.commands.registerCommand('reposense.refresh', () => {
            sidebarProvider.triggerAnalysis(true);
        })
    );

    // Open full report in editor tab
    context.subscriptions.push(
        vscode.commands.registerCommand('reposense.openInBrowser', () => {
            sidebarProvider.openFullView();
        })
    );

    // Listen to workspace folder changes — always force fresh analysis
    context.subscriptions.push(
        vscode.workspace.onDidChangeWorkspaceFolders(() => {
            sidebarProvider.triggerAnalysis(true);
        })
    );
}

export function deactivate() {
    console.log('RepoSense extension is now deactivated');
}

// Made with Bob

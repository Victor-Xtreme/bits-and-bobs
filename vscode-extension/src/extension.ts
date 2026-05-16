import * as vscode from 'vscode';
import { SidebarProvider } from './SidebarProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('RepoSense extension is now active');

    // Register the sidebar provider
    const sidebarProvider = new SidebarProvider(context.extensionUri);
    
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            'reposense-sidebar',
            sidebarProvider
        )
    );
}

export function deactivate() {
    console.log('RepoSense extension is now deactivated');
}

// Made with Bob

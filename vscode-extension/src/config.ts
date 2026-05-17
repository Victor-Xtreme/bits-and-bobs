import * as vscode from 'vscode';

interface RepoSenseConfig {
    backendUrl: string;
    remoteRepoUrl: string;
    requestTimeoutMs: number;
    pollingIntervalMs: number;
}

export function getConfig(): RepoSenseConfig {
    const config = vscode.workspace.getConfiguration('reposense');
    return {
        backendUrl: config.get<string>('backendUrl', 'http://localhost:8000'),
        remoteRepoUrl: config.get<string>('remoteRepoUrl', ''),
        requestTimeoutMs: config.get<number>('requestTimeoutMs', 30000),
        pollingIntervalMs: config.get<number>('pollingIntervalMs', 2000),
    };
}

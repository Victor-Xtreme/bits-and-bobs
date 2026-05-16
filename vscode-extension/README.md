# RepoSense

A VS Code extension that analyzes your workspace repository and provides health scores through integration with a backend analysis service.

## Features

- **Webview Sidebar**: Access RepoSense functionality through a dedicated sidebar panel
- **Workspace Analysis**: Analyze your current workspace with a single click
- **Real-time Progress**: See live updates as the analysis progresses
- **Health Score**: Get a comprehensive health score for your repository
- **Backend Integration**: Communicates with a local analysis service at `http://localhost:8000`

## Requirements

- VS Code version 1.74.0 or higher
- RepoSense backend service running on `http://localhost:8000`

## Installation

### From Source

1. Clone this repository
2. Navigate to the extension directory:
   ```bash
   cd vscode-extension
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Compile the extension:
   ```bash
   npm run compile
   ```
5. Press `F5` to open a new VS Code window with the extension loaded

### From VSIX Package

1. Download the `.vsix` file
2. Open VS Code
3. Go to Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X`)
4. Click the `...` menu at the top of the Extensions view
5. Select "Install from VSIX..."
6. Choose the downloaded `.vsix` file

## Usage

1. **Start the Backend Service**: Ensure the RepoSense backend is running on `http://localhost:8000`

2. **Open the Sidebar**: Click the RepoSense icon in the Activity Bar (left sidebar)

3. **Analyze Workspace**: 
   - Click the "Analyze Workspace" button
   - The extension will send your workspace path to the backend
   - Watch real-time progress updates as the analysis runs
   - View the final health score when complete

## How It Works

1. When you click "Analyze Workspace", the extension:
   - Reads your current workspace folder path
   - Sends a POST request to `http://localhost:8000/analyze` with the path
   - Receives a `job_id` in response

2. The extension then polls `http://localhost:8000/results/{job_id}` every 3 seconds to:
   - Check the analysis status
   - Display progress updates (e.g., "✓ Architect complete...")
   - Show the final health score when analysis is complete

## API Endpoints

The extension expects the following backend endpoints:

### POST /analyze
Request:
```json
{
  "local_path": "/path/to/workspace"
}
```

Response:
```json
{
  "job_id": "unique-job-id"
}
```

### GET /results/{job_id}
Response (in progress):
```json
{
  "job_id": "unique-job-id",
  "status": "in_progress",
  "progress": {
    "architect": true
  }
}
```

Response (complete):
```json
{
  "job_id": "unique-job-id",
  "status": "completed",
  "health_score": 85
}
```

## Development

### Building

```bash
npm run compile
```

### Watching for Changes

```bash
npm run watch
```

### Debugging

1. Open the extension folder in VS Code
2. Press `F5` to start debugging
3. A new Extension Development Host window will open with the extension loaded

## Extension Settings

This extension contributes the following:

- `reposense-sidebar`: Webview sidebar panel for RepoSense analysis

## Known Issues

- Backend service must be running on `http://localhost:8000` before using the extension
- No configuration options for custom backend URLs (coming in future versions)

## Release Notes

### 0.0.1

Initial release of RepoSense extension:
- Workspace analysis with backend integration
- Real-time progress updates
- Health score display
- Polling-based status checking

## License

See LICENSE file for details.
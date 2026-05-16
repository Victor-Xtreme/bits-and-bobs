# RepoSense VSCode Extension Setup Guide

This guide explains how to set up and connect the RepoSense VSCode extension to the backend API.

## Prerequisites

1. **Backend Running**: The RepoSense backend must be running on `http://localhost:8000` (default)
2. **Node.js**: Version 16.x or higher
3. **VSCode**: Version 1.74.0 or higher

## Backend Setup

### 1. Configure Backend Environment

Navigate to the backend directory and create a `.env` file:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your WatsonX credentials:

```env
WATSONX_API_KEY=your-actual-api-key
WATSONX_PROJECT_ID=your-actual-project-id
```

### 2. Update CORS Settings (Important!)

The backend needs to allow requests from the VSCode extension. Update the `CORS_ORIGINS` in your `.env` file:

```env
# Add vscode-webview:// protocol for VSCode extension
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,vscode-webview://,http://localhost:*
```

Or modify `backend/src/config.py` to allow all origins during development:

```python
cors_origins: str = "*"  # Allow all origins (development only!)
```

### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Start the Backend

```bash
cd backend
python -m src.main
```

Or using uvicorn directly:

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Verify the backend is running by visiting: http://localhost:8000

You should see:
```json
{
  "service": "RepoSense API",
  "status": "running",
  "version": "1.0.0"
}
```

## Extension Setup

### 1. Install Extension Dependencies

```bash
cd vscode-extension
npm install
```

### 2. Configure Backend URL (Optional)

If your backend runs on a different port, edit `vscode-extension/src/config.ts`:

```typescript
export const defaultConfig: ExtensionConfig = {
    backendUrl: 'http://localhost:8000',  // Change this if needed
    pollingIntervalMs: 3000,
    requestTimeoutMs: 30000
};
```

### 3. Compile the Extension

```bash
cd vscode-extension
npm run compile
```

### 4. Run the Extension

1. Open the `vscode-extension` folder in VSCode
2. Press `F5` to start debugging
3. A new VSCode window will open with the extension loaded

## Using the Extension

### 1. Open the RepoSense Sidebar

- Click the RepoSense icon in the Activity Bar (left sidebar)
- Or use Command Palette: `View: Show RepoSense`

### 2. Analyze Your Workspace

1. Open a workspace/folder in VSCode
2. Click the "Analyze Workspace" button in the RepoSense sidebar
3. Watch the progress as the analysis runs
4. View the results when complete

### 3. Understanding the Results

The extension displays:
- **Health Score**: Overall score (0-100) with letter grade (A-F)
- **Breakdown**: Scores for Quality, Security, Documentation, and Architecture
- **Top Priorities**: Key areas to focus on for improvement
- **Summary**: AI-generated summary of the codebase health
- **Analysis Details**: Counts of findings, issues, and recommendations

## API Endpoints Used

The extension communicates with these backend endpoints:

### POST /analyze
Start a new analysis job.

**Request:**
```json
{
  "local_path": "/path/to/workspace"
}
```

**Response:**
```json
{
  "type": "request",
  "job_id": "uuid-string",
  "progress": [
    {
      "name": "Parsing codebase",
      "status": "active",
      "files_processed": 10,
      "files_total": 50
    }
  ],
  "payload": null
}
```

### GET /jobs/{job_id}
Poll for job status and results.

**Response Types:**

1. **In Progress** (`type: "request"`):
```json
{
  "type": "request",
  "job_id": "uuid",
  "progress": [...],
  "payload": null
}
```

2. **Completed** (`type: "result"`):
```json
{
  "type": "result",
  "job_id": "uuid",
  "progress": [...],
  "payload": {
    "score": {
      "score": 85,
      "grade": "B",
      "breakdown": {...},
      "summary": "...",
      "top_priorities": [...]
    },
    "architecture": {...},
    "review": {...},
    "docs": {...},
    "security": {...}
  }
}
```

3. **Failed** (`type: "error"`):
```json
{
  "type": "error",
  "job_id": "uuid",
  "progress": [...],
  "payload": {
    "code": "PARSE_FAILED",
    "message": "Error details",
    "stage": "Parsing codebase"
  }
}
```

## Troubleshooting

### Extension Can't Connect to Backend

**Error:** "Failed to start analysis: Failed to fetch"

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000`
2. Check CORS configuration in backend `.env`
3. Check browser console in VSCode DevTools: `Help > Toggle Developer Tools`

### CORS Errors

**Error:** "Access to fetch at 'http://localhost:8000/analyze' from origin 'vscode-webview://...' has been blocked by CORS policy"

**Solution:**
Update backend CORS settings to allow VSCode webview origins:
```env
CORS_ORIGINS=*
```

Or specifically:
```env
CORS_ORIGINS=vscode-webview://,http://localhost:*
```

### Backend Not Starting

**Error:** "ValidationError: watsonx_api_key"

**Solution:**
Ensure your `.env` file has valid WatsonX credentials:
```env
WATSONX_API_KEY=your-actual-key-here
WATSONX_PROJECT_ID=your-actual-project-id
```

### Analysis Fails Immediately

**Error:** "Path does not exist" or "Path is not a directory"

**Solution:**
The extension sends the workspace folder path. Ensure:
1. You have a folder open in VSCode (not just files)
2. The backend has permission to read the directory
3. The path is valid on your system

### Polling Doesn't Stop

**Issue:** Extension keeps polling even after completion

**Solution:**
This is a bug. Reload the VSCode window: `Developer: Reload Window`

## Development Tips

### Debugging the Extension

1. Open `vscode-extension` in VSCode
2. Set breakpoints in TypeScript files
3. Press `F5` to start debugging
4. Use Debug Console to inspect variables

### Viewing Network Requests

1. In the Extension Development Host window
2. Open DevTools: `Help > Toggle Developer Tools`
3. Go to Network tab
4. Filter by "localhost:8000"

### Modifying the UI

Edit the HTML in `SidebarProvider.ts` method `_getHtmlForWebview()`:
- Styles are inline using VSCode CSS variables
- JavaScript uses the VSCode API via `acquireVsCodeApi()`

### Testing Backend Endpoints

Use curl or Postman:

```bash
# Start analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"local_path": "/path/to/project"}'

# Check status
curl http://localhost:8000/jobs/{job_id}
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         VSCode Extension                │
│  ┌───────────────────────────────────┐  │
│  │     SidebarProvider.ts            │  │
│  │  - Manages webview UI             │  │
│  │  - Handles user interactions      │  │
│  │  - Polls backend for updates      │  │
│  └───────────────┬───────────────────┘  │
│                  │                       │
│                  │ HTTP Requests         │
│                  ▼                       │
└──────────────────┼───────────────────────┘
                   │
                   │ POST /analyze
                   │ GET /jobs/{id}
                   │
┌──────────────────▼───────────────────────┐
│         FastAPI Backend                  │
│  ┌───────────────────────────────────┐  │
│  │         main.py                   │  │
│  │  - API endpoints                  │  │
│  │  - Job management                 │  │
│  │  - CORS handling                  │  │
│  └───────────────┬───────────────────┘  │
│                  │                       │
│                  ▼                       │
│  ┌───────────────────────────────────┐  │
│  │      orchestrate.py               │  │
│  │  - Coordinates analysis pipeline  │  │
│  │  - Updates progress               │  │
│  └───────────────┬───────────────────┘  │
│                  │                       │
│                  ▼                       │
│  ┌───────────────────────────────────┐  │
│  │      WatsonX AI Agent             │  │
│  │  - Analyzes code                  │  │
│  │  - Generates insights             │  │
│  └───────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Next Steps

1. **Enhance UI**: Add tabs for different analysis sections
2. **Add Commands**: Register VSCode commands for quick actions
3. **Settings**: Add VSCode settings for backend URL configuration
4. **Notifications**: Show VSCode notifications for analysis completion
5. **Results View**: Create dedicated views for detailed results

## Support

For issues or questions:
1. Check the backend logs
2. Check VSCode DevTools console
3. Review this setup guide
4. Check the main README.md

---

Made with Bob
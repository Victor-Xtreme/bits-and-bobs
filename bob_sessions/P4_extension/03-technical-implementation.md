# RepoSense Extension - Technical Implementation

**Session Date**: May 16, 2026

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    VS Code Extension                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │              extension.ts (Entry Point)            │ │
│  │  - activate()                                      │ │
│  │  - deactivate()                                    │ │
│  └──────────────────┬─────────────────────────────────┘ │
│                     │ registers                          │
│                     ▼                                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │         SidebarProvider (WebviewViewProvider)      │ │
│  │  - resolveWebviewView()                           │ │
│  │  - Message handling                               │ │
│  │  - API integration                                │ │
│  └──────────────────┬─────────────────────────────────┘ │
│                     │                                     │
│                     │ HTTP Requests                       │
│                     ▼                                     │
└─────────────────────┼─────────────────────────────────────┘
                      │
                      │ POST /analyze
                      │ GET /results/{job_id}
                      ▼
         ┌────────────────────────────┐
         │   Backend API Service      │
         │   (http://localhost:8000)  │
         └────────────────────────────┘
```

---

## API Integration Flow

### Phase 1: Initiate Analysis

```typescript
// User clicks "Analyze Workspace" button
1. Get workspace folder path
   → vscode.workspace.workspaceFolders[0].uri.fsPath

2. Send POST request
   → URL: http://localhost:8000/analyze
   → Body: { "local_path": "<workspace_path>" }
   → Method: POST
   → Headers: { "Content-Type": "application/json" }

3. Receive response
   → { "job_id": "unique-job-id" }
   → Store job_id for polling
```

### Phase 2: Poll for Results

```typescript
// Start polling every 3 seconds
setInterval(async () => {
  1. Send GET request
     → URL: http://localhost:8000/results/{job_id}
     → Method: GET

  2. Check response status
     → "in_progress" or "processing": Continue polling
     → "completed" or "complete": Stop polling, show results
     → "failed" or "error": Stop polling, show error

  3. Update UI based on status
     → Display progress messages
     → Show health score when complete
}, 3000);
```

### Phase 3: Display Results

```typescript
// Update webview based on status
switch (status) {
  case 'in_progress':
    // Show progress updates
    webview.postMessage({
      type: 'progress',
      message: '✓ Architect complete...'
    });
    break;

  case 'completed':
    // Show final health score
    webview.postMessage({
      type: 'complete',
      healthScore: 85
    });
    clearInterval(pollingInterval);
    break;

  case 'failed':
    // Show error message
    webview.postMessage({
      type: 'error',
      message: 'Analysis failed'
    });
    clearInterval(pollingInterval);
    break;
}
```

---

## WebView Communication

### Extension → WebView (postMessage)

```typescript
// From SidebarProvider to Webview
this._view.webview.postMessage({
  type: 'status' | 'progress' | 'complete' | 'error',
  message?: string,
  healthScore?: number
});
```

**Message Types**:
- `status`: Initial status update
- `progress`: Ongoing progress updates
- `complete`: Analysis finished with health score
- `error`: Error occurred during analysis

### WebView → Extension (onDidReceiveMessage)

```typescript
// From Webview to SidebarProvider
webviewView.webview.onDidReceiveMessage(async (data) => {
  switch (data.type) {
    case 'analyzeWorkspace':
      await this._analyzeWorkspace();
      break;
  }
});
```

**Message Types**:
- `analyzeWorkspace`: User clicked analyze button

---

## Data Structures

### AnalysisResult Interface

```typescript
interface AnalysisResult {
  job_id: string;
  status: string;
  progress?: {
    architect?: boolean;
    [key: string]: boolean | undefined;
  };
  health_score?: number;
  error?: string;
}
```

### Webview Message Types

```typescript
// Extension to Webview
type ExtensionMessage = 
  | { type: 'status'; message: string }
  | { type: 'progress'; message: string }
  | { type: 'complete'; healthScore: number }
  | { type: 'error'; message: string };

// Webview to Extension
type WebviewMessage = 
  | { type: 'analyzeWorkspace' };
```

---

## State Management

### SidebarProvider State

```typescript
class SidebarProvider {
  _view?: vscode.WebviewView;              // Current webview instance
  _doc?: vscode.TextDocument;              // Document reference
  private _pollingInterval?: ReturnType<typeof setInterval>; // Polling timer
  
  constructor(private readonly _extensionUri: vscode.Uri) {}
}
```

### Lifecycle Management

1. **Initialization**: `resolveWebviewView()` called when sidebar opens
2. **Active**: Webview is visible and interactive
3. **Polling**: Interval running, checking for updates
4. **Cleanup**: `dispose()` clears intervals and releases resources

---

## Error Handling Strategy

### Network Errors

```typescript
try {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
} catch (error) {
  this._view.webview.postMessage({
    type: 'error',
    message: `Failed: ${error.message}`
  });
}
```

### Workspace Errors

```typescript
const workspaceFolders = vscode.workspace.workspaceFolders;
if (!workspaceFolders || workspaceFolders.length === 0) {
  this._view.webview.postMessage({
    type: 'error',
    message: 'No workspace folder open'
  });
  return;
}
```

### Polling Cleanup

```typescript
// Always clear interval on completion or error
if (this._pollingInterval) {
  clearInterval(this._pollingInterval);
  this._pollingInterval = undefined;
}
```

---

## Security Considerations

### Content Security Policy (CSP)

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'none'; 
               style-src ${webview.cspSource} 'unsafe-inline'; 
               script-src 'nonce-${nonce}';">
```

**Restrictions**:
- No external resources by default
- Styles only from webview source or inline
- Scripts only with valid nonce
- Prevents XSS attacks

### Nonce Generation

```typescript
private _getNonce() {
  let text = '';
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}
```

---

## Performance Optimizations

### Polling Interval

- **Frequency**: 3 seconds (configurable)
- **Rationale**: Balance between responsiveness and server load
- **Cleanup**: Interval cleared immediately on completion

### Resource Management

- Webview disposed when sidebar closed
- Intervals cleared on error or completion
- Subscriptions properly managed in context

### HTTP Requests

- Uses node-fetch for efficient HTTP handling
- Proper error handling prevents memory leaks
- Async/await for clean asynchronous code

---

## TypeScript Configuration

### Compiler Options

```json
{
  "module": "commonjs",
  "target": "ES2020",
  "lib": ["ES2020", "DOM"],
  "strict": true,
  "esModuleInterop": true
}
```

**Key Settings**:
- `DOM` library: Enables console, setInterval, clearInterval
- `strict`: Full type checking
- `esModuleInterop`: Better module compatibility

---

**Implementation Status**: ✅ Complete and Tested
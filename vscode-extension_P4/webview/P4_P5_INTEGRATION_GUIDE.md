# P4 ↔ P5 Integration Guide
## Extension (P4) to Webview (P5) Communication

This guide explains how P4 (Extension Lead) and P5 (Webview Lead) integrate their work.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     VS Code Extension (P4)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  extension.ts                                          │ │
│  │  - Registers webview provider                          │ │
│  │  - Handles commands (analyze, refresh)                 │ │
│  │  - Manages backend communication                       │ │
│  │  - Sends messages to webview via postMessage()        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓ postMessage                     │
│                            ↑ postMessage                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Webview (P5) - HTML/CSS/JS                           │ │
│  │  - main.html (structure)                               │ │
│  │  - main.js (logic)                                     │ │
│  │  - styles.css (styling)                                │ │
│  │  - Listens for messages via window.addEventListener   │ │
│  │  - Renders UI based on received data                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## For P4: How to Send Data to P5

### 1. Setup Webview Provider (extension.ts)

```typescript
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

class RepoSenseViewProvider implements vscode.WebviewViewProvider {
  private _view?: vscode.WebviewView;

  constructor(private readonly _extensionUri: vscode.Uri) {}

  resolveWebviewView(webviewView: vscode.WebviewView) {
    this._view = webviewView;
    
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [
        vscode.Uri.joinPath(this._extensionUri, 'webview')
      ]
    };
    
    // Load the HTML file
    webviewView.webview.html = this.getWebviewContent(webviewView.webview);
    
    // Listen for messages FROM webview
    webviewView.webview.onDidReceiveMessage(message => {
      switch (message.type) {
        case 'retry':
          this.startAnalysis();
          break;
      }
    });
    
    // Auto-start analysis when webview loads
    this.startAnalysis();
  }

  private getWebviewContent(webview: vscode.Webview): string {
    // Get paths to resources
    const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'main.html');
    const cssPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'styles.css');
    const jsPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'main.js');
    
    // Convert to webview URIs
    const cssUri = webview.asWebviewUri(cssPath);
    const jsUri = webview.asWebviewUri(jsPath);
    const d3Uri = 'https://cdn.jsdelivr.net/npm/d3@7';
    
    // Read HTML file
    let html = fs.readFileSync(htmlPath.fsPath, 'utf8');
    
    // Replace resource paths with webview URIs
    html = html.replace('href="styles.css"', `href="${cssUri}"`);
    html = html.replace('src="main.js"', `src="${jsUri}"`);
    html = html.replace('src="https://cdn.jsdelivr.net/npm/d3@7"', `src="${d3Uri}"`);
    
    return html;
  }

  async startAnalysis() {
    const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath;
    if (!workspacePath) {
      this.sendMessage({ type: 'error', message: 'No workspace open' });
      return;
    }

    // Send loading state
    this.sendMessage({ type: 'loading', step: 'Starting analysis...' });

    try {
      // Call backend API
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ local_path: workspacePath })
      });
      
      const { job_id } = await res.json();
      this.pollResults(job_id);
      
    } catch (e) {
      this.sendMessage({
        type: 'error',
        message: 'Cannot connect to RepoSense backend. Is it running on port 8000?'
      });
    }
  }

  private pollResults(jobId: string) {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/results/${jobId}`);
        const data = await res.json();

        // Send progress updates
        if (data.progress) {
          this.sendMessage({ 
            type: 'progress', 
            data: {
              percentage: this.calculateProgress(data.progress),
              step: this.getCurrentStep(data.progress)
            }
          });
        }

        // Handle completion
        if (data.status === 'complete') {
          clearInterval(interval);
          this.sendMessage({ type: 'results', data: data.results });
          
          // Show notification
          vscode.window.showInformationMessage(
            `RepoSense: Analysis complete — Score ${data.results.health.score}/100`
          );
        } 
        else if (data.status === 'failed') {
          clearInterval(interval);
          this.sendMessage({ 
            type: 'error', 
            message: data.error || 'Analysis failed' 
          });
        }
      } catch (e) {
        clearInterval(interval);
        this.sendMessage({ type: 'error', message: 'Lost connection to backend' });
      }
    }, 3000); // Poll every 3 seconds
  }

  private calculateProgress(progressSteps: any[]): number {
    const completed = progressSteps.filter(s => s.status === 'done').length;
    return Math.round((completed / progressSteps.length) * 100);
  }

  private getCurrentStep(progressSteps: any[]): string {
    const active = progressSteps.find(s => s.status === 'active');
    return active ? active.name : 'Processing...';
  }

  private sendMessage(message: any) {
    this._view?.webview.postMessage(message);
  }
}

export function activate(context: vscode.ExtensionContext) {
  const provider = new RepoSenseViewProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('reposense.mainPanel', provider)
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('reposense.analyze', () => {
      provider.startAnalysis();
    })
  );
}
```

### 2. Message Types P4 Sends to P5

```typescript
// Loading state
{
  type: 'loading',
  step: string  // e.g., "Starting analysis...", "Parsing files..."
}

// Progress update
{
  type: 'progress',
  data: {
    percentage: number,  // 0-100
    step: string        // Current step name
  }
}

// Results (analysis complete)
{
  type: 'results',
  data: {
    health: { score, grade, summary, priorities },
    architecture: { nodes, edges },
    review: { findings },
    documentation: { functions, tests },
    security: { issues, modernization }
  }
}

// Error state
{
  type: 'error',
  message: string  // User-friendly error message
}
```

---

## For P5: How to Receive Data from P4

### 1. Setup Message Listener (main.js)

```javascript
// Acquire VS Code API (only works inside VS Code webview)
const vscode = acquireVsCodeApi();

// Listen for messages from extension
window.addEventListener('message', event => {
  const msg = event.data;
  console.log('Received message:', msg.type);
  
  switch (msg.type) {
    case 'loading':
      showLoadingState(msg.step);
      break;
      
    case 'progress':
      updateProgress(msg.data);
      break;
      
    case 'results':
      analysisData = msg.data;
      showResults(msg.data);
      break;
      
    case 'error':
      showError(msg.message);
      break;
  }
});

// Send messages TO extension (e.g., retry button)
function retryAnalysis() {
  vscode.postMessage({ type: 'retry' });
}
```

### 2. Implement State Handlers

```javascript
function showLoadingState(step) {
  hideAllStates();
  document.getElementById('loadingState').classList.remove('hidden');
  document.getElementById('loadingStep').textContent = step;
}

function updateProgress(data) {
  const progressFill = document.getElementById('progressFill');
  progressFill.style.width = `${data.percentage}%`;
  
  const loadingStep = document.getElementById('loadingStep');
  loadingStep.textContent = data.step;
}

function showResults(data) {
  hideAllStates();
  
  // Render each panel
  renderHealthPanel(data.health);
  renderArchitecturePanel(data.architecture);
  renderReviewPanel(data.review);
  renderDocsPanel(data.documentation);
  renderSecurityPanel(data.security);
  
  // Show health panel by default
  switchPanel('health');
}

function showError(message) {
  hideAllStates();
  document.getElementById('errorState').classList.remove('hidden');
  document.getElementById('errorMessage').textContent = message;
}

function hideAllStates() {
  document.getElementById('loadingState').classList.add('hidden');
  document.getElementById('errorState').classList.add('hidden');
}
```

---

## File Structure

```
your-extension/
├── src/
│   └── extension.ts          ← P4 works here
├── webview/                   ← P5 works here
│   ├── main.html
│   ├── main.js
│   ├── styles.css
│   ├── sample-data.js         ← For standalone testing
│   └── test-dependency-tree.html  ← Standalone test page
├── package.json
└── tsconfig.json
```

---

## Testing Integration

### P5: Test Standalone (Without Extension)

1. Create a test HTML file that simulates the extension:

```html
<!-- test-standalone.html -->
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
  <script src="sample-data.js"></script>
  <script src="main.js"></script>
  <script>
    // Mock VS Code API
    window.acquireVsCodeApi = () => ({
      postMessage: (msg) => console.log('To extension:', msg)
    });
    
    // Auto-load test data
    setTimeout(() => {
      window.postMessage({ type: 'results', data: sampleAnalysisData }, '*');
    }, 1000);
  </script>
</body>
</html>
```

2. Open in browser: `python3 -m http.server 8080`

### P4: Test with Mock Webview

```typescript
// In extension.ts, add a test command
context.subscriptions.push(
  vscode.commands.registerCommand('reposense.testWebview', () => {
    // Send mock data to webview
    provider.sendMessage({
      type: 'results',
      data: require('./webview/sample-data.js').sampleAnalysisData
    });
  })
);
```

---

## Common Integration Issues

### Issue 1: "acquireVsCodeApi is not defined"
**Cause:** Testing webview outside VS Code  
**Solution:** Mock the API in standalone tests (see above)

### Issue 2: Resources not loading (CSS/JS 404)
**Cause:** Incorrect resource paths or missing `localResourceRoots`  
**Solution:** Use `webview.asWebviewUri()` for all local resources

```typescript
const cssUri = webview.asWebviewUri(
  vscode.Uri.joinPath(this._extensionUri, 'webview', 'styles.css')
);
```

### Issue 3: Webview shows blank screen
**Cause:** JavaScript errors or CSP violations  
**Solution:** 
- Check browser console (F12) in Extension Host
- Add CSP meta tag to HTML:
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'none'; 
               style-src 'unsafe-inline' https://cdn.jsdelivr.net; 
               script-src 'unsafe-inline' https://cdn.jsdelivr.net; 
               img-src https: data:;">
```

### Issue 4: Messages not received
**Cause:** Timing issue - webview not ready  
**Solution:** P4 should wait for webview to be fully loaded before sending messages

---

## Handoff Checklist

### P4 Provides to P5:
- [ ] Message format specification (types and data structures)
- [ ] Sample data file matching the API contract
- [ ] Extension URI for loading resources
- [ ] CSP requirements

### P5 Provides to P4:
- [ ] `main.html` - Complete webview HTML
- [ ] `main.js` - All UI logic
- [ ] `styles.css` - All styling
- [ ] List of message types webview can send back (e.g., 'retry')
- [ ] Resource dependencies (D3.js CDN, etc.)

### Integration Testing:
- [ ] P5 tests standalone with mock data
- [ ] P4 tests with mock webview responses
- [ ] End-to-end test with real backend
- [ ] Test error states (backend down, invalid data)
- [ ] Test loading states and progress updates

---

## Quick Reference

### P4 → P5 (Extension to Webview)
```typescript
this._view?.webview.postMessage({ type: 'results', data: analysisData });
```

### P5 → P4 (Webview to Extension)
```javascript
vscode.postMessage({ type: 'retry' });
```

### P5 Receives Messages
```javascript
window.addEventListener('message', event => {
  const msg = event.data;
  // Handle msg.type
});
```

---

## Advanced: State Persistence

If you want to persist webview state across VS Code restarts:

### P5: Save State
```javascript
const vscode = acquireVsCodeApi();
const state = vscode.getState() || {};

// Save state
state.currentPanel = 'architecture';
vscode.setState(state);
```

### P5: Restore State
```javascript
const state = vscode.getState();
if (state && state.currentPanel) {
  switchPanel(state.currentPanel);
}
```

---

## Resources

- [VS Code Webview API](https://code.visualstudio.com/api/extension-guides/webview)
- [VS Code Extension Samples](https://github.com/microsoft/vscode-extension-samples)
- [D3.js Documentation](https://d3js.org/)
- Project files: `db_schema.md`, `graph_spec.md`
# RepoSense Webview - P5 Component

This directory contains all the UI components for the RepoSense VS Code extension webview.

## Structure

```
webview/
├── main.html          # Main webview HTML structure
├── styles.css         # VS Code-themed styling
├── main.js            # Core JavaScript logic and message handling
├── components/        # Reusable UI components (future)
├── assets/            # Images, icons, etc. (future)
└── utils/             # Helper functions (future)
```

## Features Implemented

### 1. **Health Score Panel** 
- Animated circular progress ring
- Score animation from 0 to final value
- Grade badge with color coding (A=green, B=blue, C=amber, D/F=red)
- Top priorities list
- Summary text

### 2. **Architecture Graph Panel**
- D3.js force-directed graph
- Node colors by type (entry, service, util, config, test)
- Interactive zoom and pan controls
- Draggable nodes
- Hover tooltips with module descriptions
- Spring physics animation

### 3. **Code Review Panel**
- Findings sorted by severity (CRITICAL first)
- Severity badges with color coding
- File location display
- Expandable details with suggestions
- Filter buttons (ALL / HIGH+ / CRITICAL)

### 4. **Documentation Panel**
- Two tabs: Documentation and Test Stubs
- Function documentation with params, returns, examples
- Copyable code blocks
- Monospace styling for code

### 5. **Security Panel**
- Security issues section with "Fix This First" highlight
- Modernization opportunities section
- Effort badges (LOW/MED/HIGH)
- Priority-ordered lists

### 6. **Navigation & States**
- Tab bar with active state highlighting
- Badge counts for findings
- Loading state with animated pulse and progress bar
- Error state with retry button
- Smooth panel transitions

## Message Protocol

The webview communicates with the extension via `postMessage`:

### Messages FROM Extension TO Webview:

```javascript
// Loading state
{ type: 'loading', step: 'Parsing files...' }

// Progress update
{ type: 'progress', data: { percentage: 45, step: 'Analyzing...' } }

// Results ready
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

// Error occurred
{ type: 'error', message: 'Analysis failed: ...' }
```

### Messages FROM Webview TO Extension:

```javascript
// Retry analysis
{ type: 'retry' }
```

## Data Structure Examples

### Health Data
```javascript
{
  score: 85,
  grade: 'B',
  summary: 'Your codebase is in good shape...',
  priorities: [
    'Add unit tests for core modules',
    'Document public APIs',
    'Fix 3 critical security issues'
  ]
}
```

### Architecture Data
```javascript
{
  nodes: [
    { id: 'main', name: 'main.js', type: 'entry', description: 'Entry point' },
    { id: 'api', name: 'api.js', type: 'service', description: 'API handler' }
  ],
  edges: [
    { source: 'main', target: 'api' }
  ]
}
```

### Review Data
```javascript
{
  findings: [
    {
      severity: 'CRITICAL',
      file: 'src/auth.js',
      line: 42,
      message: 'Hardcoded credentials detected',
      suggestion: 'Use environment variables for sensitive data'
    }
  ]
}
```

## Styling

The webview uses VS Code's native CSS variables to match the editor theme:

- `--vscode-sideBar-background`
- `--vscode-foreground`
- `--vscode-font-family`
- `--vscode-font-size`
- And many more...

Custom accent colors:
- Blue: `#3b82f6`
- Green: `#10b981`
- Amber: `#f59e0b`
- Red: `#ef4444`
- Purple: `#8b5cf6`

## Development Notes

### Testing the Webview
1. The webview runs inside VS Code as an iframe
2. Use Chrome DevTools to inspect: `Help > Toggle Developer Tools`
3. Test with different themes (dark/light)
4. Test with various data sizes (empty, small, large datasets)

### Performance Considerations
- D3.js graph is optimized for up to ~100 nodes
- Large datasets use virtual scrolling (future enhancement)
- Animations use `requestAnimationFrame` for smooth 60fps

### Browser Compatibility
- Targets VS Code's embedded Chromium
- Uses modern ES6+ features
- No polyfills needed

## Integration with P4 (Extension Lead)

P4 will:
1. Create a webview panel in VS Code
2. Load `main.html` into the webview
3. Send messages to update the UI
4. Handle retry requests from the webview

Example integration code for P4:
```javascript
const panel = vscode.window.createWebviewPanel(
  'reposense',
  'RepoSense Analysis',
  vscode.ViewColumn.One,
  {
    enableScripts: true,
    localResourceRoots: [vscode.Uri.file(path.join(context.extensionPath, 'webview'))]
  }
);

// Load HTML
const htmlPath = vscode.Uri.file(path.join(context.extensionPath, 'webview', 'main.html'));
panel.webview.html = fs.readFileSync(htmlPath.fsPath, 'utf8');

// Send results
panel.webview.postMessage({
  type: 'results',
  data: analysisResults
});
```

## Next Steps (Hour 4-22)

- [ ] Hour 4-10: Implement and test Health Score panel animations
- [ ] Hour 4-10: Build and test Architecture Graph with D3.js
- [ ] Hour 10-16: Complete Review, Docs, and Security panels
- [ ] Hour 16-18: Polish navigation and transitions
- [ ] Hour 18-22: Add skeleton loading states, empty states, responsive design

## Dependencies

- **D3.js v7**: Loaded via CDN for architecture graph
- **VS Code API**: `acquireVsCodeApi()` for extension communication

## Notes for Team

- All panels are built and ready for data
- Message protocol is defined and implemented
- Styling matches VS Code theme automatically
- Ready for integration with P4's extension code
- Can be tested standalone by mocking `postMessage` events
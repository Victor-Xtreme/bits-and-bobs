# RepoSense Webview - P5 Component (Ready for P4 Integration)

## Overview (P5 → P4 Handoff)

### Please refer to this [pull request](https://github.com/Victor-Xtreme/bits-and-bobs/pull/7)


This directory contains the complete Webview UI implementation for the RepoSense VS Code extension. All panels (Health Score, Architecture Graphs, Code Review, Documentation, and Security) are fully implemented and ready for integration with the extension backend.

## 📁 File Structure

```
vscode-extension/webview/
├── main.html                          # Main webview HTML structure
├── main.js                            # Core JavaScript with dual-view graph
├── styles.css                         # VS Code-themed styling
│
├── sample-data.js                     # Simple test data (9 nodes)
├── sample-data-complex.js             # Complex test data (31 nodes, 68 edges)
│
├── test-dependency-tree.html          # Simple standalone test
├── test-complex-tree.html             # Complex standalone test
│
├── db_schema.md                       # Database schema reference
├── graph_spec.md                      # Graph specification
├── DEPENDENCY_TREE_IMPLEMENTATION.md  # Implementation details
├── COMPLETE_GUIDE.md                  # Comprehensive feature guide
├── P4_P5_INTEGRATION_GUIDE.md         # Integration instructions
└── README.md                          # This file
```

**Note:** Monolithic file structure maintained intentionally for easy string replacement in `getWebviewContent()` - no ES module mapping required.

## ✨ Features Implemented

### 1. **Health Score Panel**
- Animated circular progress ring
- Score animation from 0 to final value
- Grade badge with color coding (A=green, B=blue, C=amber, D/F=red)
- Top priorities list
- Summary text

### 2. **Architecture Graph Panel** (Dual-View System)
**Network View** (Original):
- D3.js force-directed graph showing all nodes
- Interactive zoom and pan controls
- Draggable nodes with spring physics
- Node colors by type (entry, service, util, config, test)
- Hover tooltips with module descriptions

**Tree View** (New - Bidirectional Dependency Tree):
- Selected node at center (larger, white border)
- **Dependents** (upstream) positioned above - nodes that depend on selected
- **Dependencies** (downstream) positioned below - nodes selected depends on
- **Depth control slider** (1-5 levels) for traversal depth
- **Click to re-root** - any node becomes new center
- **Focused subgraph** - shows only relevant nodes around selection
- **Edge relationship styles**:
  - Solid lines: `imports`
  - Dashed lines: `extends`
  - Dotted lines: `calls`

**View Toggle**: Seamless switch between Network and Tree modes

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

## 🔌 Integration Notes for P4

### Message Protocol

**Extension → Webview (P4 sends to P5):**

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

**Webview → Extension (P5 sends to P4):**

```javascript
// Retry analysis
{ type: 'retry' }
```

### Data Structure Requirements

**GraphNode:**
```javascript
{
  id: string,           // Must match ParsedFile.path
  label: string,        // Display name (NEW)
  name: string,         // File name
  type: NodeType,       // 'entry' | 'service' | 'util' | 'config' | 'test'
  description: string   // Tooltip description
}
```

**GraphEdge:**
```javascript
{
  source: string,           // GraphNode.id of dependent
  target: string,           // GraphNode.id of dependency
  relationship: string      // 'imports' | 'extends' | 'calls' (NEW)
}
```

## 🧪 Testing

### Standalone Browser Testing

Test the UI without VS Code using the provided test files:

```bash
cd vscode-extension/webview
python3 -m http.server 8080
```

Then open:
- **Simple test**: http://localhost:8080/test-dependency-tree.html
- **Complex test**: http://localhost:8080/test-complex-tree.html

### Test Scenarios
1. **View Toggle**: Switch between Network and Tree views
2. **Re-rooting**: Click nodes in Tree view to change focus
3. **Depth Control**: Adjust slider (1-5) to see more/fewer levels
4. **Zoom Controls**: Test zoom in/out/reset
5. **Edge Styles**: Verify solid/dashed/dotted lines for different relationships
6. **Node Colors**: Verify colors match type specifications
7. **All Panels**: Switch tabs to test Health, Review, Docs, Security
8. **States**: Test loading, progress, error, and retry functionality

## 🎨 Styling

Uses VS Code native CSS variables for seamless theme integration:
- `--vscode-sideBar-background`
- `--vscode-foreground`
- `--vscode-font-family`
- `--vscode-font-size`

Custom accent colors:
- Blue: `#3b82f6`, Green: `#10b981`, Amber: `#f59e0b`, Red: `#ef4444`, Purple: `#8b5cf6`, Teal: `#14b8a6`, Gray: `#6b7280`

**CSP Updated**: Relaxed for local testing while maintaining security for VS Code iframe.

## 📖 Documentation

- **[`COMPLETE_GUIDE.md`](vscode-extension/webview/COMPLETE_GUIDE.md)** - Comprehensive feature documentation
- **[`DEPENDENCY_TREE_IMPLEMENTATION.md`](vscode-extension/webview/DEPENDENCY_TREE_IMPLEMENTATION.md)** - Technical implementation details
- **[`P4_P5_INTEGRATION_GUIDE.md`](vscode-extension/webview/P4_P5_INTEGRATION_GUIDE.md)** - Step-by-step integration instructions
- **[`graph_spec.md`](vscode-extension/webview/graph_spec.md)** - Graph specification
- **[`db_schema.md`](vscode-extension/webview/db_schema.md)** - Data model reference

## 🚀 Performance

- **Tree View**: Client-side BFS traversal, no server calls for re-rooting
- **Network View**: Force simulation optimized for ~100 nodes
- **Depth-Limited**: Efficient traversal stops at configured depth
- **Lazy Rendering**: Graphs only render when Architecture tab is visible
- **Smooth Animations**: Uses `requestAnimationFrame` for 60fps

## 📦 Dependencies

- **D3.js v7**: Loaded via CDN for both graph views
- **VS Code API**: `acquireVsCodeApi()` for extension communication

## 🎯 Ready for Integration

All webview assets are in the correct locations per `filetree.md`. The monolithic structure ensures your `getWebviewContent()` string replacement logic works immediately without additional URI mapping.

**Next Steps for P4:**
1. Copy webview files to extension
2. Implement `getWebviewContent()` with URI replacements
3. Send messages using the documented protocol
4. Test with mock data first, then integrate with backend

---

**Made with ❤️ for IBM Bob Hackathon 2026**

# RepoSense Webview - Complete Guide

This is the complete guide for the RepoSense webview implementation, including the bidirectional dependency tree graph.

---

## 📁 File Structure

```
webview/
├── main.html                          # Main webview HTML structure
├── main.js                            # Core JavaScript logic with dependency tree
├── styles.css                         # VS Code-themed styling
│
├── sample-data.js                     # Simple test data (9 nodes)
├── sample-data-complex.js             # Complex test data (31 nodes, 68 edges)
│
├── test-dependency-tree.html          # Simple test page
├── test-complex-tree.html             # Complex test page
│
├── db_schema.md                       # Database schema reference
├── graph_spec.md                      # Graph specification
├── DEPENDENCY_TREE_IMPLEMENTATION.md  # Implementation details
├── P4_P5_INTEGRATION_GUIDE.md         # P4↔P5 integration guide
└── COMPLETE_GUIDE.md                  # This file
```

---

## 🚀 Quick Start

### For P5 (Webview Developer)

1. **Test Standalone (No Extension Required)**
   ```bash
   cd webview
   python3 -m http.server 8080
   ```
   
2. **Open Test Pages**
   - Simple: http://localhost:8080/test-dependency-tree.html
   - Complex: http://localhost:8080/test-complex-tree.html

3. **Interact with the Graph**
   - Click nodes to re-root the tree
   - Adjust depth slider (1-5) to see more/fewer levels
   - Use zoom controls
   - Hover over nodes for tooltips

### For P4 (Extension Developer)

1. **Copy Webview Files to Extension**
   ```bash
   cp -r webview/ your-extension/webview/
   ```

2. **Load in Extension** (see `P4_P5_INTEGRATION_GUIDE.md`)
   ```typescript
   const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'webview', 'main.html');
   webviewView.webview.html = this.getWebviewContent(webview);
   ```

3. **Send Data to Webview**
   ```typescript
   this._view?.webview.postMessage({ 
     type: 'results', 
     data: analysisData 
   });
   ```

---

## 🎨 Features Implemented

### ✅ Bidirectional Dependency Tree
- **Selected node** at center (larger, white border)
- **Dependents** (upstream) above - nodes that depend on selected
- **Dependencies** (downstream) below - nodes selected depends on
- **Configurable depth** (1-5 levels)
- **Click to re-root** - any node becomes new center

### ✅ Node Rendering
- **Color by type** (per spec):
  - Entry: Red (#ef4444)
  - Service: Blue (#3b82f6)
  - Util: Teal (#14b8a6)
  - Config: Amber (#f59e0b)
  - Test: Gray (#6b7280)
- **Tooltips** with name, type, description
- **Labels** below each node

### ✅ Edge Rendering
- **Line styles by relationship**:
  - Imports: Solid line
  - Extends: Dashed line (5,5)
  - Calls: Dotted line (2,3)
- **Arrows** point from dependent to dependency
- **Filtered** to only show edges between visible nodes

### ✅ Interactive Controls
- **Depth slider** (1-5)
- **Zoom controls** (in/out/reset)
- **Re-rooting** on node click
- **Smooth transitions**

### ✅ Other Panels
- Health Score with animated ring
- Code Review with severity filtering
- Documentation with copy buttons
- Security issues and modernization

---

## 📊 Test Data

### Simple Data (`sample-data.js`)
- **9 nodes**: 1 entry, 3 services, 2 utils, 1 config, 2 tests
- **10 edges**: Mix of imports, calls
- **Good for**: Initial testing, understanding the layout

### Complex Data (`sample-data-complex.js`)
- **31 nodes**: 2 entries, 19 services, 4 utils, 3 configs, 5 tests
- **68 edges**: All relationship types
- **Multi-level**: Up to 5 levels deep
- **Good for**: Stress testing, realistic scenarios

---

## 🔧 How It Works

### 1. Traversal Algorithm (`buildSubgraph`)

```javascript
function buildSubgraph(nodeId, allNodes, allEdges, depth) {
  // BFS traversal
  // Finds dependents: edges where edge.target === nodeId
  // Finds dependencies: edges where edge.source === nodeId
  // Respects depth limit
  // Returns: { selected_node, dependents, dependencies, edges }
}
```

### 2. Layout Algorithm

```javascript
// Position selected node at center
selected_node.x = centerX;
selected_node.y = centerY;

// Position dependents above in grid
dependents.forEach((node, i) => {
  node.x = centerX + offsetX;
  node.y = centerY - verticalSpacing * (row + 1);
});

// Position dependencies below in grid
dependencies.forEach((node, i) => {
  node.x = centerX + offsetX;
  node.y = centerY + verticalSpacing * (row + 1);
});
```

### 3. Re-rooting

```javascript
node.on('click', (event, d) => {
  currentSelectedNode = d.id;
  renderDependencyTree(d.id, currentDepth);
});
```

---

## 🔗 Integration with P4

### Message Flow

```
P4 Extension                    P5 Webview
    │                               │
    ├──── postMessage('loading') ──>│
    │                               ├─ showLoadingState()
    │                               │
    ├──── postMessage('progress') ─>│
    │                               ├─ updateProgress()
    │                               │
    ├──── postMessage('results') ──>│
    │                               ├─ showResults()
    │                               ├─ renderHealthPanel()
    │                               ├─ renderArchitecturePanel()
    │                               └─ renderOtherPanels()
    │                               │
    │<─── postMessage('retry') ─────┤
    ├─ startAnalysis()              │
```

### Data Contract

```typescript
// P4 sends to P5
interface AnalysisResults {
  health: {
    score: number;
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
    summary: string;
    priorities: string[];
  };
  architecture: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
  review: { findings: Finding[] };
  documentation: { functions: DocEntry[], tests: TestEntry[] };
  security: { issues: SecurityIssue[], modernization: ModernizationItem[] };
}

interface GraphNode {
  id: string;           // Must match ParsedFile.path
  label: string;        // Display name
  name: string;         // File name
  type: 'entry' | 'service' | 'util' | 'config' | 'test';
  description: string;
}

interface GraphEdge {
  source: string;       // Node ID (dependent)
  target: string;       // Node ID (dependency)
  relationship: 'imports' | 'extends' | 'calls';
}
```

---

## 🧪 Testing Checklist

### Standalone Testing (P5)
- [ ] Open `test-dependency-tree.html` - simple data loads
- [ ] Open `test-complex-tree.html` - complex data loads
- [ ] Click different nodes - tree re-roots correctly
- [ ] Adjust depth slider - more/fewer nodes appear
- [ ] Zoom in/out - graph scales properly
- [ ] Hover nodes - tooltips appear
- [ ] Check edge styles - solid/dashed/dotted visible
- [ ] Check node colors - match type specifications
- [ ] Switch tabs - all panels render
- [ ] Test with empty data - shows empty states

### Integration Testing (P4 + P5)
- [ ] Extension loads webview
- [ ] Loading state appears
- [ ] Progress updates work
- [ ] Results render correctly
- [ ] Error states display properly
- [ ] Retry button works
- [ ] All resources load (CSS, JS, D3)
- [ ] No console errors
- [ ] Performance is acceptable

---

## 📖 Key Documentation

1. **`graph_spec.md`** - Official specification for the dependency tree
2. **`db_schema.md`** - Data model and schema reference
3. **`DEPENDENCY_TREE_IMPLEMENTATION.md`** - Implementation details
4. **`P4_P5_INTEGRATION_GUIDE.md`** - How P4 and P5 work together

---

## 🎯 Key Concepts

### Edge Direction Convention
```
source → target
  │
  └── "source depends on target"
```

- **Dependents**: Nodes where `edge.target === selectedNode`
- **Dependencies**: Nodes where `edge.source === selectedNode`

### Tree vs Graph
- **Not a full graph**: Only shows focused subgraph around selected node
- **Tree structure**: Dependents above, dependencies below
- **Depth-limited**: Configurable 1-5 levels

### Client-Side Traversal
- All nodes/edges loaded once
- Subgraph built on-demand in browser
- No server calls for re-rooting
- Fast and responsive

---

## 🐛 Troubleshooting

### Graph doesn't render
1. Check browser console for errors
2. Verify D3.js loaded: `typeof d3` should not be `undefined`
3. Check data format matches specification
4. Ensure container has non-zero dimensions

### Nodes overlap
- Increase `horizontalSpacing` or `verticalSpacing` in `renderDependencyTree()`
- Reduce number of nodes per row

### Performance issues with large graphs
- Limit depth to 2-3 for very large codebases
- Consider implementing virtual scrolling
- Add node filtering/search

### Resources not loading in extension
- Use `webview.asWebviewUri()` for all local resources
- Check `localResourceRoots` in webview options
- Verify CSP allows required resources

---

## 🚢 Deployment

### For P5 Handoff to P4
1. Ensure all files in `webview/` are ready
2. Test standalone with both simple and complex data
3. Document any external dependencies (D3.js CDN)
4. Provide sample data files
5. List message types webview expects

### For P4 Integration
1. Copy `webview/` folder to extension
2. Update resource paths in `extension.ts`
3. Configure CSP in HTML
4. Test with mock data first
5. Integrate with real backend

---

## 📝 Notes

- **VS Code Theme**: Uses native CSS variables for seamless integration
- **D3.js**: Loaded from CDN (v7) - no local copy needed
- **No Build Step**: Pure HTML/CSS/JS - works immediately
- **Responsive**: Adapts to different webview sizes
- **Accessible**: Keyboard navigation, ARIA labels (can be improved)

---

## 🎓 Learning Resources

- [D3.js Force Layout](https://d3js.org/d3-force)
- [VS Code Webview Guide](https://code.visualstudio.com/api/extension-guides/webview)
- [Graph Theory Basics](https://en.wikipedia.org/wiki/Directed_graph)
- [BFS Algorithm](https://en.wikipedia.org/wiki/Breadth-first_search)

---

## ✨ Future Enhancements

Potential improvements (not in current spec):
- [ ] Search/filter nodes by name
- [ ] Highlight path between two nodes
- [ ] Export graph as PNG/SVG
- [ ] Collapse/expand subtrees
- [ ] Show edge labels on hover
- [ ] Mini-map for large graphs
- [ ] Keyboard shortcuts
- [ ] Dark/light theme toggle
- [ ] Animation on re-root
- [ ] Node grouping by directory

---

## 👥 Team Roles

- **P4 (Extension Lead)**: Manages VS Code extension, backend communication
- **P5 (Webview Lead)**: Builds UI, implements graph visualization
- **Integration**: Both work together using message passing

---

## 📞 Support

For questions or issues:
1. Check this guide first
2. Review `P4_P5_INTEGRATION_GUIDE.md`
3. Inspect browser console for errors
4. Test with sample data to isolate issues
5. Verify data format matches `db_schema.md`

---

**Made with ❤️ for IBM Bob Hackathon 2026**
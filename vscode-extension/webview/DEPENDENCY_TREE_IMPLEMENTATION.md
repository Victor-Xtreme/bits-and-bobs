# Bidirectional Dependency Tree Implementation

This document describes the implementation of the bidirectional dependency tree graph as specified in `graph_spec.md`.

## Overview

The dependency tree visualization shows:
- **Selected node** at the center (highlighted with larger size and white border)
- **Dependents** (upstream) - nodes that depend on the selected node - positioned above
- **Dependencies** (downstream) - nodes that the selected node depends on - positioned below

## Key Features Implemented

### 1. Traversal Algorithm (`buildSubgraph`)
Located in `main.js`, this function implements the breadth-first search algorithm from the spec:
- Finds all dependents by following edges where `edge.target === selectedNode`
- Finds all dependencies by following edges where `edge.source === selectedNode`
- Respects the configurable depth parameter (default: 1, max: 5)
- Returns only edges between visible nodes

### 2. Node Rendering
Each node is rendered with:
- **Color coding by type** (as per spec):
  - `entry`: Red/Coral (#ef4444) - entrypoints that many things depend on
  - `service`: Blue (#3b82f6) - core business logic
  - `util`: Teal (#14b8a6) - shared helpers
  - `config`: Amber (#f59e0b) - configuration modules
  - `test`: Gray (#6b7280) - test files
- **Size**: Selected node is 20% larger than others
- **Border**: Selected node has a white border
- **Label**: Displayed below each node
- **Tooltip**: Shows name, type, and description on hover

### 3. Edge Rendering
Edges are rendered with different styles based on relationship type:
- **`imports`**: Solid line (opacity 0.8)
- **`extends`**: Dashed line (5,5 pattern, opacity 0.7)
- **`calls`**: Dotted line (2,3 pattern, opacity 0.6)
- **Direction**: Arrow points from source (dependent) to target (dependency)

### 4. Re-rooting
- Click any node to re-root the tree at that node
- The tree rebuilds showing dependents/dependencies from the new perspective
- Maintains the current depth setting

### 5. Depth Control
- Slider control (1-5) to adjust traversal depth
- Depth 1: Shows immediate neighbors only
- Depth 5: Shows up to 5 levels of transitive dependencies/dependents
- Updates in real-time when slider is moved

### 6. Layout Algorithm
- **Vertical tree layout**: Dependents above, dependencies below
- **Grid positioning**: Multiple nodes at same level arranged in rows
- **Spacing**: 100px vertical, 150px horizontal between nodes
- **Centering**: Selected node always at center of viewport

## Data Structure Requirements

### GraphNode
```javascript
{
  id: string,           // Must match ParsedFile.path
  label: string,        // Display name
  name: string,         // File name
  type: NodeType,       // 'entry' | 'service' | 'util' | 'config' | 'test'
  description: string   // Tooltip description
}
```

### GraphEdge
```javascript
{
  source: string,           // GraphNode.id of dependent
  target: string,           // GraphNode.id of dependency
  relationship: string      // 'imports' | 'extends' | 'calls'
}
```

## Testing

### Test File
Open `test-dependency-tree.html` in a browser to test the implementation:

```bash
cd webview
python3 -m http.server 8080
# Open http://localhost:8080/test-dependency-tree.html
```

### Test Scenarios
1. **Initial Load**: Should show 'main.js' (entry node) at center with its immediate dependencies
2. **Click Node**: Click any node to re-root the tree
3. **Adjust Depth**: Move slider to see more/fewer levels
4. **Hover**: Hover over nodes to see tooltips
5. **Zoom**: Use zoom controls to zoom in/out
6. **Edge Styles**: Verify different line styles for different relationship types

### Sample Data
The `sample-data.js` file includes a test architecture with:
- 9 nodes (1 entry, 3 services, 2 utils, 1 config, 2 tests)
- 10 edges with different relationship types
- Proper bidirectional dependencies

## Integration with Backend

The webview expects data in this format:

```javascript
{
  architecture: {
    nodes: GraphNode[],
    edges: GraphEdge[]
  }
}
```

All nodes and edges are loaded once. The client-side traversal algorithm builds subgraphs on demand without additional API calls.

## Key Differences from Previous Implementation

### Before (Force-Directed Graph)
- Used D3 force simulation
- All nodes visible at once
- Physics-based layout
- Draggable nodes with forces

### After (Bidirectional Tree)
- Tree-based layout
- Focused subgraph around selected node
- Fixed grid positioning
- Click to re-root, not drag

## Files Modified

1. **main.js**
   - Replaced `renderArchitecturePanel()` with tree-based implementation
   - Added `buildSubgraph()` traversal algorithm
   - Added `renderDependencyTree()` for tree layout
   - Added depth slider event handler

2. **main.html**
   - Added depth control slider to graph controls

3. **styles.css**
   - Added styles for depth control
   - Updated graph controls layout

4. **sample-data.js**
   - Added `label` field to nodes
   - Added `relationship` field to edges

## Performance Considerations

- **Client-side traversal**: No server calls needed for re-rooting
- **Efficient BFS**: Stops at configured depth
- **Lazy rendering**: Graph only renders when Architecture tab is visible
- **Single render**: No continuous animation/simulation

## Future Enhancements

Potential improvements (not in current spec):
- Search/filter nodes by name or type
- Highlight path between two nodes
- Export graph as image
- Collapse/expand subtrees
- Show edge labels on hover
- Mini-map for large graphs
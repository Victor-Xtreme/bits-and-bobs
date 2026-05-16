# RepoSense — dependency tree graph spec

This document describes how the architecture graph data maps to a bidirectional dependency tree, what the webview receives, and how to render it.

---

## Concept

When a user selects a node, the tree grows in two directions from that node:

- **Upward — dependents:** modules that depend on the selected node
- **Downward — dependencies:** modules that the selected node depends on

The selected node sits at the centre. The tree is not a full graph render — it is a focused, rooted subgraph scoped to the selected node and its neighbours up to a configurable depth.

---

## Edge direction convention

Every `GraphEdge` encodes: **source depends on target**.

```
source  →  target
  │
  └── "source imports / calls / extends target"
```

Given a selected node `S`:

| direction | query | result |
|---|---|---|
| find dependents (upstream in the tree, nodes that need S) | `edges where edge.target === S` | `edge.source` nodes |
| find dependencies (downstream in the tree, nodes S needs) | `edges where edge.source === S` | `edge.target` nodes |

Both directions can recurse to depth N. At depth 1 you get immediate neighbours. At depth ∞ you get the full transitive closure.

---

## Webview payload

For a selected node `S` at depth `D`, the backend should return:

```json
{
  "selected_node": GraphNode,
  "dependents":    GraphNode[],
  "dependencies":  GraphNode[],
  "edges":         GraphEdge[],
  "depth":         int
}
```

| field | source | notes |
|---|---|---|
| `selected_node` | `AnalysisResult.architecture.nodes` filtered by id | rendered as the root/centre node |
| `dependents` | nodes reachable by following `edge.target === S` upward | rendered above / to the left of root |
| `dependencies` | nodes reachable by following `edge.source === S` downward | rendered below / to the right of root |
| `edges` | `AnalysisResult.architecture.edges` filtered to only edges between visible nodes | used for drawing connectors and labelling relationship type |
| `depth` | query parameter | default 1, configurable |

All three node arrays contain full `GraphNode` objects (id, label, type, description). No extra fetch is needed for basic rendering.

---

## Node rendering

Each node in the tree has the following data available:

| visual element | data field | notes |
|---|---|---|
| label text | `GraphNode.label` | primary text in the node pill |
| node colour / shape | `GraphNode.type` | see colour map below |
| tooltip / sidebar | `GraphNode.description` | shown on hover or tap |
| click / drill-down key | `GraphNode.id` | selecting a node re-roots the tree at that node |
| file path subtitle | `ParsedFile.path` (via `id` join) | optional enrichment |
| language badge | `ParsedFile.language` (via `id` join) | optional enrichment |

### Node type colour map

| `NodeType` | suggested colour | rationale |
|---|---|---|
| `entry` | coral / red | entrypoints draw attention — many things depend on them |
| `service` | blue | core logic — the bulk of the graph |
| `util` | teal | shared helpers — appear deep in the dependency direction |
| `config` | amber | configuration — usually leaves in the dependency direction |
| `test` | gray | test files — appear only in the dependent direction, never the other |

---

## Edge rendering

Each edge between visible nodes has:

| visual element | data field | notes |
|---|---|---|
| arrow direction | `source → target` | always points from dependent to dependency |
| line style | `GraphEdge.relationship` | see style map below |
| edge label (optional) | `GraphEdge.relationship` | display only when space allows |
| highlight on hover | `source` and `target` ids | highlight both connected nodes |

### Edge relationship line style map

| `EdgeRelationship` | line style |
|---|---|
| `imports` | solid |
| `extends` | dashed |
| `calls` | dotted |

---

## Node enrichment (optional, depth-0 panel)

When the user selects a node and opens its detail panel, the following additional data is available by joining `GraphNode.id` to `ParsedFile.path`:

| panel section | data source |
|---|---|
| file path + language | `ParsedFile.path`, `ParsedFile.language` |
| classes defined | `ParsedFile.classes` → `ParsedClass[]` |
| functions defined | `ParsedFile.functions` → `ParsedFunction[]` |
| raw import list | `ParsedFile.imports` |
| code review findings | `CodeReviewFinding[]` where `file === node.id` |
| security issues | `SecurityIssue[]` where `file === node.id` |
| documentation | `DocEntry[]` where `function_name` starts with `node.id` |

All of this data is in the same `AnalysisResult` object returned by the job — no second API call needed.

---

## Traversal algorithm (pseudocode)

```
function buildSubgraph(nodeId, allNodes, allEdges, depth):
  visited = {nodeId}
  dependents = []
  dependencies = []
  queue = [(nodeId, 0)]

  while queue not empty:
    (current, d) = queue.pop()
    if d >= depth: continue

    for edge in allEdges:
      if edge.target === current and edge.source not in visited:
        visited.add(edge.source)
        dependents.append(getNode(edge.source))
        queue.append((edge.source, d + 1))

      if edge.source === current and edge.target not in visited:
        visited.add(edge.target)
        dependencies.append(getNode(edge.target))
        queue.append((edge.target, d + 1))

  return {
    selected_node: getNode(nodeId),
    dependents: dependents,
    dependencies: dependencies,
    edges: allEdges.filter(e => visited.has(e.source) and visited.has(e.target)),
    depth: depth
  }
```

---

## Re-rooting the tree

When the user taps a non-root node, the webview should call `buildSubgraph` with the tapped node's `id` as the new root. The full `allNodes` and `allEdges` arrays are already in memory from the initial `AnalysisResult` load — no new network request is needed for re-rooting.

---

## Data availability summary

| what the webview needs | where it comes from | requires extra fetch? |
|---|---|---|
| all nodes and edges | `AnalysisResult.architecture` | no — loaded once |
| subgraph for selected node | client-side traversal over above | no |
| node type for colour | `GraphNode.type` | no |
| edge style | `GraphEdge.relationship` | no |
| file path / language | `ParsedFile` via `id` join | no — in same payload |
| functions / classes in node | `ParsedFile.functions`, `.classes` | no |
| code issues for node | `CodeReview.findings` filtered by file | no |
| security issues for node | `SecurityReport.security` filtered by file | no |
| docs for node | `Documentation.docs` filtered by function_name prefix | no |

# RepoSense Webview

The UI rendered inside the RepoSense sidebar and full-editor panel. Loaded by [`SidebarProvider.ts`](../src/SidebarProvider.ts) — the provider reads `main.html` from disk, rewrites the `styles.css` and `main.js` references to webview URIs, then hands it to VS Code.

Plain HTML/CSS/JS, no bundler. The monolithic structure is deliberate so the extension can swap in webview URIs by string replacement.

---

## File Structure

```
webview/
├── main.html                        # Layout: tab bar, all five panels, state views
├── main.js                          # All rendering, message handling, D3 graph code
├── styles.css                       # VS Code-themed CSS using --vscode-* variables
│
├── sample-data.js                   # 9-node fixture for standalone testing
├── sample-data-complex.js           # 31-node, 68-edge fixture
├── test-dependency-tree.html        # Standalone harness — simple
├── test-complex-tree.html           # Standalone harness — complex
│
├── db_schema.md                     # Data model reference
├── graph_spec.md                    # Architecture graph specification
├── DEPENDENCY_TREE_IMPLEMENTATION.md
├── COMPLETE_GUIDE.md                # Feature reference
├── P4_P5_INTEGRATION_GUIDE.md       # Original handoff notes (historical)
├── ARCHITECTURE_ISSUES.md
├── TESTING_GUIDE.md
└── TODO
```

---

## Panels

Tab bar at the top switches between five panels rendered into the same `<main>` area:

| Panel | What it shows |
|---|---|
| **Score** | Animated circular ring (0 → final), grade badge (A/B/C/D/F), summary, top priorities |
| **Architecture** | D3 graph with two modes: **Network** (force-directed, all nodes) and **Tree** (selected node centered, dependents above, dependencies below, depth slider 1-5, click to re-root) |
| **Review** | Findings sorted by severity, filter buttons (ALL / HIGH+ / CRITICAL), expandable details |
| **Docs** | Two tabs — function documentation (params/returns/example) and unit test stubs |
| **Security** | Security issues with "Fix This First" highlight, then modernization items with effort badges |

Additional non-panel states: `idle` (no workspace), `loading` (with progress bar), `error` (with retry), `setup` (3-step wizard for entering watsonx credentials).

---

## Message Protocol

The webview talks to the extension via `vscode.postMessage` and `window.addEventListener('message', …)`.

### Extension → Webview

| `type` | Payload | Effect |
|---|---|---|
| `idle` | — | Show "No folder open" |
| `loading` | `{ step: string }` | Show loading state with step text |
| `progress` | `{ data: { percentage, step } }` | Update progress bar |
| `results` | `{ data: AnalysisResult }` | Render all panels, show Score by default |
| `error` | `{ message: string }` | Show error state with retry button |
| `setup` | — | Show 3-step credentials wizard |
| `complete` | `{ healthScore, grade, summary, result }` | Optional — also sent on completion |
| `status` | `{ message: string }` | Status text update |

### Webview → Extension

| `type` | Payload | Effect |
|---|---|---|
| `ready` | — | Sent on `DOMContentLoaded`; extension responds with `setup`/`results`/`idle` |
| `analyzeWorkspace` / `retry` | — | Force a fresh analysis |
| `openFullView` | — | Open the report in a full editor panel |
| `saveConfig` | `{ data: Record<string,string> }` | Save watsonx credentials from the wizard |

The `AnalysisResult` shape matches `backend/src/models.py` — see [`db_schema.md`](db_schema.md) for the full data model.

---

## Standalone Testing (No VS Code)

The `test-*.html` files run the graph code against the sample data fixtures, so you can iterate on the UI without launching the extension:

```bash
cd vscode-extension/webview
python3 -m http.server 8080
```

Then open:
- http://localhost:8080/test-dependency-tree.html (9 nodes)
- http://localhost:8080/test-complex-tree.html (31 nodes, 68 edges)

These harnesses skip the message protocol and call the render functions directly with the sample data.

---

## Styling

Uses VS Code CSS variables so the panel matches whatever theme the user has — `--vscode-sideBar-background`, `--vscode-foreground`, `--vscode-font-family`, etc. Accent colors for grades/severity are hardcoded.

CSP in `main.html` allows inline styles/scripts and the D3 CDN. D3.js v7 is loaded via `cdn.jsdelivr.net`.

---

*Part of RepoSense · IBM Bob Hackathon 2026*

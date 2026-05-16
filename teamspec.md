# RepoSense — Team Spec & Battle Plan
### IBM Bob Hackathon 2026 | 6 People | 24 Hours | VS Code Extension

---

## What We're Building

**RepoSense** — A VS Code extension that gives developers an instant AI-powered health report on any codebase, right inside their editor. Architecture map, code review, auto-documentation, and security hardening — without ever leaving VS Code.

**Tagline:** *Understand any codebase in minutes. Never leave your editor.*

---

## Why VS Code Extension Wins

- Developers live in VS Code. Results inside the editor = zero friction
- No browser. No tab switching. No setup for the user
- Judges see results appear *inline inside VS Code* — that's a product moment nobody else will have
- The hackathon theme is "turn idea into impact faster" — this is the most direct answer to that
- We control the demo machine — backend runs locally, extension connects to it, demo is flawless

---

## What It Does

```
Developer opens any project in VS Code
            ↓
Clicks the RepoSense icon in the sidebar
            ↓
Extension reads the current workspace
            ↓
Live progress panel: "Analyzing... Reviewing... Scoring..."
            ↓
Full health report appears in the sidebar:

  ┌─────────────────────────────┐
  │  RepoSense                  │
  │                             │
  │  Health Score               │
  │  ████████░░  74/100  B      │
  │                             │
  │  Top Priorities             │
  │  1. Add input validation    │
  │  2. Document 12 functions   │
  │  3. Update Werkzeug imports │
  │                             │
  │  Architecture    →          │
  │  Code Review     →          │
  │  Documentation   →          │
  │  Security        →          │
  └─────────────────────────────┘
```

Each section expands into a full webview panel with rich output.

---

## The Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Extension | TypeScript + VS Code Extension API | Native VS Code integration |
| UI Panels | Webview (HTML + CSS + JS + D3.js) | Rich interactive UI inside VS Code |
| Backend | Python FastAPI | Runs locally, handles all AI orchestration |
| AI Agents | IBM watsonx Orchestrate | 4 specialized agents |
| AI Inference | IBM watsonx.ai (Granite model) | Health scoring + plain-English reports |
| Dev Tool | IBM Bob IDE | Used to BUILD everything — sessions exported |
| Repo | GitHub (public) | Submission + bob_sessions folder |

---

## Four Core Features

```
1. UNDERSTAND   →  Architecture map — D3 module dependency graph in webview
2. REVIEW       →  AI code review — severity-rated findings list
3. DOCUMENT     →  Auto-generated docs + unit test stubs
4. HARDEN       →  Security vulnerabilities + modernization priorities
```

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│              VS Code Extension              │
│  (TypeScript — runs inside VS Code)         │
│                                             │
│  • Reads workspace path on activation       │
│  • Sends POST /analyze to local backend     │
│  • Polls GET /results/{job_id} every 3s     │
│  • Renders results in Webview panels        │
│  • Updates sidebar with live progress       │
└──────────────────┬──────────────────────────┘
                   │  HTTP (localhost:8000)
                   ▼
┌─────────────────────────────────────────────┐
│           FastAPI Backend (local)           │
│                                             │
│  POST /analyze                              │
│  • Read workspace files directly            │
│  • Parse file tree                          │
│  • Extract functions, classes, imports      │
│  • Chunk code by module                     │
│  • Return job_id immediately                │
│                                             │
│  GET /results/{job_id}                      │
│  • Return progress + results as they come   │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      watsonx Orchestrate — 4 Agents         │
│                                             │
│  Agent 1: ARCHITECT                         │
│  → file tree + import graph                 │
│  → nodes + edges JSON (for D3 graph)        │
│                                             │
│  Agent 2: REVIEWER                          │
│  → code chunks                              │
│  → findings[] with severity ratings         │
│                                             │
│  Agent 3: DOCUMENTER                        │
│  → functions + classes                      │
│  → markdown docs + unit test stubs          │
│                                             │
│  Agent 4: HARDENER                          │
│  → code + dependencies                      │
│  → security issues + modernization list     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         watsonx.ai — Granite Model          │
│                                             │
│  • Synthesizes all 4 agent outputs          │
│  • Overall health score /100                │
│  • Grade A–F                                │
│  • Plain-English 2-3 sentence summary       │
│  • Top 3 priorities to fix                  │
└─────────────────────────────────────────────┘
```

---

## Team Split

| Person | Role | Owns |
|--------|------|------|
| P1 | Backend Lead | FastAPI engine — file parsing, job queue, AI orchestration |
| P2 | Orchestrate Lead | All 4 watsonx Orchestrate agents |
| P3 | AI Lead | watsonx.ai Granite scoring + synthesis |
| P4 | Extension Lead | VS Code extension core — sidebar, activation, polling |
| P5 | Webview Lead | All webview panels — architecture graph, review, docs, security |
| P6 | Integration + Demo | Wiring everything together + Bob sessions + submission |

---

## P1 — Backend Lead

**Stack:** Python, FastAPI, AST parser

**Owns the engine that the extension calls.**

### Hour 0–4: Foundation
- [ ] Init FastAPI project
- [ ] `POST /analyze` — accepts `{ "local_path": string }`
- [ ] Walk file tree — list all `.py`, `.js`, `.ts`, `.java` files
- [ ] Return `{ "job_id": "abc123", "status": "processing" }` immediately
- [ ] In-memory job store (dict is fine for POC)
- [ ] CORS enabled — extension webview needs it

### Hour 4–10: Core Parsing
- [ ] AST chunker for Python — extract functions, classes, docstrings, imports
- [ ] Regex chunker for JS/TS — extract functions, classes, imports
- [ ] Import graph extractor — map which file imports which
- [ ] Build payload to send to Orchestrate
- [ ] `GET /results/{job_id}` — return progress + results

### Hour 10–18: Integration
- [ ] Wire parsed output → Orchestrate agents (P2 provides API details)
- [ ] Wire Orchestrate output → watsonx.ai scorer (P3 provides API details)
- [ ] Store final results per job_id
- [ ] Update progress steps in real time as each agent completes
- [ ] Test end-to-end with a real local Python repo

### Hour 18–22: Hardening
- [ ] Handle edge cases: empty folders, binary files, huge files (skip >500KB)
- [ ] Clean error responses for extension to display gracefully
- [ ] Confirm response schema matches API contract exactly

### Key Files
```
/backend
  main.py         ← FastAPI app, routes, CORS config
  parser.py       ← File walker, AST chunker, import extractor
  orchestrate.py  ← Orchestrate API client
  watsonx.py      ← watsonx.ai Granite client
  models.py       ← Pydantic request/response schemas
  jobs.py         ← In-memory job store + progress tracking
```

**Use Bob for:** AST parser, FastAPI scaffolding, Orchestrate client, Pydantic models, error handling

---

## P2 — Orchestrate Lead

**Stack:** IBM watsonx Orchestrate

**Owns all four AI agents. These are the intelligence of the product.**

### Hour 0–4: Setup
- [ ] Log into watsonx Orchestrate on hackathon IBM Cloud account
- [ ] Create 4 agent skeletons — name, description, blank instructions
- [ ] Test one inference call end-to-end
- [ ] Get Orchestrate API endpoint + credentials — share with P1 immediately

### Hour 4–10: Agent 1 + 2

**Agent 1 — ARCHITECT**
```
Name: RepoSense Architect
Model: granite-3-8b-instruct

Instructions:
You are a software architect analyzing a codebase.
Given a file tree and import relationships, identify the main
modules, their purpose, and how they connect to each other.

Output ONLY valid JSON. No markdown, no explanation:
{
  "nodes": [
    {
      "id": "string",
      "label": "filename.py",
      "type": "entry|service|util|config|test",
      "description": "one sentence description"
    }
  ],
  "edges": [
    {
      "source": "string",
      "target": "string",
      "relationship": "imports|extends|calls"
    }
  ]
}
```

**Agent 2 — REVIEWER**
```
Name: RepoSense Reviewer
Model: granite-3-8b-instruct

Instructions:
You are a senior code reviewer with 10 years experience.
Analyze the given code chunks and identify real, specific issues.
Focus on logic errors, missing validation, bad patterns.

Output ONLY valid JSON. No markdown, no explanation:
{
  "findings": [
    {
      "file": "string",
      "line": number,
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "issue": "specific description of the problem",
      "suggestion": "concrete fix suggestion"
    }
  ]
}
```

### Hour 10–16: Agent 3 + 4

**Agent 3 — DOCUMENTER**
```
Name: RepoSense Documenter
Model: granite-3-8b-instruct

Instructions:
You are a technical writer generating developer documentation.
Given functions and classes, write clear documentation and
unit test stubs covering the main cases.

Output ONLY valid JSON. No markdown, no explanation:
{
  "docs": [
    {
      "function_name": "string",
      "description": "string",
      "params": [{ "name": "string", "type": "string", "description": "string" }],
      "returns": "string",
      "example": "code example string"
    }
  ],
  "tests": [
    {
      "function_name": "string",
      "test_cases": [
        { "description": "string", "input": "string", "expected": "string" }
      ]
    }
  ]
}
```

**Agent 4 — HARDENER**
```
Name: RepoSense Hardener
Model: granite-3-8b-instruct

Instructions:
You are a security and modernization expert.
Find real security vulnerabilities and outdated code patterns.
Be specific — reference actual files and patterns found.

Output ONLY valid JSON. No markdown, no explanation:
{
  "security": [
    {
      "issue": "specific issue description",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "file": "string",
      "fix": "concrete fix description"
    }
  ],
  "modernization": [
    {
      "pattern": "what the outdated pattern is",
      "suggestion": "what to replace it with",
      "effort": "LOW|MEDIUM|HIGH"
    }
  ]
}
```

### Hour 16–22: Tuning
- [ ] Test each agent with real code chunks
- [ ] Tune prompts until JSON output is 100% consistent — no markdown leaking
- [ ] Document exact API call format for P1 to integrate
- [ ] Make sure all 4 return valid parseable JSON every single time

**Use Bob for:** Writing and refining agent prompts, testing configurations, generating Orchestrate API call code

---

## P3 — AI Lead (watsonx.ai)

**Stack:** IBM watsonx.ai, Granite model, Python

**Owns the health scoring and synthesis layer.**

### Hour 0–4: Setup
- [ ] Access watsonx.ai on hackathon IBM Cloud account
- [ ] Get Project ID + API key from Developer Access section
- [ ] Test first Granite model REST API call successfully
- [ ] Model to use: `granite-3-8b-instruct`

### Hour 4–10: Health Scoring Engine

**Scoring Prompt:**
```
You are a code quality analyst. Given analysis from four specialized
agents, produce an overall health scorecard for this codebase.

Architecture analysis: {architect_output}
Code review findings: {reviewer_output}
Documentation coverage: {documenter_output}
Security analysis: {hardener_output}

Score the codebase from 0 to 100:
- Code Quality (30 points): fewer HIGH/CRITICAL review findings = more points
- Security (30 points): fewer security issues = more points
- Documentation (20 points): better coverage = more points
- Architecture (20 points): cleaner, clearer structure = more points

Return ONLY valid JSON. No markdown, no explanation:
{
  "score": number,
  "grade": "A|B|C|D|F",
  "breakdown": {
    "quality": number,
    "security": number,
    "documentation": number,
    "architecture": number
  },
  "summary": "2-3 sentences describing this codebase honestly",
  "top_priorities": [
    "Most important thing to fix first",
    "Second most important",
    "Third most important"
  ]
}
```

### Hour 10–18: Integration
- [ ] Build internal `/score` logic that takes all 4 agent outputs
- [ ] Call Granite, parse JSON response, return scorecard
- [ ] Test with 3 real repos — calibrate that scores feel accurate
- [ ] Wire into P1's pipeline

### Hour 18–22: Polish
- [ ] Summaries must read as genuinely insightful — test and refine the prompt
- [ ] Add fallback if Granite call fails (return partial score with error note)
- [ ] Ensure response time is under 15 seconds

**Use Bob for:** Writing the scoring prompt, building the watsonx.ai Python client, fallback logic

---

## P4 — Extension Lead

**Stack:** TypeScript, VS Code Extension API

**Owns the VS Code extension core — the shell that holds everything together.**

### Hour 0–4: Setup
- [ ] `npm install -g yo generator-code` then `yo code`
- [ ] Select: New Extension (TypeScript)
- [ ] Set up extension manifest (`package.json`)
- [ ] Register sidebar activity bar icon + view container
- [ ] Confirm: extension loads in VS Code Extension Host (press F5)

```json
// package.json — contributes section
{
  "contributes": {
    "commands": [
      {
        "command": "reposense.analyze",
        "title": "RepoSense: Analyze Workspace"
      },
      {
        "command": "reposense.refresh",
        "title": "RepoSense: Refresh Analysis"
      }
    ],
    "viewsContainers": {
      "activitybar": [
        {
          "id": "reposense-sidebar",
          "title": "RepoSense",
          "icon": "$(pulse)"
        }
      ]
    },
    "views": {
      "reposense-sidebar": [
        {
          "type": "webview",
          "id": "reposense.mainPanel",
          "name": "Code Health"
        }
      ]
    }
  }
}
```

### Hour 4–10: Core Extension Logic

```typescript
// extension.ts
import * as vscode from 'vscode'

export function activate(context: vscode.ExtensionContext) {
  const provider = new RepoSenseViewProvider(context.extensionUri)

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('reposense.mainPanel', provider)
  )

  context.subscriptions.push(
    vscode.commands.registerCommand('reposense.analyze', () => {
      provider.startAnalysis()
    })
  )
}

class RepoSenseViewProvider implements vscode.WebviewViewProvider {
  private _view?: vscode.WebviewView

  constructor(private readonly _extensionUri: vscode.Uri) {}

  resolveWebviewView(webviewView: vscode.WebviewView) {
    this._view = webviewView
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri]
    }
    webviewView.webview.html = this.getLoadingHtml()
    this.startAnalysis()
  }

  async startAnalysis() {
    const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath
    if (!workspacePath) {
      this._view?.webview.postMessage({ type: 'error', message: 'No workspace open' })
      return
    }

    this._view?.webview.postMessage({ type: 'loading', step: 'Starting analysis...' })

    try {
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ local_path: workspacePath })
      })
      const { job_id } = await res.json()
      this.pollResults(job_id)
    } catch (e) {
      this._view?.webview.postMessage({
        type: 'error',
        message: 'Cannot connect to RepoSense backend. Is it running?'
      })
    }
  }

  private pollResults(jobId: string) {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/results/${jobId}`)
        const data = await res.json()

        this._view?.webview.postMessage({ type: 'progress', data: data.progress })

        if (data.status === 'complete') {
          clearInterval(interval)
          this._view?.webview.postMessage({ type: 'results', data: data.results })
        } else if (data.status === 'failed') {
          clearInterval(interval)
          this._view?.webview.postMessage({ type: 'error', message: 'Analysis failed' })
        }
      } catch (e) {
        clearInterval(interval)
      }
    }, 3000)
  }

  private getLoadingHtml(): string {
    return `<!DOCTYPE html>
    <html>
    <body style="background:#0a0e1a;color:#f9fafb;font-family:monospace;padding:16px;">
      <p>Initializing RepoSense...</p>
    </body>
    </html>`
  }
}

export function deactivate() {}
```

### Hour 10–18: Extension Polish
- [ ] Status bar item showing current analysis state
- [ ] Refresh button in sidebar title bar
- [ ] Handle workspace change — re-run analysis on folder switch
- [ ] Show notification when analysis completes: "RepoSense: Analysis complete — Score 74/100"
- [ ] "Open in browser" command if they want full web view later

### Hour 18–22: Final Extension Polish
- [ ] Package extension: `vsce package` → produces `.vsix`
- [ ] Test fresh install from `.vsix` on clean VS Code
- [ ] Error messages are friendly and actionable
- [ ] Extension activates instantly with no lag

**Use Bob for:** Extension boilerplate, TypeScript types, polling logic, VS Code API usage, error handling

---

## P5 — Webview Lead

**Stack:** HTML, CSS, JavaScript, D3.js (inside VS Code webview)

**Owns all the UI panels that render inside the extension.**

### What Is a Webview?
A VS Code webview is an iframe inside VS Code. P4's extension injects HTML into it. P5 writes that HTML — it's a regular web page but styled to look native inside VS Code. It listens for `postMessage` events from the extension and renders results.

### Design Direction
Match VS Code's dark theme exactly. Use VS Code CSS variables so it looks native.

```css
/* VS Code native CSS variables — use these */
body {
  background-color: var(--vscode-sideBar-background);
  color: var(--vscode-foreground);
  font-family: var(--vscode-font-family);
  font-size: var(--vscode-font-size);
}

/* Custom accents */
--rs-blue:   #3b82f6;
--rs-green:  #10b981;
--rs-amber:  #f59e0b;
--rs-red:    #ef4444;
--rs-purple: #8b5cf6;
```

### Hour 0–4: Setup
- [ ] Create `/webview/` folder in extension project
- [ ] Build `main.html` — the base webview HTML file
- [ ] Set up message listener:
  ```javascript
  const vscode = acquireVsCodeApi()
  window.addEventListener('message', event => {
    const msg = event.data
    if (msg.type === 'loading') showLoading(msg.step)
    if (msg.type === 'progress') updateProgress(msg.data)
    if (msg.type === 'results') showResults(msg.data)
    if (msg.type === 'error') showError(msg.message)
  })
  ```
- [ ] Build loading state — animated pulse, step names ticking through
- [ ] Build error state — clear message, retry button

### Hour 4–10: Health Score Panel (The Hero)

This is the first thing users see. Make it stunning.

```html
<!-- Health Score Card -->
<div class="score-card">
  <div class="score-ring">
    <!-- SVG circular progress ring -->
    <svg viewBox="0 0 100 100">
      <circle class="ring-bg" cx="50" cy="50" r="40"/>
      <circle class="ring-fill" cx="50" cy="50" r="40"
              stroke-dasharray="251"
              stroke-dashoffset="calc(251 - (251 * var(--score)) / 100)"/>
    </svg>
    <div class="score-number" id="scoreNum">0</div>
  </div>
  <div class="grade-badge" id="gradeBadge">B</div>
  <p class="summary" id="summary"></p>
  <div class="priorities">
    <h4>Top Priorities</h4>
    <ol id="priorityList"></ol>
  </div>
</div>
```

- [ ] Score number animates from 0 to final value on load
- [ ] Circular SVG ring fills to match score
- [ ] Grade badge colour: A=green, B=blue, C=amber, D/F=red
- [ ] Summary text fades in after score animation

### Hour 4–10: Architecture Graph Panel

The visual centrepiece. D3 force-directed graph inside a webview.

- [ ] D3.js loaded via CDN in webview HTML
- [ ] Force-directed graph with nodes and edges
- [ ] Node colours by type:
  ```
  entry   → #3b82f6  blue
  service → #8b5cf6  purple
  util    → #10b981  green
  config  → #f59e0b  amber
  test    → #6b7280  grey
  ```
- [ ] Zoom + pan enabled
- [ ] Click a node → shows module description in a tooltip
- [ ] Nodes animate in with spring physics on load

### Hour 10–16: Review + Docs + Security Panels

**Code Review Panel:**
- [ ] Findings sorted by severity — CRITICAL first
- [ ] Severity badge per finding: red/orange/yellow/blue
- [ ] File name + line number
- [ ] Expandable: click to see full issue + suggestion
- [ ] Filter buttons: ALL / HIGH+ / CRITICAL

**Documentation Panel:**
- [ ] Two tabs: Docs / Tests
- [ ] Each function shown with description, params, return, example
- [ ] Code blocks with monospace styling + copy button
- [ ] Test stubs displayed as copyable code

**Security Panel:**
- [ ] Two sections: Security Issues / Modernization
- [ ] Top item highlighted: "Fix This First"
- [ ] Effort badges: LOW/MED/HIGH
- [ ] Priority-ordered list

### Hour 16–18: Navigation
- [ ] Tab bar at top of webview: Score | Architecture | Review | Docs | Security
- [ ] Smooth panel transitions
- [ ] Active tab highlighted
- [ ] Tab shows badge count for findings (e.g. "Review (7)")

### Hour 18–22: Polish
- [ ] Skeleton loading states per panel while analysis runs
- [ ] All panels look great with both small and large datasets
- [ ] Empty state messages: "No security issues found 🎉"
- [ ] Everything feels fast and native inside VS Code

**Use Bob for:** Webview HTML/CSS structure, D3 graph component, score ring animation, panel tab navigation

---

## P6 — Integration + Demo + Submission

**Stack:** Everything a bit — glue code, testing, demo, Bob sessions

**This role is the most critical for actually winning.**

### Hour 0–4: Setup
- [ ] Create GitHub repo: `reposense-ibm-hackathon` (public)
- [ ] Create `bob_sessions/` folder immediately
- [ ] Set up project structure:
  ```
  /reposense-ibm-hackathon
    /backend          ← P1's FastAPI
    /vscode-extension ← P4 + P5's extension
    /bob_sessions     ← All session exports
    README.md
    .env.example
    DEMO_SCRIPT.md
  ```
- [ ] Set up `.env.example`:
  ```
  WATSONX_API_KEY=your_key_here
  WATSONX_PROJECT_ID=your_project_id_here
  WATSONX_URL=https://us-south.ml.cloud.ibm.com
  ORCHESTRATE_API_KEY=your_key_here
  ORCHESTRATE_URL=your_orchestrate_url_here
  ```
- [ ] Start using Bob IDE from minute one — export every session

### Hour 4–10: Integration
- [ ] Confirm P4's extension can POST to P1's backend
- [ ] Confirm polling works — progress steps update in webview
- [ ] Confirm results flow through to P5's webview panels
- [ ] Test full pipeline with a small real local Python project
- [ ] Document any blockers and help unblock them

### Hour 10–18: End-to-End Testing
- [ ] Clone `pallets/flask` locally
- [ ] Run full pipeline — all 4 agents — through extension
- [ ] Every panel shows real data
- [ ] Test with a JS project too (different language)
- [ ] Fix everything that breaks
- [ ] Keep exporting Bob sessions throughout

### Hour 18–22: Demo Prep
- [ ] Run full pipeline 3 times on `pallets/flask`
- [ ] Pick the cleanest run — note the score and key findings
- [ ] Record 2-minute demo video (script below)
- [ ] Take screenshots of every panel for README
- [ ] Write the README (template below)

### Hour 22–24: Submission
- [ ] Collect Bob session exports from ALL 6 team members
- [ ] Screenshot every session consumption summary
- [ ] Upload all to `bob_sessions/`:
  ```
  bob_sessions/
    P1_parser_session.md
    P1_parser_screenshot.png
    P2_agents_session.md
    P2_agents_screenshot.png
    P3_scoring_session.md
    P3_scoring_screenshot.png
    P4_extension_session.md
    P4_extension_screenshot.png
    P5_webview_session.md
    P5_webview_screenshot.png
    P6_integration_session.md
    P6_integration_screenshot.png
  ```
- [ ] Final submit on lablab.ai before **May 17, 2026 — 8:00 AM PDT**

**Use Bob for:** Integration scripts, README writing, debugging help, test scripts

---

## API Contract — Locked at Hour 4

Everyone builds against this. Do not change after hour 4.

### POST `/analyze`
```json
Request:
{ "local_path": "/Users/dev/flask" }

Response:
{ "job_id": "abc-123-def", "status": "processing" }
```

### GET `/results/{job_id}`
```json
{
  "status": "processing|complete|failed",
  "progress": {
    "steps": [
      { "name": "Reading workspace files", "status": "done|active|pending" },
      { "name": "Parsing code structure", "status": "done|active|pending" },
      { "name": "Architect agent", "status": "done|active|pending" },
      { "name": "Reviewer agent", "status": "done|active|pending" },
      { "name": "Documenter agent", "status": "done|active|pending" },
      { "name": "Hardener agent", "status": "done|active|pending" },
      { "name": "Generating health score", "status": "done|active|pending" }
    ]
  },
  "results": {
    "score": 74,
    "grade": "B",
    "breakdown": {
      "quality": 22,
      "security": 20,
      "documentation": 16,
      "architecture": 16
    },
    "summary": "Flask is a well-structured micro-framework with clear separation of concerns. Input validation is inconsistent across route handlers. Documentation coverage is below industry standard for a public library.",
    "top_priorities": [
      "Add input validation to 3 route handlers in app.py",
      "Document 12 undocumented public functions",
      "Update deprecated Werkzeug import patterns"
    ],
    "architecture": {
      "nodes": [
        { "id": "app", "label": "app.py", "type": "entry", "description": "Main application factory and entry point" },
        { "id": "routing", "label": "routing.py", "type": "service", "description": "URL routing and endpoint registration" }
      ],
      "edges": [
        { "source": "app", "target": "routing", "relationship": "imports" }
      ]
    },
    "review": {
      "findings": [
        {
          "file": "app.py",
          "line": 47,
          "severity": "HIGH",
          "issue": "No input validation on user-supplied request data",
          "suggestion": "Add validation using request.args.get() with type checking"
        }
      ]
    },
    "docs": {
      "docs": [
        {
          "function_name": "create_app",
          "description": "Application factory function that creates and configures the Flask instance",
          "params": [{ "name": "config", "type": "dict", "description": "Configuration dictionary" }],
          "returns": "Flask application instance",
          "example": "app = create_app({'DEBUG': True})"
        }
      ],
      "tests": [
        {
          "function_name": "create_app",
          "test_cases": [
            { "description": "Creates app with default config", "input": "None", "expected": "Flask instance" },
            { "description": "Creates app with custom config", "input": "{'DEBUG': True}", "expected": "Flask instance with debug mode" }
          ]
        }
      ]
    },
    "security": {
      "security": [
        {
          "issue": "Secret key hardcoded in source",
          "severity": "CRITICAL",
          "file": "config.py",
          "fix": "Move to environment variable: os.environ.get('SECRET_KEY')"
        }
      ],
      "modernization": [
        {
          "pattern": "Deprecated Werkzeug import path used",
          "suggestion": "Update to werkzeug.utils for forward compatibility",
          "effort": "LOW"
        }
      ]
    }
  }
}
```

---

## Bob IDE Rules — All 6 People

Non-negotiable. Judges check the `bob_sessions` exports carefully.

**Every person must:**
- Use Bob IDE to generate their code — actually build through Bob
- Export task session report after every meaningful task
- Screenshot the session consumption summary
- Name exports clearly: `P1_ast_parser.md`, `P5_d3_graph.md`

**Recommended Bob prompts per person:**

| Person | Bob prompts to use |
|--------|-------------------|
| P1 | "Write a Python AST parser that extracts all function names, parameters, and docstrings from .py files and returns structured JSON" |
| P1 | "Create a FastAPI endpoint that accepts a local_path, walks the file tree, and returns a job_id" |
| P2 | "Help me write a watsonx Orchestrate agent prompt that outputs strict JSON representing code architecture as nodes and edges" |
| P3 | "Write a Python REST client for IBM watsonx.ai that calls the Granite model with retry logic and error handling" |
| P4 | "Write a VS Code extension in TypeScript that registers a webview sidebar, reads the workspace path, and polls a REST API every 3 seconds" |
| P5 | "Generate an HTML/CSS/JS webview for a VS Code extension that displays a health score ring animation and a D3 force-directed graph" |
| P6 | "Write an integration test script that sends a POST to a FastAPI endpoint and polls until complete, printing progress" |

---

## Demo Script — 2 Minutes

**Project to analyze:** Clone `pallets/flask` locally before the demo

```
0:00–0:20  The Problem
  "Every developer knows this feeling — you open an unfamiliar codebase
   and spend hours just figuring out where things are, what's broken,
   what's risky. RepoSense fixes that. Right inside VS Code."

0:20–1:10  Live Demo
  • Open VS Code with flask project in workspace
  • Click the RepoSense icon in the activity bar
  • Sidebar panel appears — "Analyzing your workspace..."
  • Live progress ticks through:
      ✓ Reading workspace files
      ✓ Parsing code structure
      ⟳ Architect agent running...
      ✓ Architect agent complete
      ⟳ Reviewer agent running...
      ... etc
  • Health score ring fills to 74/100 — Grade B
  • Score number counts up from 0
  • Summary text fades in
  • Top 3 priorities appear

1:10–1:40  Explore Panels
  • Click Architecture tab — D3 graph springs to life
  • Zoom in, click a node — module description appears
  • Click Review tab — HIGH severity findings with file + line
  • Click Security tab — CRITICAL issue at top: "hardcoded secret key"
  • "All of this, without leaving VS Code. No browser. No context switch."

1:40–2:00  Close
  • "Built with IBM Bob. Powered by watsonx Orchestrate and watsonx.ai."
  • "RepoSense — understand any codebase in minutes."
```

**Practise this twice before recording.**

---

## README Template

```markdown
# RepoSense
> AI-powered codebase health analysis, right inside VS Code.

Built with IBM Bob | Powered by IBM watsonx Orchestrate + watsonx.ai

## The Problem
Developers waste hours understanding unfamiliar codebases — where
things live, what's broken, what's risky. RepoSense fixes that
without you ever leaving your editor.

## What It Does
Open any project in VS Code. Click the RepoSense icon.
Get a complete health report in minutes:

- **Architecture Map** — visual D3 module dependency graph
- **Code Review** — AI-detected issues with severity ratings
- **Documentation** — auto-generated docs + unit test stubs
- **Security** — vulnerabilities and modernization priorities
- **Health Score** — overall codebase score out of 100

## Tech Stack
- VS Code Extension: TypeScript + VS Code Extension API
- UI: Webview (HTML + CSS + D3.js)
- Backend: Python FastAPI (runs locally)
- AI Agents: IBM watsonx Orchestrate (4 agents)
- AI Inference: IBM watsonx.ai (Granite model)
- Built using: IBM Bob IDE

## Running Locally

### 1. Start the backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # fill in your watsonx credentials
uvicorn main:app --reload

### 2. Install and run the extension
cd vscode-extension
npm install
# Press F5 in VS Code to launch Extension Development Host
# Open any project folder
# Click the RepoSense icon in the sidebar

## IBM Bob Usage
See bob_sessions/ for all task session exports showing IBM Bob
was used throughout the entire development process.

## Team
[Your names here]
```

---

## Hour-by-Hour Summary

| Hours | Milestone |
|-------|-----------|
| 0–4 | Repo live. Backend skeleton running and returning fake data. Extension loads in VS Code. Webview renders basic HTML. All 4 agent skeletons in Orchestrate. |
| 4–10 | Backend parsing real files. Agents 1+2 producing real JSON. D3 graph renders in webview. Health score card animates. Polling works end-to-end. |
| 10–18 | Full pipeline working. All 4 agents + scorer. All 5 panels showing real data. Integration tested with Flask repo. |
| 18–22 | Polish everything. Demo run 3 times. Video recorded. README written. |
| 22–24 | Bob sessions collected from all 6 people. Submitted on lablab.ai. |

---

## If Things Break — Cut Priority

**Never cut:**
- Health score card with animated number
- Architecture graph — this is what judges remember
- At least 2 of 4 agents producing output

**Cut first if needed:**
- Docs panel → drop Agent 3, show placeholder
- Modernization section → simplify Hardener to security only

**Cut second if needed:**
- D3 graph → replace with simple indented file tree
- Live progress steps → replace with single spinner

**Never ever cut:**
- The extension working end-to-end
- The health score
- The code review findings

---

## Submission Checklist

- [ ] GitHub repo is public
- [ ] `bob_sessions/` has exports + screenshots from all 6 people
- [ ] Extension installs and runs from the repo
- [ ] Backend runs with `uvicorn main:app`
- [ ] README has screenshots of every panel
- [ ] Demo video is 2 minutes max
- [ ] No API keys in the repo — `.env.example` only
- [ ] Submitted on lablab.ai before **May 17, 2026 — 8:00 AM PDT**

---

*RepoSense — Understand any codebase in minutes. Never leave your editor.*
*Built with IBM Bob. Powered by IBM watsonx Orchestrate + watsonx.ai.*
# RepoSense — Full Team Spec & Battle Plan
### IBM Bob Hackathon 2026 | 6 People | 24 Hours | Built to Win

---

## What We're Building

**RepoSense** — Drop any GitHub repo URL. Get a complete AI-powered codebase health report in minutes. Architecture map, code review, auto-documentation, security hardening — all in one beautiful dashboard.

**Tagline:** *From repo to insight in minutes.*

---

## The Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14 + Tailwind + shadcn/ui | Fast, beautiful, production-grade |
| Backend | Python FastAPI | Async, fast, easy to wire to AI |
| AI Agents | IBM watsonx Orchestrate | 4 specialized agents, orchestrated |
| AI Inference | IBM watsonx.ai (Granite model) | Health scoring + plain-English reports |
| Visualization | D3.js | Architecture graph — the visual centrepiece |
| Dev Tool | IBM Bob IDE | Used to BUILD everything — sessions exported |
| Repo | GitHub (public) | Submission + bob_sessions folder |

---

## Four Core Features

```
1. UNDERSTAND   →  Architecture map — visual module dependency graph
2. REVIEW       →  AI code review — issues, risks, severity ratings
3. DOCUMENT     →  Auto-generated docs + unit test suites
4. HARDEN       →  Security vulnerabilities + modernization priorities
```

**One repo in. One complete health dashboard out.**

---

## System Architecture

```
[User pastes GitHub URL on frontend]
            ↓
[FastAPI Backend — /analyze endpoint]
  • git clone repo
  • parse file tree
  • extract functions, classes, imports
  • chunk code by module
            ↓
[watsonx Orchestrate — 4 Agents in sequence]
  │
  ├── Agent 1: ARCHITECT
  │     Input:  file tree + import graph
  │     Output: nodes + edges JSON for D3 graph
  │
  ├── Agent 2: REVIEWER
  │     Input:  code chunks
  │     Output: findings[] with severity LOW/MED/HIGH
  │
  ├── Agent 3: DOCUMENTER
  │     Input:  functions + classes
  │     Output: markdown docs + test file stubs
  │
  └── Agent 4: HARDENER
        Input:  code chunks + dependencies
        Output: security issues + modernization list
            ↓
[watsonx.ai — IBM Granite model]
  • Synthesizes all 4 agent outputs
  • Generates plain-English summary
  • Produces overall health score /100
            ↓
[Next.js Dashboard — 5 panels]
  ├── Health Score Card       (animated number, colour coded)
  ├── Architecture Graph      (D3, zoomable, clickable nodes)
  ├── Code Review Panel       (severity-badged findings list)
  ├── Documentation Viewer    (syntax-highlighted markdown)
  └── Security Report         (priority-ordered fix list)
```

---

## Team Split — Who Owns What

---

### P1 — Backend Lead

**Stack:** Python, FastAPI, git, file parsing

**Owns everything the server does.**

**Hour 0–4: Foundation**
- [ ] Init FastAPI project
- [ ] POST `/analyze` endpoint — accepts `{ repo_url: string }`
- [ ] git clone logic (use `gitpython` or subprocess)
- [ ] File tree walker — list all `.py`, `.js`, `.ts`, `.java` files
- [ ] Basic file reader — extract raw content per file

**Hour 4–10: Core Build**
- [ ] Smart chunker — split code by function/class/module (use AST for Python, regex for JS/TS)
- [ ] Import graph extractor — map which file imports which
- [ ] Build payload structure to send to Orchestrate
- [ ] GET `/results/{job_id}` endpoint for polling
- [ ] Basic job queue (in-memory dict is fine for POC)

**Hour 10–18: Integration**
- [ ] Wire chunker output → Orchestrate API call
- [ ] Handle Orchestrate response and store results
- [ ] Test with Flask repo, then Express repo
- [ ] Add timeout handling and error responses

**Hour 18–22: Hardening**
- [ ] Edge cases: private repos, empty repos, huge files
- [ ] Make sure diverse language repos work (Python + JS minimum)
- [ ] Clean up response schema so frontend can consume it easily

**Key files:**
```
/backend
  main.py           ← FastAPI app + routes
  parser.py         ← File tree + chunker
  orchestrate.py    ← Orchestrate API client
  watsonx.py        ← watsonx.ai client
  models.py         ← Pydantic schemas
```

**Use Bob for:** Generating the AST parser, writing the chunking logic, building the Orchestrate client, writing error handlers

---

### P2 — Orchestrate Lead

**Stack:** IBM watsonx Orchestrate, prompt engineering

**Owns all four AI agents.**

**Hour 0–4: Foundation**
- [ ] Log into watsonx Orchestrate (hackathon cloud account)
- [ ] Create 4 agent skeletons — name, description, blank instructions
- [ ] Test one simple inference call end-to-end
- [ ] Understand how to call agents via the Orchestrate API

**Hour 4–10: Build Agent 1 + 2**

**Agent 1 — ARCHITECT**
```
System prompt:
"You are a software architect. Given a file tree and import 
relationships, identify the main modules, their purpose, 
and how they connect. Output ONLY valid JSON:
{
  nodes: [{ id, label, type, description }],
  edges: [{ source, target, relationship }]
}"
```

**Agent 2 — REVIEWER**
```
System prompt:
"You are a senior code reviewer. Analyze the given code chunks 
and identify issues. Output ONLY valid JSON:
{
  findings: [{
    file, line, severity (LOW|MEDIUM|HIGH|CRITICAL),
    issue, suggestion
  }]
}"
```

**Hour 10–16: Build Agent 3 + 4**

**Agent 3 — DOCUMENTER**
```
System prompt:
"You are a technical writer. Generate documentation and unit 
test stubs for the given functions and classes. Output:
{
  docs: [{ function_name, description, params, returns, example }],
  tests: [{ function_name, test_cases: [{ input, expected }] }]
}"
```

**Agent 4 — HARDENER**
```
System prompt:
"You are a security and modernization expert. Analyze the code 
for security vulnerabilities and outdated patterns. Output:
{
  security: [{ issue, severity, file, fix }],
  modernization: [{ pattern, suggestion, effort (LOW|MED|HIGH) }]
}"
```

**Hour 16–22: Tuning**
- [ ] Test each agent with real repo chunks
- [ ] Tune prompts until output is consistently valid JSON
- [ ] Make sure agent chaining works (output of 1 feeds into scorer)
- [ ] Document the API call format for P1 to integrate

**Use Bob for:** Writing and refining agent prompts, testing agent configurations, generating the API integration code

---

### P3 — AI Lead (watsonx.ai)

**Stack:** IBM watsonx.ai, Granite model, Python

**Owns the health scoring and synthesis layer.**

**Hour 0–4: Setup**
- [ ] Access watsonx.ai on hackathon cloud account
- [ ] Get Project ID + API key (from Developer Access section)
- [ ] Test first Granite model inference call via API
- [ ] Choose model: `granite-3-8b-instruct` (fast, good for code)

**Hour 4–10: Build Scoring Engine**

**Health Score Prompt:**
```
Given these analysis results from a codebase:
- Architecture findings: {architect_output}
- Code review findings: {reviewer_output}  
- Security findings: {hardener_output}

Calculate a health score from 0-100 based on:
- Code quality (30 points): based on review findings severity
- Security (30 points): based on security issues found
- Documentation (20 points): based on doc coverage
- Architecture (20 points): based on complexity and structure

Return ONLY JSON:
{
  score: number,
  grade: "A"|"B"|"C"|"D"|"F",
  breakdown: { quality, security, documentation, architecture },
  summary: "2-3 sentence plain English overview",
  top_priorities: ["string x3 — most important things to fix"]
}
```

**Hour 10–18: Integration**
- [ ] Wire scoring endpoint to receive Orchestrate outputs
- [ ] Return structured scorecard to backend
- [ ] Test with 3 different repos — calibrate scoring

**Hour 18–22: Polish**
- [ ] Make sure summaries are genuinely useful, not generic
- [ ] Add model fallback if primary call fails
- [ ] Ensure response time is under 15 seconds

**Use Bob for:** Writing the scoring prompts, building the watsonx.ai API client, generating the synthesis logic

---

### P4 — Frontend Lead

**Stack:** Next.js 14, Tailwind CSS, shadcn/ui, D3.js

**Owns the entire UI shell and the architecture graph.**

**Design Direction:** Dark theme. Deep navy/slate background. Electric blue and amber accents. Monospace font for code elements. Clean, data-dense, premium developer tool aesthetic. Think Linear meets Datadog.

**Hour 0–4: Foundation**
- [ ] `npx create-next-app@latest reposense` with TypeScript + Tailwind
- [ ] Install shadcn/ui, D3.js, framer-motion, react-syntax-highlighter
- [ ] Set up colour tokens in `tailwind.config.ts`
- [ ] Build the homepage — URL input, hero, submit button
- [ ] Set up routing: `/` (home) → `/report/[id]` (dashboard)

**Colour tokens:**
```css
--bg-base: #0a0e1a
--bg-surface: #111827
--bg-elevated: #1f2937
--accent-blue: #3b82f6
--accent-amber: #f59e0b
--accent-green: #10b981
--accent-red: #ef4444
--text-primary: #f9fafb
--text-secondary: #9ca3af
```

**Hour 4–10: Architecture Graph**

This is the visual centrepiece. Spend real time here.

- [ ] D3 force-directed graph component
- [ ] Nodes: colour coded by type (entry/service/util/config)
- [ ] Edges: directional arrows showing import flow
- [ ] Zoom + pan enabled
- [ ] Click a node → side panel shows module info
- [ ] Animated on load — nodes spring into position

```tsx
// Node colour mapping
const nodeColors = {
  entry: '#3b82f6',      // blue — entry points
  service: '#8b5cf6',    // purple — services
  util: '#10b981',       // green — utilities
  config: '#f59e0b',     // amber — config files
  test: '#6b7280',       // grey — test files
}
```

**Hour 10–18: Dashboard Shell**
- [ ] 5-panel dashboard layout
- [ ] Health score card with animated count-up number
- [ ] Grade badge (A/B/C/D/F) with appropriate colour
- [ ] Top priorities section
- [ ] Loading state — live progress log (not just a spinner)
- [ ] Error state — graceful failure UI

**Hour 18–22: Polish**
- [ ] Smooth page transitions
- [ ] Skeleton loading states for each panel
- [ ] Mobile-responsive layout
- [ ] Make the health score number animate from 0 on load

**Key components:**
```
/components
  ArchitectureGraph.tsx   ← D3 graph
  HealthScoreCard.tsx     ← Animated score + grade
  ReviewPanel.tsx         ← Findings list
  DocsViewer.tsx          ← Syntax-highlighted docs
  SecurityReport.tsx      ← Priority fix list
  ProgressLog.tsx         ← Live pipeline status
  RepoInput.tsx           ← Homepage input form
```

**Use Bob for:** Generating the D3 graph component, writing the animation logic, building the dashboard layout

---

### P5 — Frontend Support

**Stack:** Next.js, Tailwind, shadcn/ui

**Owns three of the five dashboard panels.**

**Hour 0–4: Setup**
- [ ] Pull P4's repo once initialized
- [ ] Set up local dev environment
- [ ] Build the Code Review Panel component (empty but structured)
- [ ] Build the Docs Viewer component (empty but structured)
- [ ] Build the Security Report component (empty but structured)

**Hour 4–10: Panel Build**

**Code Review Panel:**
- [ ] Findings list sorted by severity (CRITICAL first)
- [ ] Severity badges: red/orange/yellow/blue
- [ ] File + line number for each finding
- [ ] Expandable detail for each finding
- [ ] Filter by severity

**Docs Viewer:**
- [ ] Tab-switcher: Documentation / Tests
- [ ] Syntax-highlighted code blocks (react-syntax-highlighter)
- [ ] Copy-to-clipboard button on each block
- [ ] Function name headers with description

**Security Report:**
- [ ] Two sections: Security Issues + Modernization
- [ ] Effort badges: LOW/MED/HIGH
- [ ] Priority ordered list
- [ ] "Fix this first" highlight on top item

**Hour 10–18: Wire to API**
- [ ] Connect each panel to receive real data from P6's API integration
- [ ] Handle loading states per panel
- [ ] Handle empty states (no findings = good news message)

**Hour 18–22: Polish**
- [ ] Consistent spacing and typography across all panels
- [ ] Hover states on all interactive elements
- [ ] Make sure panels look good with both small and large datasets

**Use Bob for:** Generating panel components, writing filter logic, building the copy-to-clipboard functionality

---

### P6 — Integration Lead + Demo

**Stack:** Everything a bit, focused on glue code and submission

**Owns: connecting all the pieces, demo, Bob sessions, submission**

**This is the most critical role for actually winning.**

**Hour 0–4: Setup**
- [ ] Create GitHub repo: `reposense-ibm-hackathon`
- [ ] Create `bob_sessions/` folder immediately
- [ ] Set up `.env.example` with all required keys
- [ ] Create initial README structure
- [ ] Start using Bob IDE — export every single session from day one

**Hour 4–10: API Integration**
- [ ] Build the frontend API client (`/lib/api.ts`)
- [ ] Connect homepage form → POST `/analyze`
- [ ] Implement polling logic → GET `/results/{id}` every 3 seconds
- [ ] Feed results into each panel component as data arrives
- [ ] Build the live progress log (show pipeline steps as they complete)

```typescript
// Polling logic
const pollResults = async (jobId: string) => {
  const interval = setInterval(async () => {
    const res = await fetch(`/api/results/${jobId}`)
    const data = await res.json()
    if (data.status === 'complete') {
      clearInterval(interval)
      setResults(data)
    }
    setProgress(data.progress) // update live log
  }, 3000)
}
```

**Hour 10–18: End-to-End Testing**
- [ ] Test full pipeline with `pallets/flask` repo
- [ ] Test with `expressjs/express` repo
- [ ] Test with a small unknown repo (edge case)
- [ ] Log and fix every broken thing
- [ ] Make sure Bob sessions are being exported throughout

**Hour 18–22: Demo Prep**
- [ ] Pick the best demo repo — **`pallets/flask`** recommended
- [ ] Run full pipeline 3 times — screenshot best output
- [ ] Record 2-minute demo video:
  - 0:00–0:20 — problem statement (devs waste hours understanding repos)
  - 0:20–1:00 — live demo (paste URL, watch pipeline, show dashboard)
  - 1:00–1:40 — show each panel with real output
  - 1:40–2:00 — health score reveal, close with tagline
- [ ] Write final README

**Hour 22–24: Submission**
- [ ] Export ALL Bob task sessions from all team members
- [ ] Screenshot every session consumption summary
- [ ] Upload all to `bob_sessions/` folder
- [ ] Final README with:
  - What it does (2 sentences)
  - How to run it locally
  - Tech stack
  - Screenshots
  - Team
- [ ] Submit on lablab.ai before deadline

**Use Bob for:** Writing the API client, building the polling logic, generating the README, helping debug integration issues

---

## Bob IDE — Rules for All 6 People

This is non-negotiable. Judges check the bob_sessions exports.

**Every person must:**
- Use Bob IDE to write code — not just chat with it, actually generate code through it
- Export task session report after every meaningful task
- Screenshot the session consumption summary
- Save everything to `bob_sessions/` with naming: `P1_parser_task.md`, `P2_agent1_task.md` etc.

**Good Bob tasks to run:**
- "Help me write a Python AST parser that extracts all function names and docstrings"
- "Generate a D3 force-directed graph React component with zoom and pan"
- "Write a watsonx.ai API client in Python that calls the Granite model"
- "Create a FastAPI endpoint that accepts a GitHub URL and returns a job ID"
- "Write unit tests for the file chunker module"

---

## API Contract — The Single Most Important Document

P1 (backend) and P4/P5/P6 (frontend) must agree on this before hour 4.

**POST `/analyze`**
```json
Request:  { "repo_url": "https://github.com/pallets/flask" }
Response: { "job_id": "abc123", "status": "processing" }
```

**GET `/results/{job_id}`**
```json
Response: {
  "status": "processing|complete|failed",
  "progress": {
    "steps": [
      { "name": "Cloning repo", "status": "done" },
      { "name": "Parsing files", "status": "done" },
      { "name": "Running Architect agent", "status": "active" },
      { "name": "Running Reviewer agent", "status": "pending" },
      { "name": "Running Documenter agent", "status": "pending" },
      { "name": "Running Hardener agent", "status": "pending" },
      { "name": "Generating health score", "status": "pending" }
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
    "summary": "Flask is a well-structured micro-framework...",
    "top_priorities": [
      "Add input validation to route handlers",
      "Document 12 undocumented public functions",
      "Update deprecated Werkzeug patterns"
    ],
    "architecture": {
      "nodes": [...],
      "edges": [...]
    },
    "review": {
      "findings": [...]
    },
    "docs": {
      "docs": [...],
      "tests": [...]
    },
    "security": {
      "security": [...],
      "modernization": [...]
    }
  }
}
```

**Everyone builds against this contract. P1 implements it. Everyone else consumes it.**

---

## The Demo — Exactly What to Show

**Repo to use:** `https://github.com/pallets/flask`

**Demo flow:**
1. Open RepoSense homepage — clean, dark, impressive
2. Paste the Flask GitHub URL
3. Hit Analyze — live progress log starts updating
4. Watch: "Cloning... Parsing... Architect running... Reviewer running..."
5. Dashboard loads panel by panel as results come in
6. Show architecture graph — zoom in, click a node
7. Show code review — 3 HIGH severity findings highlighted
8. Show docs — generated docstrings for undocumented functions
9. Show security — 2 issues flagged with fix suggestions
10. Health score animates to final number — **74/100 — Grade B**
11. "Flask is production-ready but has 3 areas needing attention..."

**That's the demo. Practise it twice before submitting.**

---

## Submission Checklist

- [ ] GitHub repo is public
- [ ] `bob_sessions/` folder has exports from all 6 team members
- [ ] README has screenshots, setup instructions, tech stack
- [ ] Demo video is 2 minutes max
- [ ] App runs locally with `npm run dev` + `uvicorn main:app`
- [ ] `.env.example` shows required keys (no actual keys committed)
- [ ] Submitted on lablab.ai before May 17 8:00 AM PDT

---

## Hour-by-Hour Summary

| Hours | Milestone |
|-------|-----------|
| 0–4 | All 6 setups done. Backend skeleton. 4 agent skeletons. Homepage UI live. |
| 4–10 | Backend parsing works. Agents 1+2 producing real output. D3 graph renders. |
| 10–18 | Full pipeline connected end-to-end. Real data in all 5 panels. |
| 18–22 | Polish. Edge cases. Demo repo tested. Video recorded. |
| 22–24 | Bob sessions exported. README done. Submitted. |

---

## If Things Break — Priority Order

If you run out of time, cut in this order — **never cut the core loop:**

**Must have (non-negotiable):**
- Repo URL input → backend → at least 2 agents running → health score → dashboard

**Cut first if needed:**
- Docs viewer (Agent 3 output)
- Modernization section of Security panel

**Cut second if needed:**
- D3 graph → replace with simple file tree list
- Live progress log → replace with simple spinner

**Never cut:**
- Health score card — this is the money shot
- Code review findings — this is the clearest value
- The architecture graph — this is what judges remember

---

*Built with IBM Bob. Powered by watsonx. RepoSense — From repo to insight in minutes.*
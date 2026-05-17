# RepoSense

> AI-powered codebase health analysis, right inside VS Code.

Built with IBM Bob · IBM watsonx Orchestrate · watsonx.ai (Granite)

---

## What It Does

Open any project in VS Code, click the RepoSense icon, get a full health report in minutes — without leaving your editor.

| Panel | What You Get |
|---|---|
| 💯 Health Score | Score out of 100 with grade (A–F) and breakdown |
| 🏗️ Architecture | D3 module dependency graph, zoomable and clickable |
| 🔍 Code Review | AI-detected issues with severity and file locations |
| 📚 Documentation | Auto-generated function docs and unit test stubs |
| 🔒 Security | Vulnerability detection and modernization priorities |

Four IBM watsonx Orchestrate agents do the work — Architect, Reviewer, Documenter, Hardener — coordinated by a local FastAPI backend. Health scoring uses the Granite model on watsonx.ai.

**Supported languages:** Python, JavaScript, TypeScript.

---

## Architecture

```
VS Code Extension (TypeScript)
    │
    │  HTTP (localhost:8000)
    ▼
FastAPI Backend (Python)
  ├── Parser — reads workspace files
  ├── Job Queue — tracks analysis state
  └── Orchestrate Client
            │
            │  IBM watsonx APIs
            ▼
    ┌───────────────────────────────────┐
    │  watsonx Orchestrate              │
    │  ├── Architect Agent              │
    │  ├── Reviewer Agent               │
    │  ├── Documenter Agent             │
    │  └── Hardener Agent               │
    │                                   │
    │  watsonx.ai (Granite)             │
    │  └── Health Score Calculator      │
    └───────────────────────────────────┘
```

---

## Running Locally

### Prerequisites

- **Python 3.11, 3.12, or 3.13** (constrained by `ibm-watsonx-ai==1.5.11` which requires `>=3.11,<3.14`). Install from [python.org](https://www.python.org/downloads/).
- **Node.js 18+** (LTS recommended). Install from [nodejs.org](https://nodejs.org/).
- **VS Code** with the `code` command in PATH.
  - macOS: open VS Code → `Cmd+Shift+P` → "Shell Command: Install 'code' command in PATH".
  - Windows: re-run the VS Code installer and check "Add to PATH".
- **bash** (built-in on macOS/Linux; on Windows install [Git for Windows](https://gitforwindows.org/) and run from Git Bash).
- IBM watsonx credentials (entered via the in-app setup wizard — no manual `.env` editing required).

### Quick Start (Recommended)

Execute `run.sh` from the repo root to set up everything and launch the application:

```bash
./run.sh
```

The script will:

1. **Check prerequisites** — Python (correct version), Node.js, npm, `code` CLI, port 8000. Bails early with a clear message if anything's missing.
2. Create a Python virtual environment in `venv/` using a compatible Python.
3. Install backend dependencies from `backend/requirements.txt`.
4. Install extension dependencies with `npm install` and compile the TypeScript.
5. Start the uvicorn backend on `http://localhost:8000` and wait until it actually responds (not just "process exists").
6. Launch VS Code with the extension loaded in development mode.

The backend keeps running in the background. Press `Ctrl+C` to stop the launcher; the backend's PID is printed so you can `kill` it when you're done.

On first launch, the RepoSense sidebar shows a setup wizard for your watsonx credentials. The wizard writes them to `backend/.env` and reloads settings in memory.

### Manual Setup

If you prefer to run components separately:

#### 1. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Backend runs on `http://localhost:8000`. Verify:

```bash
curl http://localhost:8000/
# {"service":"RepoSense API","status":"running","version":"1.0.0"}
```

#### 2. Run the extension

```bash
cd vscode-extension
npm install
```

Press `F5` in VS Code to launch the Extension Development Host, open any project folder, and click the RepoSense icon in the sidebar.

#### 3. Configure credentials

On first launch, the sidebar shows a setup wizard. Enter your watsonx credentials there — the extension posts them to `/config/setup`, which persists them to `backend/.env` and reloads settings in memory. No manual `.env` editing required.

If you'd rather pre-populate `.env` yourself, copy `backend/.env.example` to `backend/.env` and fill in the real values (not the placeholder strings — the backend treats non-empty placeholders as "configured" and skips the wizard).

---

## API Reference

### `POST /analyze`

Start analysis on a local path.

```json
{ "local_path": "/absolute/path/to/project" }
```

Returns:

```json
{ "type": "request", "job_id": "abc-123", "progress": [...] }
```

### `GET /jobs/{job_id}`

Poll for status. While running, returns `type: "request"` with current `progress` steps. On completion, `type: "result"` with the full payload:

```json
{
  "type": "result",
  "job_id": "abc-123",
  "progress": [...],
  "payload": {
    "score":        { "score": 74, "grade": "B", "breakdown": {...}, "summary": "...", "top_priorities": [...] },
    "architecture": { "nodes": [...], "edges": [...] },
    "review":       { "findings": [...] },
    "docs":         { "docs": [...], "tests": [...] },
    "security":     { "security": [...], "modernization": [...] }
  }
}
```

On failure, `type: "error"` with a code, message, and the stage that failed.

### `DELETE /jobs/{job_id}`

Remove a job from the in-memory store.

### `POST /cleanup`

Manually trigger cleanup of jobs older than `JOB_RETENTION_HOURS` (default 24). Returns `{ "removed": <count> }`.

### `GET /config/status`

Check whether all required watsonx credentials are set. Returns `{ "configured": bool, "missing_fields": [...] }`. The VS Code extension calls this on launch to decide whether to show its setup wizard.

### `POST /config/setup`

Persist any subset of watsonx credentials. Non-empty values are written to `backend/.env` and reloaded in memory. Returns the same shape as `/config/status`.

---

## Environment Variables

See `.env.example` for the full list. Required:

```
# watsonx Orchestrate (agents)
ORCHESTRATE_API_KEY=
ORCHESTRATE_URL=https://api.us-south.watson-orchestrate.cloud.ibm.com
ORCHESTRATE_INSTANCE_ID=
ORCHESTRATE_AGENT_ARCHITECT_ID=
ORCHESTRATE_AGENT_REVIEWER_ID=
ORCHESTRATE_AGENT_DOCUMENTER_ID=
ORCHESTRATE_AGENT_HARDENER_ID=

# watsonx.ai (health scoring)
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

The Orchestrate client exchanges your API key for an IBM IAM bearer token on demand — no manual token handling required.

---

## IBM Bob Usage

Built entirely with IBM Bob IDE. Session exports for all 6 team members are in `bob_sessions/`, organized by role (P1–P6).

---

## Team

| Member | Role |
|---|---|
| P1 | Backend — FastAPI, job queue, parser |
| P2 | Orchestrate — four AI agent implementations |
| P3 | AI — health scoring with watsonx.ai Granite |
| P4 | Extension — VS Code extension core |
| P5 | Webview — interactive panels with D3.js |
| P6 | Integration, demo, submission |

---

## License

Built for the IBM Bob Hackathon 2026. See repository for license details.

---

*IBM Bob Hackathon 2026*

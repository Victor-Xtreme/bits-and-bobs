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

- Python 3.10+
- Node.js 18+
- VS Code
- IBM watsonx credentials (API key + project ID)

### 1. Start the backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # fill in your watsonx credentials
uvicorn src.main:app --reload
```

Backend runs on `http://localhost:8000`. Verify:

```bash
curl http://localhost:8000/
# {"service":"RepoSense API","status":"running","version":"1.0.0"}
```

### 2. Run the extension

```bash
cd vscode-extension
npm install
```

Press `F5` in VS Code to launch the Extension Development Host, open any project folder, and click the RepoSense icon in the sidebar.

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

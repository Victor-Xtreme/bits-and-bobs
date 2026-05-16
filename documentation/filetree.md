# RepoSense — Project File Tree

## Overview
This file tree represents the complete structure for the RepoSense VS Code extension project, organized by component and responsibility.

---

## Root Structure

```
reposense-ibm-hackathon/
├── backend/                      # FastAPI backend (P1 - Backend Lead)
├── vscode-extension/             # VS Code extension (P4 - Extension Lead, P5 - Webview Lead)
├── bob_sessions/                 # IBM Bob IDE session exports (P6 - Integration)
├── documentation/                # Project documentation
├── tests/                        # Integration and E2E tests
├── .github/                      # GitHub workflows and templates
├── .gitignore
├── .env.example
├── README.md
├── DEMO_SCRIPT.md
├── LICENSE
└── package.json                  # Root package.json for workspace management
```

---

## Backend Directory (`/backend`)

**Owner:** P1 - Backend Lead  
**Purpose:** FastAPI server handling code analysis, orchestration, and AI integration

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, routes, CORS config
│   ├── parser.py                 # File walker, AST chunker, import extractor
│   ├── orchestrate.py            # watsonx Orchestrate API client
│   ├── watsonx.py                # watsonx.ai Granite model client
│   ├── models.py                 # Pydantic request/response schemas
│   ├── jobs.py                   # In-memory job store + progress tracking
│   ├── config.py                 # Configuration management
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py         # File system utilities
│       ├── ast_parser.py         # AST parsing helpers
│       └── logger.py             # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_orchestrate.py
│   ├── test_watsonx.py
│   ├── test_api.py
│   └── fixtures/
│       └── sample_repos/         # Test repositories
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml                # Python project configuration
├── setup.py                      # Package setup
├── .env.example                  # Environment variables template
├── .pylintrc                     # Linting configuration
├── pytest.ini                    # Pytest configuration
└── README.md                     # Backend documentation
```

### Backend Key Files Details

**[`main.py`](backend/src/main.py)**
- FastAPI application initialization
- Route definitions: POST /analyze, GET /results/{job_id}
- CORS configuration for local development
- Error handling middleware
- Health check endpoint

**[`parser.py`](backend/src/parser.py)**
- Recursive file tree walker
- AST-based code parsing (Python, JavaScript, TypeScript)
- Function/class extraction
- Import graph generation
- Code chunking by module

**[`orchestrate.py`](backend/src/orchestrate.py)**
- watsonx Orchestrate API client
- 4 agent implementations:
  - Agent 1: ARCHITECT (file tree + import graph)
  - Agent 2: REVIEWER (code review findings)
  - Agent 3: DOCUMENTER (docs + test stubs)
  - Agent 4: HARDENER (security + modernization)
- Agent orchestration logic
- Response parsing and normalization

**[`watsonx.py`](backend/src/watsonx.py)**
- watsonx.ai Granite model client
- Health score calculation
- Grade assignment (A-F)
- Summary generation
- Top 3 priorities extraction

**[`models.py`](backend/src/models.py)**
- Pydantic schemas for:
  - AnalyzeRequest
  - AnalyzeResponse
  - JobStatus
  - HealthScore
  - ArchitectureGraph
  - CodeReviewFinding
  - Documentation
  - SecurityIssue

**[`jobs.py`](backend/src/jobs.py)**
- In-memory job store (dict-based)
- Job status tracking
- Progress updates
- Result caching

---

## VS Code Extension Directory (`/vscode-extension`)

**Owners:** P4 - Extension Lead, P5 - Webview Lead  
**Purpose:** VS Code extension with webview UI

```
vscode-extension/
├── src/
│   ├── extension.ts              # Main extension entry point
│   ├── providers/
│   │   ├── RepoSenseViewProvider.ts    # Webview view provider
│   │   └── StatusBarProvider.ts        # Status bar integration
│   ├── services/
│   │   ├── ApiClient.ts          # Backend API client
│   │   ├── AnalysisService.ts    # Analysis orchestration
│   │   └── WorkspaceService.ts   # Workspace file operations
│   ├── commands/
│   │   ├── analyzeCommand.ts     # Analyze workspace command
│   │   ├── refreshCommand.ts     # Refresh analysis command
│   │   └── openBrowserCommand.ts # Open in browser command
│   ├── types/
│   │   ├── api.types.ts          # API response types
│   │   └── extension.types.ts    # Extension-specific types
│   └── utils/
│       ├── logger.ts             # Extension logging
│       └── config.ts             # Extension configuration
├── webview/                      # Webview UI (P5 - Webview Lead)
│   ├── index.html                # Main webview HTML
│   ├── styles/
│   │   ├── main.css              # Base styles
│   │   ├── components.css        # Component styles
│   │   ├── panels.css            # Panel-specific styles
│   │   └── animations.css        # Animations and transitions
│   ├── scripts/
│   │   ├── main.js               # Main webview script
│   │   ├── components/
│   │   │   ├── ScoreCard.js      # Health score component
│   │   │   ├── ArchitectureGraph.js  # D3 graph component
│   │   │   ├── ReviewPanel.js    # Code review panel
│   │   │   ├── DocsPanel.js      # Documentation panel
│   │   │   ├── SecurityPanel.js  # Security panel
│   │   │   └── Navigation.js     # Tab navigation
│   │   ├── utils/
│   │   │   ├── messageHandler.js # VS Code message handling
│   │   │   ├── animations.js     # Animation utilities
│   │   │   └── formatters.js     # Data formatting
│   │   └── d3/
│   │       └── graph-renderer.js # D3 force-directed graph
│   └── assets/
│       ├── icons/                # UI icons
│       └── images/               # Images and graphics
├── media/                        # Extension media assets
│   ├── icon.png                  # Extension icon (128x128)
│   ├── icon-dark.png             # Dark theme icon
│   └── icon-light.png            # Light theme icon
├── test/
│   ├── suite/
│   │   ├── extension.test.ts
│   │   ├── apiClient.test.ts
│   │   └── providers.test.ts
│   └── runTest.ts                # Test runner
├── .vscode/
│   ├── launch.json               # Debug configuration
│   ├── tasks.json                # Build tasks
│   └── extensions.json           # Recommended extensions
├── package.json                  # Extension manifest
├── tsconfig.json                 # TypeScript configuration
├── webpack.config.js             # Webpack bundling config
├── .vscodeignore                 # Files to exclude from package
├── .eslintrc.json                # ESLint configuration
├── .prettierrc                   # Prettier configuration
└── README.md                     # Extension documentation
```

### Extension Key Files Details

**[`extension.ts`](vscode-extension/src/extension.ts)**
- Extension activation/deactivation
- Command registration
- View provider registration
- Workspace folder monitoring

**[`RepoSenseViewProvider.ts`](vscode-extension/src/providers/RepoSenseViewProvider.ts)**
- Webview view provider implementation
- Message passing between extension and webview
- Analysis lifecycle management
- Progress polling (3-second intervals)

**[`ApiClient.ts`](vscode-extension/src/services/ApiClient.ts)**
- HTTP client for backend API
- POST /analyze endpoint
- GET /results/{job_id} polling
- Error handling and retries

**Webview Components:**
- **[`ScoreCard.js`](vscode-extension/webview/scripts/components/ScoreCard.js)**: Animated health score with circular progress ring
- **[`ArchitectureGraph.js`](vscode-extension/webview/scripts/components/ArchitectureGraph.js)**: D3.js force-directed module dependency graph
- **[`ReviewPanel.js`](vscode-extension/webview/scripts/components/ReviewPanel.js)**: Code review findings with severity filtering
- **[`DocsPanel.js`](vscode-extension/webview/scripts/components/DocsPanel.js)**: Auto-generated documentation and test stubs
- **[`SecurityPanel.js`](vscode-extension/webview/scripts/components/SecurityPanel.js)**: Security vulnerabilities and modernization priorities

---

## Bob Sessions Directory (`/bob_sessions`)

**Owner:** P6 - Integration + Demo + Submission  
**Purpose:** IBM Bob IDE session exports demonstrating AI-assisted development

```
bob_sessions/
├── P1_backend/
│   ├── parser_session.md
│   ├── parser_screenshot.png
│   ├── fastapi_session.md
│   ├── fastapi_screenshot.png
│   ├── orchestrate_session.md
│   └── orchestrate_screenshot.png
├── P2_orchestrate/
│   ├── agents_session.md
│   ├── agents_screenshot.png
│   ├── architect_agent_session.md
│   └── reviewer_agent_session.md
├── P3_ai/
│   ├── scoring_session.md
│   ├── scoring_screenshot.png
│   ├── watsonx_integration_session.md
│   └── watsonx_screenshot.png
├── P4_extension/
│   ├── extension_session.md
│   ├── extension_screenshot.png
│   ├── commands_session.md
│   └── providers_session.md
├── P5_webview/
│   ├── webview_session.md
│   ├── webview_screenshot.png
│   ├── d3_graph_session.md
│   └── components_session.md
├── P6_integration/
│   ├── integration_session.md
│   ├── integration_screenshot.png
│   ├── testing_session.md
│   └── demo_prep_session.md
├── README.md                     # Bob sessions overview
└── placeholderfile.txt           # Placeholder (to be replaced)
```

---

## Documentation Directory (`/documentation`)

```
documentation/
├── teamspec.md                   # Complete team specification
├── filetree.md                   # This file
├── architecture.md               # System architecture details
├── api-contract.md               # API endpoint specifications
├── development-guide.md          # Development setup and guidelines
├── deployment.md                 # Deployment instructions
├── demo-guide.md                 # Demo preparation guide
└── diagrams/
    ├── system-architecture.mmd   # Mermaid system diagram
    ├── data-flow.mmd             # Data flow diagram
    └── agent-workflow.mmd        # Agent orchestration workflow
```

---

## Tests Directory (`/tests`)

```
tests/
├── integration/
│   ├── test_full_pipeline.py     # End-to-end pipeline test
│   ├── test_extension_backend.py # Extension-backend integration
│   └── test_agents.py            # Agent integration tests
├── e2e/
│   ├── test_flask_analysis.py    # Test with Flask repository
│   ├── test_js_project.py        # Test with JavaScript project
│   └── test_error_scenarios.py   # Error handling tests
├── fixtures/
│   ├── sample_python_repo/       # Sample Python project
│   ├── sample_js_repo/           # Sample JavaScript project
│   └── expected_outputs/         # Expected analysis results
└── README.md                     # Testing documentation
```

---

## GitHub Directory (`/.github`)

```
.github/
├── workflows/
│   ├── backend-tests.yml         # Backend CI/CD
│   ├── extension-tests.yml       # Extension CI/CD
│   └── integration-tests.yml     # Integration tests
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   └── feature_request.md
├── PULL_REQUEST_TEMPLATE.md
└── CODEOWNERS                    # Code ownership
```

---

## Root Configuration Files

**[`.gitignore`](.gitignore)**
```
# Python
__pycache__/
*.py[cod]
*$py.class
.env
venv/
.pytest_cache/

# Node
node_modules/
dist/
*.vsix
.vscode-test/

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

**[`.env.example`](.env.example)**
```
# watsonx.ai Configuration
WATSONX_API_KEY=your_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# watsonx Orchestrate Configuration
ORCHESTRATE_API_KEY=your_key_here
ORCHESTRATE_URL=your_orchestrate_url_here

# Backend Configuration
BACKEND_PORT=8000
BACKEND_HOST=localhost

# Development
DEBUG=false
LOG_LEVEL=INFO
```

**[`README.md`](README.md)**
- Project overview and tagline
- Features showcase
- Installation instructions
- Usage guide with screenshots
- Architecture diagram
- Technology stack
- Team credits
- IBM Bob IDE usage documentation
- Demo video link
- License information

**[`DEMO_SCRIPT.md`](DEMO_SCRIPT.md)**
- 2-minute demo script
- Key talking points
- Screenshot references
- Demo flow timeline

**[`package.json`](package.json)** (Root workspace)
```json
{
  "name": "reposense-workspace",
  "private": true,
  "workspaces": [
    "vscode-extension"
  ],
  "scripts": {
    "install:all": "npm install && cd vscode-extension && npm install && cd ../backend && pip install -r requirements.txt",
    "dev:backend": "cd backend && uvicorn src.main:app --reload",
    "dev:extension": "cd vscode-extension && npm run watch",
    "test:backend": "cd backend && pytest",
    "test:extension": "cd vscode-extension && npm test",
    "build:extension": "cd vscode-extension && npm run compile && vsce package",
    "lint": "npm run lint:extension && npm run lint:backend",
    "lint:extension": "cd vscode-extension && npm run lint",
    "lint:backend": "cd backend && pylint src/"
  }
}
```

---

## File Count Summary

| Component | Files | Purpose |
|-----------|-------|---------|
| Backend | ~25 | FastAPI server, parsers, AI clients |
| Extension | ~30 | VS Code extension logic |
| Webview | ~20 | UI components and styling |
| Tests | ~15 | Integration and E2E tests |
| Documentation | ~10 | Specs, guides, diagrams |
| Bob Sessions | ~24 | AI development session exports |
| Configuration | ~15 | Build, lint, deploy configs |
| **Total** | **~139** | Complete project structure |

---

## Technology Stack by Directory

### Backend (`/backend`)
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **AI:** IBM watsonx.ai (Granite), watsonx Orchestrate
- **Parsing:** ast (Python), esprima (JavaScript)
- **Testing:** pytest
- **Linting:** pylint, black

### Extension (`/vscode-extension`)
- **Language:** TypeScript
- **Framework:** VS Code Extension API
- **Build:** Webpack
- **Testing:** Mocha, VS Code Test Runner
- **Linting:** ESLint, Prettier

### Webview (`/vscode-extension/webview`)
- **Languages:** HTML, CSS, JavaScript
- **Visualization:** D3.js (force-directed graphs)
- **Styling:** Custom CSS with VS Code theme variables
- **Animation:** CSS animations + JavaScript

---

## Development Workflow

1. **Backend Development** (P1)
   - Work in [`/backend`](backend/)
   - Run: `uvicorn src.main:app --reload`
   - Test: `pytest`

2. **Extension Development** (P4)
   - Work in [`/vscode-extension/src`](vscode-extension/src/)
   - Run: Press F5 in VS Code (launches Extension Host)
   - Test: `npm test`

3. **Webview Development** (P5)
   - Work in [`/vscode-extension/webview`](vscode-extension/webview/)
   - Preview: Extension Host with live reload
   - Test: Manual testing in webview

4. **Integration** (P6)
   - Run full pipeline: Backend + Extension
   - Test with real repositories
   - Export Bob sessions to [`/bob_sessions`](bob_sessions/)

---

## Build and Package

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m pytest
```

### Extension
```bash
cd vscode-extension
npm install
npm run compile
vsce package  # Creates .vsix file
```

### Full Build
```bash
npm run install:all
npm run build:extension
```

---

## Deployment Artifacts

- **Extension Package:** `reposense-*.vsix` (VS Code extension installer)
- **Backend Docker:** `Dockerfile` in backend/ (optional for cloud deployment)
- **Demo Video:** Linked in README.md
- **Bob Sessions:** All exports in [`/bob_sessions`](bob_sessions/)

---

## Notes

- All file paths are relative to project root
- Backend runs on `http://localhost:8000`
- Extension connects to backend via HTTP
- Webview uses VS Code's webview API for secure rendering
- Bob sessions demonstrate AI-assisted development throughout
- Project designed for 24-hour hackathon timeline
- Modular structure allows parallel development by 6 team members

---

**Last Updated:** 2026-05-16  
**Project:** RepoSense — IBM Bob Hackathon 2026  
**Team Size:** 6 developers  
**Timeline:** 24 hours
# RepoSense VS Code Extension - Release Notes

## Version 1.0.0 - May 17, 2026

### Release Overview

RepoSense 1.0.0 is the first stable release of the RepoSense VS Code extension, now fully integrated with a cloud-deployed backend service. This release enables repository analysis and health scoring directly from VS Code with real-time progress tracking.

### What's New

- **Cloud-Deployed Backend**: Backend service now runs on Render at `https://bits-and-bobs-deployment-1.onrender.com`
- **No Local Setup Required**: Simply install the extension and start analyzing workspaces
- **Real-Time Progress Updates**: Watch analysis progress as it happens with step-by-step status
- **Comprehensive Health Scoring**: Get detailed repository health metrics including:
  - Code quality score
  - Security assessment
  - Documentation coverage
  - Architecture analysis
  - Top priority recommendations
- **WebView Sidebar**: Dedicated sidebar panel for analysis results and configuration
- **Configurable Backend URL**: Option to override backend URL for custom deployments

### Installation

#### Option A: Install from VSIX File (Recommended for Testing)

1. Download the `reposense-1.0.0.vsix` file from the release assets
2. Open Visual Studio Code
3. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (Mac) to open Extensions
4. Click the `...` menu at the top of the Extensions panel
5. Select **"Install from VSIX..."**
6. Navigate to and select `reposense-1.0.0.vsix`
7. VS Code will install the extension and reload

#### Option B: Install from VS Code Marketplace (When Published)

Coming soon! The extension will be published to the official VS Code Marketplace, allowing one-click installation directly from VS Code.

### Quick Start

1. **Open the RepoSense Sidebar**:
   - Click the RepoSense icon in the Activity Bar (left sidebar)
   - A new panel titled "RepoSense" will appear

2. **Configure Backend (First Time Only)**:
   - If the backend is not yet configured, you'll see a setup screen
   - Enter your credentials for IBM WatsonX and Orchestrate (these are used by the backend for AI analysis)
   - Click "Save Configuration"

3. **Analyze Your Workspace**:
   - Click "Analyze Workspace" button
   - The extension will send your workspace folder to the Render backend
   - Watch real-time progress updates:
     - ✓ Parser complete
     - ✓ Architect complete
     - ✓ Code Review complete
     - ✓ Documentation complete
     - ✓ Security Hardening complete
   - Results will display automatically when analysis completes

4. **View Results**:
   - **Health Score**: Overall repository health (0-100) with letter grade (A-F)
   - **Score Breakdown**: Detailed metrics for quality, security, documentation, and architecture
   - **Top Priorities**: Key recommendations to improve repository health
   - **Full Analysis**: Click "Open Full Report" to see comprehensive analysis details

### Backend Service Details

The RepoSense backend runs on **Render** (PaaS platform) at:
```
https://bits-and-bobs-deployment-1.onrender.com
```

#### Supported Endpoints

- `POST /analyze` - Start a new codebase analysis
- `GET /jobs/{job_id}` - Check analysis status and retrieve results
- `DELETE /jobs/{job_id}` - Delete an analysis job
- `GET /config/status` - Check backend configuration status
- `POST /config/setup` - Configure backend credentials
- `POST /cleanup` - Manually trigger cleanup of old analysis jobs

#### Backend Features

- **Asynchronous Processing**: Long-running analyses run in background tasks
- **Job Management**: Automatic cleanup of old jobs (>24 hours)
- **Concurrent Job Limits**: Default limit of 5 concurrent analyses
- **CORS Support**: Backend accepts requests from any origin
- **Path Validation**: Secure path validation prevents unauthorized filesystem access

#### Technology Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn + Gunicorn (4 workers on Render)
- **AI Integration**: IBM WatsonX AI 1.5.11
- **Process Orchestration**: Orchestrate AI platform
- **Deployment**: Render (Docker container, Python 3.12)

### Configuration

#### Extension Settings

Access via VS Code: `File → Preferences → Settings → Search "reposense"`

- **`reposense.backendUrl`** (default: `https://bits-and-bobs-deployment-1.onrender.com`)
  - The backend API server URL
  - Change this if running a custom backend deployment

- **`reposense.requestTimeoutMs`** (default: `30000`)
  - HTTP request timeout in milliseconds
  - Increase if analyses are timing out

- **`reposense.pollingIntervalMs`** (default: `2000`)
  - How often to poll backend for job status (milliseconds)
  - Lower = more frequent updates (higher bandwidth/CPU)

### Usage Scenarios

#### Scenario 1: Repository Health Check
```
1. Open a workspace in VS Code
2. Click RepoSense in Activity Bar
3. Click "Analyze Workspace"
4. Wait for analysis (~2-5 minutes depending on repo size)
5. Review health score and recommendations
```

#### Scenario 2: Pre-Commit Quality Gate
```
Use the health score to ensure code quality before pushing:
- If score < 70, review top priorities before committing
- If score >= 80, proceed with confidence
```

#### Scenario 3: Technical Debt Assessment
```
1. Analyze workspace quarterly
2. Track health score trends
3. Use top priorities to guide refactoring work
```

### Architecture

```
┌─────────────────────────────────────────┐
│   VS Code Extension (Webview Sidebar)   │
│                                         │
│  - User Interface                       │
│  - Job Polling                          │
│  - Results Display                      │
└──────────────────┬──────────────────────┘
                   │ HTTPS
                   ↓
┌─────────────────────────────────────────┐
│    Render Backend (Cloud Deployed)      │
│  https://bits-and-bobs-deployment...    │
│                                         │
│  - FastAPI Server                       │
│  - Job Management                       │
│  - Analysis Orchestration               │
│  - WatsonX AI Integration               │
│  - Orchestrate Process Execution        │
└──────────────────┬──────────────────────┘
                   │ (async background tasks)
                   ↓
┌─────────────────────────────────────────┐
│    Analysis Pipeline (on Backend)       │
│                                         │
│  1. Parser - Extract code structure    │
│  2. Architect - Analyze architecture   │
│  3. Reviewer - AI code review          │
│  4. Documenter - Generate docs         │
│  5. Hardener - Security analysis       │
└─────────────────────────────────────────┘
```

### Performance & Limitations

- **Analysis Time**: 2-5 minutes depending on repository size
- **Concurrent Jobs**: Max 5 per backend instance
- **Free Tier**: Render free tier is used; may experience cold starts (first request slower)
- **Workspace Size**: Works best with codebases < 1 GB
- **Supported Languages**: Python, TypeScript, JavaScript (extensible)

### Troubleshooting

#### Issue: "Backend unreachable"
- **Cause**: Render service may be in cold start or down
- **Solution**: Wait 30 seconds and retry; check https://bits-and-bobs-deployment-1.onrender.com in browser

#### Issue: "Configuration incomplete"
- **Cause**: WatsonX or Orchestrate API keys not set on backend
- **Solution**: 
  1. Contact backend administrator to configure credentials
  2. Or configure via Settings panel if you have backend credentials

#### Issue: Analysis takes very long
- **Cause**: Large repository or backend overloaded
- **Solution**: 
  - Increase `reposense.requestTimeoutMs` setting
  - Try analyzing a smaller workspace
  - Wait and retry (backend may be processing other jobs)

#### Issue: "Maximum concurrent jobs exceeded"
- **Cause**: Too many analyses running on backend
- **Solution**: Wait for other analyses to complete; Render cleans up old jobs automatically

### Known Limitations

- Extension only supports analyzing a single workspace folder
- Backend must be configured with WatsonX and Orchestrate API keys
- Analyses are retained for 24 hours on backend, then auto-deleted
- Cannot cancel running analyses from UI (will auto-complete or timeout)
- Repository credentials/secrets are never sent to backend; only code structure is analyzed

### Future Roadmap

- Multi-workspace analysis support
- Analysis history and trends tracking
- Custom rule configuration for code quality
- Local backend option (Docker container)
- Integration with GitHub Actions for CI/CD
- Detailed code visualization and navigation
- Performance benchmarking and profiling tools

### Feedback & Support

- **Report Issues**: GitHub Issues (when repo is public)
- **Feature Requests**: GitHub Discussions or email
- **Documentation**: See [README.md](README.md) for additional information

### Technical Support

For backend deployment questions or custom setups, refer to:
- Backend docs: `backend/README.md` (in repository)
- Render documentation: https://render.com/docs
- FastAPI docs: https://fastapi.tiangolo.com
- Extension development: https://code.visualstudio.com/api

### License

MIT License - See [LICENSE](LICENSE) file for details

---

**Happy Analyzing! 🎉**

For the best experience, ensure your workspace is committed to Git and has a clear project structure.

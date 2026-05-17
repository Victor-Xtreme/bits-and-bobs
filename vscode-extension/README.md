# RepoSense — VS Code Extension

The VS Code front end for RepoSense. Triggers analysis on the local FastAPI backend, polls for progress, and renders the full report (health score, architecture graph, code review, docs, security) in a sidebar webview.

The webview UI itself lives in [`webview/`](webview/) and is documented separately.

---

## Requirements

- VS Code 1.74.0 or higher
- Node.js 18+ (for building the extension)
- RepoSense backend reachable at the configured `backendUrl` (default `http://localhost:8000`) — see the [backend setup](../README.md#running-locally)

---

## Install & Run (Development)

```bash
cd vscode-extension
npm install
npm run compile
```

Then press `F5` in VS Code to launch an Extension Development Host with the extension loaded. Open any folder in that window and click the **RepoSense** icon in the Activity Bar.

For watch mode during development:

```bash
npm run watch
```

---

## How It Works

On first launch, the extension calls `GET /config/status`. If watsonx credentials are missing, the webview shows a setup wizard that POSTs them to `/config/setup` (which writes them to `backend/.env`).

Once configured, the analysis flow is:

1. Read the first workspace folder's path
2. `POST /analyze` with `{ local_path }` → backend returns a `job_id`
3. Poll `GET /jobs/{job_id}` every `pollingIntervalMs` (2s default)
4. On `type: "result"`, render the payload in the webview and cache it per workspace folder
5. On `type: "error"`, show the error message and stop polling

Results are cached per workspace path. Switching workspace folders clears the cache and re-runs analysis automatically.

---

## Commands

| Command ID | Title | Behavior |
|---|---|---|
| `reposense.focusSidebar` | (status bar click) | Focuses the RepoSense sidebar view |
| `reposense.refresh` | Refresh Analysis | Forces a fresh analysis, bypassing the cache |
| `reposense.openInBrowser` | RepoSense: Open in Browser | Opens the cached report in a full editor panel |

The status bar item (left side) shows the current state: `Ready` / `Analyzing...` / `Score N/100` / `Error`.

---

## Settings

Configurable via VS Code settings (`reposense.*`):

| Setting | Default | Description |
|---|---|---|
| `reposense.backendUrl` | `http://localhost:8000` | URL of the RepoSense backend API |
| `reposense.requestTimeoutMs` | `30000` | HTTP request timeout in milliseconds |
| `reposense.pollingIntervalMs` | `2000` | How often to poll `/jobs/{id}` for results |

---

## Backend API Used

The extension speaks to four backend endpoints. All analysis responses use a shared envelope:

```ts
interface ApiResponse {
  type: 'request' | 'result' | 'error';
  job_id: string;
  progress: ProgressStep[];
  payload: AnalysisResult | AnalysisError | null;
}
```

### `POST /analyze`

Request: `{ "local_path": "/absolute/path/to/workspace" }`

Returns an `ApiResponse` with `type: "request"`, the new `job_id`, and the initial progress steps. `payload` is `null` at this point.

### `GET /jobs/{job_id}`

Returns the current state of the job:

- **In progress** — `type: "request"`, `payload: null`, `progress[]` reflects which steps are `done`/`active`/`pending`.
- **Done** — `type: "result"`, `payload: AnalysisResult` containing `{ score, architecture, review, docs, security }`.
- **Failed** — `type: "error"`, `payload: AnalysisError` with `{ code, message, stage }`.

### `GET /config/status`

Returns `{ configured: boolean, missing_fields: string[] }` so the extension can decide whether to show the setup wizard.

### `POST /config/setup`

Body contains any subset of the watsonx credential fields. The backend persists non-empty values to `backend/.env` and reloads settings in memory. Returns the same shape as `/config/status`.

The full TypeScript types mirroring the backend models live at the top of [`src/SidebarProvider.ts`](src/SidebarProvider.ts#L7-L136).

---

## Source Layout

```
vscode-extension/
├── src/
│   ├── extension.ts          # activate/deactivate, command registration
│   ├── SidebarProvider.ts    # webview host, API calls, polling, caching
│   └── config.ts             # reads reposense.* settings from VS Code
├── webview/                  # HTML/CSS/JS UI rendered inside the sidebar (see webview/README.md)
├── media/                    # icons
├── out/                      # compiled JS (gitignored)
├── package.json              # commands, views, settings contributions
├── tsconfig.json
├── SETUP.md                  # extended setup + troubleshooting walkthrough
└── README.md
```

---

## Troubleshooting

- **Sidebar shows the setup wizard repeatedly** — backend reports credentials are still missing. Check `backend/.env` after submitting the wizard.
- **"Failed to start analysis: Failed to fetch"** — backend isn't running at `reposense.backendUrl`, or CORS blocks the webview origin. See [SETUP.md](SETUP.md#troubleshooting).
- **Polling never stops** — reload the window (`Developer: Reload Window`). The poller stops on `result`/`error` responses; a transient network blip retries up to 3 times before surfacing an error.

For deeper setup notes (CORS, watsonx credentials, manual curl tests) see [SETUP.md](SETUP.md).

---

*Part of RepoSense · IBM Bob Hackathon 2026*

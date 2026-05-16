# RepoSense Extension - API Documentation

**Session Date**: May 16, 2026

---

## Backend API Requirements

The RepoSense extension requires a backend service running on `http://localhost:8000` with the following endpoints.

---

## Endpoint 1: Initiate Analysis

### POST /analyze

Starts a new repository analysis job.

#### Request

**URL**: `http://localhost:8000/analyze`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Body**:
```json
{
  "local_path": "/absolute/path/to/workspace"
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| local_path | string | Yes | Absolute path to the workspace folder |

**Example Request**:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"local_path": "/Users/username/projects/my-repo"}'
```

#### Response

**Status Code**: `200 OK`

**Body**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| job_id | string | Unique identifier for the analysis job |

#### Error Responses

**400 Bad Request**:
```json
{
  "error": "Invalid request",
  "message": "local_path is required"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Server error",
  "message": "Failed to start analysis"
}
```

---

## Endpoint 2: Check Analysis Status

### GET /results/{job_id}

Retrieves the current status and results of an analysis job.

#### Request

**URL**: `http://localhost:8000/results/{job_id}`  
**Method**: `GET`

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| job_id | string | Yes | Job ID returned from /analyze |

**Example Request**:
```bash
curl http://localhost:8000/results/550e8400-e29b-41d4-a716-446655440000
```

#### Response - In Progress

**Status Code**: `200 OK`

**Body**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "progress": {
    "architect": true,
    "security": false,
    "quality": false
  }
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| job_id | string | The job identifier |
| status | string | Current status: "in_progress", "processing", "completed", "failed" |
| progress | object | Optional. Breakdown of completed analysis steps |

#### Response - Completed

**Status Code**: `200 OK`

**Body**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "health_score": 85,
  "progress": {
    "architect": true,
    "security": true,
    "quality": true
  }
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| job_id | string | The job identifier |
| status | string | "completed" or "complete" |
| health_score | number | Repository health score (0-100) |
| progress | object | Optional. All analysis steps completed |

#### Response - Failed

**Status Code**: `200 OK`

**Body**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "error": "Repository not found at specified path"
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| job_id | string | The job identifier |
| status | string | "failed" or "error" |
| error | string | Error message describing what went wrong |

#### Error Responses

**404 Not Found**:
```json
{
  "error": "Job not found",
  "message": "No job exists with the specified ID"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Server error",
  "message": "Failed to retrieve job status"
}
```

---

## Status Flow Diagram

```
POST /analyze
     ↓
  job_id created
     ↓
GET /results/{job_id}
     ↓
┌────────────────────┐
│ status: "in_progress" │ ← Poll every 3 seconds
└────────────────────┘
     ↓
┌────────────────────┐
│ progress updates    │
│ - architect: true   │
│ - security: true    │
└────────────────────┘
     ↓
┌────────────────────┐
│ status: "completed" │
│ health_score: 85    │
└────────────────────┘
     ↓
  Stop polling
```

---

## Extension Integration

### How the Extension Uses the API

```typescript
// 1. Start Analysis
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ local_path: workspacePath })
});
const { job_id } = await response.json();

// 2. Poll for Results
const interval = setInterval(async () => {
  const result = await fetch(`http://localhost:8000/results/${job_id}`);
  const data = await result.json();
  
  if (data.status === 'completed') {
    clearInterval(interval);
    displayHealthScore(data.health_score);
  } else if (data.status === 'failed') {
    clearInterval(interval);
    showError(data.error);
  } else {
    updateProgress(data.progress);
  }
}, 3000);
```

---

## Progress Object Structure

The `progress` object can contain any number of analysis steps. Common examples:

```json
{
  "progress": {
    "architect": true,      // Architecture analysis
    "security": true,       // Security scan
    "quality": false,       // Code quality check
    "dependencies": false,  // Dependency analysis
    "documentation": false, // Documentation coverage
    "testing": false        // Test coverage
  }
}
```

The extension displays completed steps as:
```
✓ architect complete
✓ security complete
```

---

## Polling Strategy

### Configuration

- **Interval**: 3 seconds
- **Method**: GET request
- **Timeout**: None (polls until completion or error)

### Optimization Considerations

**Current Implementation**:
- Simple interval-based polling
- No exponential backoff
- Immediate stop on completion/error

**Potential Improvements**:
- Exponential backoff for long-running jobs
- WebSocket connection for real-time updates
- Configurable polling interval
- Maximum polling duration timeout

---

## Error Handling

### Network Errors

```typescript
try {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
} catch (error) {
  // Display error to user
  showError(`Network error: ${error.message}`);
}
```

### Timeout Handling

Currently no timeout implemented. Consider adding:

```typescript
const timeout = setTimeout(() => {
  clearInterval(pollingInterval);
  showError('Analysis timeout - please try again');
}, 300000); // 5 minutes
```

---

## Testing the API

### Using curl

```bash
# Start analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"local_path": "/path/to/repo"}'

# Check status (replace JOB_ID)
curl http://localhost:8000/results/JOB_ID
```

### Using Postman

1. **POST /analyze**:
   - Method: POST
   - URL: http://localhost:8000/analyze
   - Body: raw JSON
   - Content: `{"local_path": "/path/to/repo"}`

2. **GET /results/{job_id}**:
   - Method: GET
   - URL: http://localhost:8000/results/{job_id}

### Mock Server for Testing

Create a simple mock server for development:

```javascript
// mock-server.js
const express = require('express');
const app = express();
app.use(express.json());

const jobs = {};

app.post('/analyze', (req, res) => {
  const jobId = Math.random().toString(36).substr(2, 9);
  jobs[jobId] = { status: 'in_progress', progress: {} };
  res.json({ job_id: jobId });
});

app.get('/results/:jobId', (req, res) => {
  const job = jobs[req.params.jobId];
  if (!job) return res.status(404).json({ error: 'Not found' });
  
  // Simulate progress
  if (job.status === 'in_progress') {
    job.progress.architect = true;
    setTimeout(() => {
      job.status = 'completed';
      job.health_score = 85;
    }, 5000);
  }
  
  res.json({ job_id: req.params.jobId, ...job });
});

app.listen(8000, () => console.log('Mock server on :8000'));
```

---

## Security Considerations

### CORS

If backend is on different domain, enable CORS:

```javascript
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});
```

### Authentication

Currently no authentication. Consider adding:
- API keys
- OAuth tokens
- JWT authentication

### Rate Limiting

Implement rate limiting to prevent abuse:
- Max requests per minute
- Per-IP or per-user limits
- Exponential backoff on errors

---

**API Documentation Complete**: Ready for backend implementation
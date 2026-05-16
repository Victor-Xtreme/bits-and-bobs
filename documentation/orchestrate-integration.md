# WatsonX Orchestrate Integration Guide

## Overview

This document describes the integration between RepoSense backend and IBM WatsonX Orchestrate agents. The system uses 4 specialized agents to analyze codebases and generate insights.

---

## Architecture

```
┌─────────────────┐
│   FastAPI       │
│   Backend       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ orchestrate.py  │  ← Orchestration logic
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  watsonx.py     │  ← Agent function wrappers
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│orchestrate_     │  ← HTTP client for Orchestrate API
│client.py        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   IBM WatsonX Orchestrate Platform      │
│                                         │
│  ┌──────────┐  ┌──────────┐           │
│  │ ARCHITECT│  │ REVIEWER │           │
│  └──────────┘  └──────────┘           │
│  ┌──────────┐  ┌──────────┐           │
│  │DOCUMENTER│  │ HARDENER │           │
│  └──────────┘  └──────────┘           │
└─────────────────────────────────────────┘
```

---

## The Four Agents

### 1. ARCHITECT Agent
**Purpose:** Analyze codebase structure and generate architecture graphs

**Input:**
- File tree with classes and functions
- Import relationships between files

**Output:**
```json
{
  "nodes": [
    {
      "id": "main_py",
      "label": "main.py",
      "type": "entry",
      "description": "Application entry point"
    }
  ],
  "edges": [
    {
      "source": "main_py",
      "target": "config_py",
      "relationship": "imports"
    }
  ]
}
```

**Configuration:**
- Model: `ibm/granite-3-8b-instruct`
- Temperature: 0.1
- Max Tokens: 4000
- Max Nodes: 15

---

### 2. REVIEWER Agent
**Purpose:** Identify code quality issues and suggest improvements

**Input:**
- File samples with metadata
- Class and function counts
- Documentation status

**Output:**
```json
{
  "findings": [
    {
      "file": "src/utils.py",
      "line": 42,
      "severity": "HIGH",
      "issue": "Function lacks input validation",
      "suggestion": "Add type checking and bounds validation"
    }
  ]
}
```

**Configuration:**
- Model: `ibm/granite-3-8b-instruct`
- Temperature: 0.1
- Max Tokens: 4000
- Max Findings: 10

---

### 3. DOCUMENTER Agent
**Purpose:** Generate documentation and test stubs for undocumented functions

**Input:**
- List of undocumented functions
- Function parameters

**Output:**
```json
{
  "docs": [
    {
      "function_name": "calculate_score",
      "description": "Calculates health score based on metrics",
      "params": [
        {
          "name": "metrics",
          "type": "dict",
          "description": "Dictionary of metric values"
        }
      ],
      "returns": "Integer score between 0-100",
      "example": "score = calculate_score({'quality': 80})"
    }
  ],
  "tests": [
    {
      "function_name": "calculate_score",
      "test_cases": [
        {
          "description": "Test with valid metrics",
          "input": "{'quality': 80, 'security': 70}",
          "expected": "75"
        }
      ]
    }
  ]
}
```

**Configuration:**
- Model: `ibm/granite-3-8b-instruct`
- Temperature: 0.1
- Max Tokens: 4000

---

### 4. HARDENER Agent
**Purpose:** Find security vulnerabilities and modernization opportunities

**Input:**
- Codebase summary
- List of imports (for dependency analysis)
- Programming languages used

**Output:**
```json
{
  "security": [
    {
      "issue": "Using deprecated crypto library",
      "severity": "CRITICAL",
      "file": "src/auth.py",
      "fix": "Replace with cryptography library"
    }
  ],
  "modernization": [
    {
      "pattern": "Using Python 2 style print statements",
      "suggestion": "Migrate to Python 3 print function",
      "effort": "LOW"
    }
  ]
}
```

**Configuration:**
- Model: `ibm/granite-3-8b-instruct`
- Temperature: 0.1
- Max Tokens: 4000
- Max Security Issues: 8
- Max Modernization Items: 5

---

## Environment Configuration

### Required Environment Variables

```bash
# WatsonX Orchestrate
ORCHESTRATE_API_KEY=your_orchestrate_api_key_here
ORCHESTRATE_URL=https://your-orchestrate-instance.ibm.com
ORCHESTRATE_AGENT_ARCHITECT_ID=agent_id_1
ORCHESTRATE_AGENT_REVIEWER_ID=agent_id_2
ORCHESTRATE_AGENT_DOCUMENTER_ID=agent_id_3
ORCHESTRATE_AGENT_HARDENER_ID=agent_id_4

# Optional
ORCHESTRATE_TIMEOUT=120
ORCHESTRATE_MODEL_ID=ibm/granite-3-8b-instruct
```

### Getting Agent IDs

1. Log into IBM WatsonX Orchestrate
2. Navigate to "Agents" section
3. Create each agent with the configurations above
4. Copy the agent ID from the agent details page
5. Add to your `.env` file

---

## API Client Usage

### Basic Usage

```python
from orchestrate_client import get_orchestrate_client

# Get client instance
client = get_orchestrate_client()

# Call an agent
prompt = "Analyze this codebase..."
result = await client.call_architect_agent(prompt)
```

### Error Handling

The client handles several error types:

- **TimeoutError**: Agent took too long to respond
- **ValueError**: Authentication failed or invalid response
- **ConnectionError**: Network issues or server errors

```python
try:
    result = await client.call_reviewer_agent(prompt)
except TimeoutError:
    # Handle timeout
    pass
except ValueError as e:
    # Handle auth or parsing errors
    pass
except ConnectionError as e:
    # Handle network errors
    pass
```

---

## Agent Prompt Guidelines

### Critical Rules for All Agents

1. **JSON Only**: Agents MUST return valid JSON with no markdown code blocks
2. **No Explanations**: No additional text before or after JSON
3. **Consistent Structure**: Always follow the exact schema
4. **Valid Enums**: Use only specified enum values (LOW/MEDIUM/HIGH/CRITICAL, etc.)

### Example of GOOD Response

```json
{
  "findings": [
    {
      "file": "main.py",
      "line": 10,
      "severity": "HIGH",
      "issue": "Missing error handling",
      "suggestion": "Add try-except block"
    }
  ]
}
```

### Example of BAD Response

```markdown
Here's the analysis:

```json
{
  "findings": [...]
}
```

The code has several issues...
```

---

## Testing Agents

### Test Each Agent Individually

```python
# Test ARCHITECT
prompt = """
Analyze this codebase structure:
{
  "files": [
    {"path": "main.py", "classes": ["App"], "functions": ["main"]}
  ]
}
"""
result = await client.call_architect_agent(prompt)
assert "nodes" in result
assert "edges" in result
```

### Validation Checklist

- [ ] Response is valid JSON
- [ ] No markdown code blocks
- [ ] All required fields present
- [ ] Enum values are valid
- [ ] Arrays are not empty (when data exists)
- [ ] IDs in edges reference valid nodes

---

## Integration with Backend

### Flow Diagram

```
1. POST /analyze
   ↓
2. orchestrate_analysis() in orchestrate.py
   ↓
3. parse_codebase() - Parse files
   ↓
4. generate_architecture() - Call ARCHITECT agent
   ↓
5. generate_review() - Call REVIEWER agent
   ↓
6. generate_docs() - Call DOCUMENTER agent
   ↓
7. generate_security() - Call HARDENER agent
   ↓
8. generate_score() - Calculate final score (uses watsonx.ai directly)
   ↓
9. Return complete AnalysisResult
```

### Error Handling Strategy

Each agent call is wrapped with error handling:

```python
async def _run_stage_with_error_handling(
    job_id: str,
    step_index: int,
    stage_name: str,
    stage_func: Callable,
    *args, **kwargs
) -> Optional[Any]:
    try:
        result = await stage_func(*args, **kwargs)
        return result
    except TimeoutError:
        set_job_error(job_id, "Agent timeout")
        return None
    except ValueError:
        set_job_error(job_id, "Invalid JSON")
        return None
```

---

## Performance Considerations

### Timeouts

- Default: 120 seconds per agent
- Configurable via `ORCHESTRATE_TIMEOUT`
- Total analysis time: ~8-10 minutes for medium codebase

### Rate Limiting

- Orchestrate may have rate limits
- Consider implementing retry logic with exponential backoff
- Cache results when possible

### Optimization Tips

1. **Limit Input Size**: Use MAX_FILES_* constants to limit data sent to agents
2. **Parallel Calls**: Agents 1-4 could potentially run in parallel (future optimization)
3. **Caching**: Cache agent responses for identical inputs

---

## Troubleshooting

### Common Issues

**Issue: "Agent not found" error**
- Solution: Verify agent IDs in `.env` file
- Check that agents exist in Orchestrate platform

**Issue: "Invalid JSON response"**
- Solution: Review agent system instructions
- Ensure "Return ONLY valid JSON" is emphasized
- Test agent directly in Orchestrate UI

**Issue: Timeout errors**
- Solution: Increase `ORCHESTRATE_TIMEOUT`
- Reduce input size (fewer files)
- Check Orchestrate platform status

**Issue: Authentication failed**
- Solution: Verify `ORCHESTRATE_API_KEY`
- Check API key hasn't expired
- Ensure correct permissions

---

## Next Steps for P2

### Phase 1: Agent Creation (Hours 0-4)
- [ ] Create 4 agents in Orchestrate platform
- [ ] Copy agent IDs to `.env` file
- [ ] Test one agent end-to-end

### Phase 2: Agent Tuning (Hours 4-16)
- [ ] Test each agent with sample data
- [ ] Refine prompts for consistent JSON output
- [ ] Validate all enum values
- [ ] Handle edge cases (empty inputs, etc.)

### Phase 3: Integration Testing (Hours 16-22)
- [ ] Test full pipeline with real codebases
- [ ] Verify error handling
- [ ] Document any API quirks
- [ ] Share findings with P1

---

## Resources

- [IBM WatsonX Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/orchestrate)
- [Granite Model Documentation](https://www.ibm.com/granite)
- Backend Code: `backend/src/orchestrate_client.py`
- Agent Wrappers: `backend/src/watsonx.py`

---

**Last Updated:** 2026-05-16  
**Owner:** P2 - Orchestrate Lead  
**Status:** Implementation Ready

# Made with Bob
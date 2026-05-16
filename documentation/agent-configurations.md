# WatsonX Orchestrate Agent Configurations

## Quick Setup Guide for P2

This document contains the **exact configurations** to use when creating the 4 agents in IBM WatsonX Orchestrate.

---

## Agent 1: RepoSense Architect

### Basic Settings
- **Name:** `RepoSense Architect`
- **Description:** `Analyzes codebase structure and generates architecture graphs showing modules and their relationships`
- **Model:** `ibm/granite-3-8b-instruct`
- **Temperature:** `0.1`
- **Max Tokens:** `4000`
- **Top P:** `1.0`

### System Instructions

```
You are a software architect analyzing a codebase.
Given a file tree and import relationships, identify the main modules, their purpose, and how they connect to each other.

Output ONLY valid JSON. No markdown, no explanation, no code blocks.

Required JSON structure:
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

Rules:
- Maximum 15 nodes
- Focus on main architectural components
- Use clear, descriptive labels
- Ensure all edge source/target IDs exist in nodes
- type must be exactly one of: entry, service, util, config, test
- relationship must be exactly one of: imports, extends, calls
```

### Test Input
```
Analyze this codebase structure:

Codebase Summary:
[
  {
    "path": "src/main.py",
    "language": "python",
    "classes": ["Application"],
    "functions": ["main", "setup"],
    "imports": ["config", "utils"]
  },
  {
    "path": "src/config.py",
    "language": "python",
    "classes": ["Settings"],
    "functions": [],
    "imports": []
  }
]

Import Graph:
{
  "src/main.py": ["src/config.py", "src/utils.py"],
  "src/utils.py": ["src/config.py"]
}
```

### Expected Output Format
```json
{
  "nodes": [
    {
      "id": "main_py",
      "label": "main.py",
      "type": "entry",
      "description": "Application entry point and initialization"
    },
    {
      "id": "config_py",
      "label": "config.py",
      "type": "config",
      "description": "Application configuration and settings"
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

---

## Agent 2: RepoSense Reviewer

### Basic Settings
- **Name:** `RepoSense Reviewer`
- **Description:** `Reviews code quality and identifies issues with specific suggestions for improvement`
- **Model:** `ibm/granite-3-8b-instruct`
- **Temperature:** `0.1`
- **Max Tokens:** `4000`
- **Top P:** `1.0`

### System Instructions

```
You are a senior code reviewer with 10 years experience.
Analyze the given code chunks and identify real, specific issues.
Focus on logic errors, missing validation, bad patterns.

Output ONLY valid JSON. No markdown, no explanation, no code blocks.

Required JSON structure:
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

Rules:
- Maximum 10 findings
- Be specific with file paths and line numbers
- Focus on actionable issues
- Prioritize by severity
- severity must be exactly one of: LOW, MEDIUM, HIGH, CRITICAL
- Provide concrete, implementable suggestions
```

### Test Input
```
Review this codebase:

Codebase Files:
[
  {
    "path": "src/auth.py",
    "language": "python",
    "classes": 2,
    "functions": 5,
    "has_docstrings": false
  },
  {
    "path": "src/utils.py",
    "language": "python",
    "classes": 0,
    "functions": 8,
    "has_docstrings": true
  }
]
```

### Expected Output Format
```json
{
  "findings": [
    {
      "file": "src/auth.py",
      "line": 15,
      "severity": "HIGH",
      "issue": "Password validation missing length check",
      "suggestion": "Add minimum password length validation of 8 characters"
    },
    {
      "file": "src/auth.py",
      "line": 1,
      "severity": "MEDIUM",
      "issue": "Missing docstrings for all functions",
      "suggestion": "Add docstrings describing parameters and return values"
    }
  ]
}
```

---

## Agent 3: RepoSense Documenter

### Basic Settings
- **Name:** `RepoSense Documenter`
- **Description:** `Generates documentation and unit test stubs for undocumented functions`
- **Model:** `ibm/granite-3-8b-instruct`
- **Temperature:** `0.1`
- **Max Tokens:** `4000`
- **Top P:** `1.0`

### System Instructions

```
You are a technical writer generating developer documentation.
Given functions and classes, write clear documentation and unit test stubs covering the main cases.

Output ONLY valid JSON. No markdown, no explanation, no code blocks.

Required JSON structure:
{
  "docs": [
    {
      "function_name": "string",
      "description": "string",
      "params": [
        {
          "name": "string",
          "type": "string",
          "description": "string"
        }
      ],
      "returns": "string",
      "example": "code example string"
    }
  ],
  "tests": [
    {
      "function_name": "string",
      "test_cases": [
        {
          "description": "string",
          "input": "string",
          "expected": "string"
        }
      ]
    }
  ]
}

Rules:
- Focus on undocumented functions
- Provide practical examples
- Include edge cases in tests
- Be concise but complete
```

### Test Input
```
Generate documentation for these functions:

Functions:
[
  {
    "function_name": "calculate_score",
    "file": "src/scoring.py",
    "params": ["metrics", "weights"]
  },
  {
    "function_name": "validate_input",
    "file": "src/validation.py",
    "params": ["data", "schema"]
  }
]
```

### Expected Output Format
```json
{
  "docs": [
    {
      "function_name": "calculate_score",
      "description": "Calculates weighted score based on provided metrics",
      "params": [
        {
          "name": "metrics",
          "type": "dict",
          "description": "Dictionary of metric names to values"
        },
        {
          "name": "weights",
          "type": "dict",
          "description": "Dictionary of metric names to weight multipliers"
        }
      ],
      "returns": "Float value representing the weighted score",
      "example": "score = calculate_score({'quality': 80}, {'quality': 0.5})"
    }
  ],
  "tests": [
    {
      "function_name": "calculate_score",
      "test_cases": [
        {
          "description": "Test with valid metrics and weights",
          "input": "metrics={'quality': 80}, weights={'quality': 0.5}",
          "expected": "40.0"
        },
        {
          "description": "Test with empty metrics",
          "input": "metrics={}, weights={}",
          "expected": "0.0"
        }
      ]
    }
  ]
}
```

---

## Agent 4: RepoSense Hardener

### Basic Settings
- **Name:** `RepoSense Hardener`
- **Description:** `Identifies security vulnerabilities and suggests modernization improvements`
- **Model:** `ibm/granite-3-8b-instruct`
- **Temperature:** `0.1`
- **Max Tokens:** `4000`
- **Top P:** `1.0`

### System Instructions

```
You are a security and modernization expert.
Find real security vulnerabilities and outdated code patterns.
Be specific — reference actual files and patterns found.

Output ONLY valid JSON. No markdown, no explanation, no code blocks.

Required JSON structure:
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

Rules:
- Maximum 8 security issues
- Maximum 5 modernization items
- Be specific about vulnerabilities
- Provide actionable fixes
- severity must be exactly one of: LOW, MEDIUM, HIGH, CRITICAL
- effort must be exactly one of: LOW, MEDIUM, HIGH
```

### Test Input
```
Analyze this codebase for security issues:

Codebase Summary:
{
  "total_files": 15,
  "languages": ["python", "javascript"],
  "sample_imports": [
    "flask",
    "requests",
    "sqlite3",
    "pickle",
    "eval"
  ]
}
```

### Expected Output Format
```json
{
  "security": [
    {
      "issue": "Using pickle for deserialization can execute arbitrary code",
      "severity": "CRITICAL",
      "file": "src/data_loader.py",
      "fix": "Replace pickle with json or use safe serialization library"
    },
    {
      "issue": "SQL queries may be vulnerable to injection",
      "severity": "HIGH",
      "file": "src/database.py",
      "fix": "Use parameterized queries or ORM"
    }
  ],
  "modernization": [
    {
      "pattern": "Using deprecated Flask methods",
      "suggestion": "Update to Flask 3.0 API patterns",
      "effort": "MEDIUM"
    },
    {
      "pattern": "Python 2 style string formatting",
      "suggestion": "Migrate to f-strings",
      "effort": "LOW"
    }
  ]
}
```

---

## Validation Checklist

After creating each agent, test with the provided test inputs and verify:

### For All Agents
- [ ] Response is valid JSON (use JSON validator)
- [ ] No markdown code blocks (```json or ```)
- [ ] No explanatory text before or after JSON
- [ ] All required fields are present
- [ ] Field types match schema (string, number, array, object)

### Agent-Specific Checks

**ARCHITECT:**
- [ ] All node IDs are unique
- [ ] All edge source/target IDs reference existing nodes
- [ ] Node types are valid enums (entry, service, util, config, test)
- [ ] Edge relationships are valid enums (imports, extends, calls)

**REVIEWER:**
- [ ] Severity values are valid (LOW, MEDIUM, HIGH, CRITICAL)
- [ ] Line numbers are positive integers
- [ ] File paths are strings
- [ ] Issues and suggestions are non-empty

**DOCUMENTER:**
- [ ] All functions have docs and tests
- [ ] Param arrays contain objects with name, type, description
- [ ] Test cases have description, input, expected
- [ ] Examples are valid code strings

**HARDENER:**
- [ ] Severity values are valid (LOW, MEDIUM, HIGH, CRITICAL)
- [ ] Effort values are valid (LOW, MEDIUM, HIGH)
- [ ] Security issues have file references
- [ ] Fixes are actionable

---

## Common Issues and Fixes

### Issue: Agent returns markdown code blocks

**Bad Response:**
```
Here's the analysis:
```json
{"nodes": [...]}
```
```

**Fix:** Update system instructions to emphasize:
```
Output ONLY valid JSON. No markdown, no explanation, no code blocks.
Do not wrap the JSON in ```json or ``` markers.
```

### Issue: Agent adds explanatory text

**Bad Response:**
```
Based on the analysis, here are the findings:
{"findings": [...]}
```

**Fix:** Add to system instructions:
```
Return ONLY the JSON object. No text before or after.
Start your response with { and end with }
```

### Issue: Invalid enum values

**Bad Response:**
```json
{"severity": "high"}  // Should be "HIGH"
```

**Fix:** Emphasize in system instructions:
```
severity must be EXACTLY one of: LOW, MEDIUM, HIGH, CRITICAL (all uppercase)
```

---

## Next Steps

1. **Create Agents** (30 minutes)
   - Create all 4 agents in Orchestrate
   - Copy configurations exactly as shown above
   - Save agent IDs

2. **Test Each Agent** (2 hours)
   - Use test inputs provided
   - Verify output format
   - Refine prompts if needed

3. **Update .env** (5 minutes)
   - Add all agent IDs to `.env` file
   - Verify API key and URL

4. **Integration Test** (1 hour)
   - Run backend with real codebase
   - Check all agents respond correctly
   - Verify error handling

---

**Created:** 2026-05-16  
**Owner:** P2 - Orchestrate Lead  
**Status:** Ready for Implementation

# Made with Bob
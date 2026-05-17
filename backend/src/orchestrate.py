"""
RepoSense Orchestration Logic
Coordinates the entire analysis pipeline using watsonx Orchestrate agents
"""

import json
import logging
from typing import Optional, Callable, Any, Awaitable

from .models import (
    AnalysisResult,
    AnalysisError,
    ErrorCode,
    StepStatus,
    ParsedCodebase,
    ArchitectureGraph,
    GraphNode,
    GraphEdge,
    NodeType,
    EdgeRelationship,
    CodeReview,
    CodeReviewFinding,
    Severity,
    Documentation,
    DocEntry,
    DocParam,
    TestEntry,
    TestCase,
    SecurityReport,
    SecurityIssue,
    ModernizationItem,
    Effort
)
from .jobs import (
    update_job_progress,
    set_job_result,
    set_job_error
)
from .parser import parse_codebase
from .orchestrate_client import get_orchestrate_client
from .watsonx import generate_score
from .config import settings

logger = logging.getLogger(__name__)


async def _run_stage_with_error_handling(
    job_id: str,
    step_index: int,
    stage_name: str,
    stage_func: Callable[..., Awaitable[Any]],
    *args: Any,
    **kwargs: Any
) -> Optional[Any]:
    """
    Execute a stage with standardized error handling.

    Args:
        job_id: The job ID for tracking
        step_index: Index of the progress step
        stage_name: Human-readable stage name for error messages
        stage_func: Async function to execute
        *args: Positional arguments for stage_func
        **kwargs: Keyword arguments for stage_func

    Returns:
        Result from stage_func, or None if error occurred
    """
    update_job_progress(job_id, step_index, StepStatus.active)

    try:
        result = await stage_func(*args, **kwargs)
        update_job_progress(job_id, step_index, StepStatus.done)
        return result

    except TimeoutError as e:
        logger.error(f"{stage_name} timed out: {str(e)}")
        error = AnalysisError(
            code=ErrorCode.AGENT_TIMEOUT,
            message=f"{stage_name} timed out",
            stage=stage_name
        )
        set_job_error(job_id, error)
        update_job_progress(job_id, step_index, StepStatus.active)
        return None

    except ValueError as e:
        error_msg = str(e)
        if "json" in error_msg.lower() or "parse" in error_msg.lower():
            logger.error(f"{stage_name} invalid JSON: {error_msg}")
            error = AnalysisError(
                code=ErrorCode.AGENT_INVALID_JSON,
                message=f"Invalid JSON response: {error_msg}",
                stage=stage_name
            )
        else:
            logger.error(f"{stage_name} validation error: {error_msg}")
            error = AnalysisError(
                code=ErrorCode.UNKNOWN,
                message=f"Validation error: {error_msg}",
                stage=stage_name
            )
        set_job_error(job_id, error)
        update_job_progress(job_id, step_index, StepStatus.active)
        return None

    except Exception as e:
        logger.error(f"{stage_name} error: {str(e)}", exc_info=True)
        error = AnalysisError(
            code=ErrorCode.WATSONX_UNAVAILABLE,
            message=f"WatsonX API error: {str(e)}",
            stage=stage_name
        )
        set_job_error(job_id, error)
        update_job_progress(job_id, step_index, StepStatus.active)
        return None


async def _generate_architecture(parsed_codebase: ParsedCodebase) -> ArchitectureGraph:
    """Generate architecture graph using the ARCHITECT Orchestrate agent."""
    file_summary = []
    for file in parsed_codebase.files[:20]:
        file_summary.append({
            "path": file.path,
            "language": file.language,
            "classes": [c.name for c in file.classes],
            "functions": [f.name for f in file.functions],
            "imports": file.imports[:10]
        })

    import_graph_sample = dict(list(parsed_codebase.import_graph.items())[:10])

    prompt = f"""You are a software architect analyzing a codebase.
Given a file tree and import relationships, identify the main modules, their purpose,
and how they connect to each other.

Codebase Summary:
{json.dumps(file_summary, indent=2)}

Import Graph (sample):
{json.dumps(import_graph_sample, indent=2)}

Output ONLY valid JSON. No markdown, no explanation:
{{
  "nodes": [
    {{
      "id": "string",
      "label": "filename.py",
      "type": "entry|service|util|config|test",
      "description": "one sentence description"
    }}
  ],
  "edges": [
    {{
      "source": "string",
      "target": "string",
      "relationship": "imports|extends|calls"
    }}
  ]
}}"""

    client = get_orchestrate_client()
    data = await client.call_architect_agent(prompt)

    nodes = []
    for node_data in data.get("nodes", []):
        nodes.append(GraphNode(
            id=node_data["id"],
            label=node_data["label"],
            type=NodeType(node_data["type"]),
            description=node_data["description"]
        ))

    edges = []
    for edge_data in data.get("edges", []):
        edges.append(GraphEdge(
            source=edge_data["source"],
            target=edge_data["target"],
            relationship=EdgeRelationship(edge_data["relationship"])
        ))

    return ArchitectureGraph(nodes=nodes, edges=edges)


async def _generate_review(parsed_codebase: ParsedCodebase) -> CodeReview:
    """Generate code review findings using the REVIEWER Orchestrate agent."""
    file_samples = []
    for file in parsed_codebase.files[:10]:
        file_samples.append({
            "path": file.path,
            "language": file.language,
            "classes": len(file.classes),
            "functions": len(file.functions),
            "has_docstrings": (
                any(c.docstring for c in file.classes)
                or any(f.docstring for f in file.functions)
            )
        })

    prompt = f"""You are a senior code reviewer with 10 years experience.
Analyze the given code chunks and identify real, specific issues.
Focus on logic errors, missing validation, bad patterns.

Codebase Files (sample):
{json.dumps(file_samples, indent=2)}

Output ONLY valid JSON. No markdown, no explanation:
{{
  "findings": [
    {{
      "file": "string",
      "line": 1,
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "issue": "specific description of the problem",
      "suggestion": "concrete fix suggestion"
    }}
  ]
}}"""

    client = get_orchestrate_client()
    data = await client.call_reviewer_agent(prompt)

    findings = []
    for finding_data in data.get("findings", []):
        findings.append(CodeReviewFinding(
            file=finding_data["file"],
            line=finding_data["line"],
            severity=Severity(finding_data["severity"]),
            issue=finding_data["issue"],
            suggestion=finding_data["suggestion"]
        ))

    return CodeReview(findings=findings)


async def _generate_docs(parsed_codebase: ParsedCodebase) -> Documentation:
    """Generate documentation using the DOCUMENTER Orchestrate agent."""
    undocumented = []
    for file in parsed_codebase.files[:5]:
        for func in file.functions[:3]:
            if not func.docstring:
                undocumented.append({
                    "function_name": func.name,
                    "file": file.path,
                    "params": func.params
                })

    if not undocumented:
        return Documentation(docs=[], tests=[])

    prompt = f"""You are a technical writer generating developer documentation.
Given functions and classes, write clear documentation and unit test stubs
covering the main cases.

Functions:
{json.dumps(undocumented, indent=2)}

Output ONLY valid JSON. No markdown, no explanation:
{{
  "docs": [
    {{
      "function_name": "string",
      "description": "string",
      "params": [{{"name": "string", "type": "string", "description": "string"}}],
      "returns": "string",
      "example": "code example string"
    }}
  ],
  "tests": [
    {{
      "function_name": "string",
      "test_cases": [
        {{"description": "string", "input": "string", "expected": "string"}}
      ]
    }}
  ]
}}"""

    client = get_orchestrate_client()
    data = await client.call_documenter_agent(prompt)

    docs = []
    for doc_data in data.get("docs", []):
        params = [
            DocParam(name=p["name"], type=p["type"], description=p["description"])
            for p in doc_data.get("params", [])
        ]
        docs.append(DocEntry(
            function_name=doc_data["function_name"],
            description=doc_data["description"],
            params=params,
            returns=doc_data["returns"],
            example=doc_data["example"]
        ))

    tests = []
    for test_data in data.get("tests", []):
        test_cases = [
            TestCase(
                description=tc["description"],
                input=tc["input"],
                expected=tc["expected"]
            )
            for tc in test_data.get("test_cases", [])
        ]
        tests.append(TestEntry(
            function_name=test_data["function_name"],
            test_cases=test_cases
        ))

    return Documentation(docs=docs, tests=tests)


async def _generate_security(parsed_codebase: ParsedCodebase) -> SecurityReport:
    """Generate security report using the HARDENER Orchestrate agent."""
    all_imports: list = []
    for file in parsed_codebase.files:
        all_imports.extend(file.imports)

    summary = {
        "total_files": len(parsed_codebase.files),
        "languages": list({f.language for f in parsed_codebase.files}),
        "sample_imports": list(set(all_imports))[:30]
    }

    prompt = f"""You are a security and modernization expert.
Find real security vulnerabilities and outdated code patterns.
Be specific — reference actual files and patterns found.

Codebase Summary:
{json.dumps(summary, indent=2)}

Output ONLY valid JSON. No markdown, no explanation:
{{
  "security": [
    {{
      "issue": "specific issue description",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "file": "string",
      "fix": "concrete fix description"
    }}
  ],
  "modernization": [
    {{
      "pattern": "what the outdated pattern is",
      "suggestion": "what to replace it with",
      "effort": "LOW|MEDIUM|HIGH"
    }}
  ]
}}"""

    client = get_orchestrate_client()
    data = await client.call_hardener_agent(prompt)

    security = []
    for issue_data in data.get("security", []):
        security.append(SecurityIssue(
            issue=issue_data["issue"],
            severity=Severity(issue_data["severity"]),
            file=issue_data["file"],
            fix=issue_data["fix"]
        ))

    modernization = []
    for mod_data in data.get("modernization", []):
        modernization.append(ModernizationItem(
            pattern=mod_data["pattern"],
            suggestion=mod_data["suggestion"],
            effort=Effort(mod_data["effort"])
        ))

    return SecurityReport(security=security, modernization=modernization)


async def orchestrate_analysis(job_id: str, local_path: str) -> None:
    """
    Main orchestration function that coordinates the entire analysis pipeline.

    Pipeline stages:
    1. Parse codebase
    2. Generate architecture graph (ARCHITECT agent)
    3. Generate code review (REVIEWER agent)
    4. Generate documentation (DOCUMENTER agent)
    5. Generate security report (HARDENER agent)
    6. Compute health score (watsonx.ai)

    Args:
        job_id: The job ID for tracking progress
        local_path: Path to the local codebase to analyze
    """
    import asyncio

    timeout = settings.analysis_timeout

    try:
        await asyncio.wait_for(
            _orchestrate_analysis_impl(job_id, local_path),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Analysis timed out after {timeout} seconds")
        error = AnalysisError(
            code=ErrorCode.AGENT_TIMEOUT,
            message=f"Overall analysis timed out after {timeout} seconds",
            stage="Overall orchestration"
        )
        set_job_error(job_id, error)
    except Exception as e:
        logger.error(f"Unexpected error in orchestration: {str(e)}", exc_info=True)
        error = AnalysisError(
            code=ErrorCode.UNKNOWN,
            message=f"Unexpected error: {str(e)}",
            stage="Unknown"
        )
        set_job_error(job_id, error)


async def _orchestrate_analysis_impl(job_id: str, local_path: str) -> None:
    """
    Internal implementation of the orchestration logic.

    Args:
        job_id: The job ID for tracking progress
        local_path: Path to the local codebase to analyze
    """
    try:
        # Stage 0: Parse codebase
        update_job_progress(job_id, 0, StepStatus.active)
        try:
            parsed_codebase = await parse_codebase(local_path, job_id)
            update_job_progress(job_id, 0, StepStatus.done)
        except Exception as e:
            logger.error(f"Failed to parse codebase: {str(e)}", exc_info=True)
            error = AnalysisError(
                code=ErrorCode.PARSE_FAILED,
                message=f"Failed to parse codebase: {str(e)}",
                stage="Parsing codebase"
            )
            set_job_error(job_id, error)
            return

        # Stage 1: Generate architecture graph via ARCHITECT agent
        architecture = await _run_stage_with_error_handling(
            job_id, 1, "Analyzing architecture",
            _generate_architecture, parsed_codebase
        )
        if architecture is None:
            return

        # Stage 2: Generate code review via REVIEWER agent
        review = await _run_stage_with_error_handling(
            job_id, 2, "Reviewing code quality",
            _generate_review, parsed_codebase
        )
        if review is None:
            return

        # Stage 3: Generate documentation via DOCUMENTER agent
        docs = await _run_stage_with_error_handling(
            job_id, 3, "Generating documentation",
            _generate_docs, parsed_codebase
        )
        if docs is None:
            return

        # Stage 4: Generate security report via HARDENER agent
        security = await _run_stage_with_error_handling(
            job_id, 4, "Scanning security",
            _generate_security, parsed_codebase
        )
        if security is None:
            return

        # Stage 5: Compute health score via watsonx.ai (P3's domain)
        score = await _run_stage_with_error_handling(
            job_id, 5, "Computing health score",
            generate_score,
            architecture=architecture,
            review=review,
            docs=docs,
            security=security
        )
        if score is None:
            return

        result = AnalysisResult(
            score=score,
            architecture=architecture,
            review=review,
            docs=docs,
            security=security
        )

        set_job_result(job_id, result)

    except Exception as e:
        raise

async def orchestrate_analysis_from_parsed(
    job_id: str,
    parsed_codebase: ParsedCodebase
) -> None:
    """
    Entry point when the codebase was parsed client-side.
    Identical to orchestrate_analysis but skips Stage 0 (parsing).

    Args:
        job_id: The job ID for tracking progress
        parsed_codebase: Already-parsed codebase from the client
    """
    import asyncio

    timeout = settings.analysis_timeout

    try:
        await asyncio.wait_for(
            _orchestrate_analysis_from_parsed_impl(job_id, parsed_codebase),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Analysis timed out after {timeout} seconds")
        error = AnalysisError(
            code=ErrorCode.AGENT_TIMEOUT,
            message=f"Overall analysis timed out after {timeout} seconds",
            stage="Overall orchestration"
        )
        set_job_error(job_id, error)
    except Exception as e:
        logger.error(f"Unexpected error in orchestration: {str(e)}", exc_info=True)
        error = AnalysisError(
            code=ErrorCode.UNKNOWN,
            message=f"Unexpected error: {str(e)}",
            stage="Unknown"
        )
        set_job_error(job_id, error)


async def _orchestrate_analysis_from_parsed_impl(
    job_id: str,
    parsed_codebase: ParsedCodebase
) -> None:
    """
    Internal implementation that accepts a pre-parsed codebase.
    Stage 0 is skipped — it is immediately marked done.
    Stages 1-5 are identical to _orchestrate_analysis_impl.
    """
    try:
        # Stage 0: Skipped — mark done immediately
        update_job_progress(job_id, 0, StepStatus.done)

        # Stage 1: Generate architecture graph via ARCHITECT agent
        architecture = await _run_stage_with_error_handling(
            job_id, 1, "Analyzing architecture",
            _generate_architecture, parsed_codebase
        )
        if architecture is None:
            return

        # Stage 2: Generate code review via REVIEWER agent
        review = await _run_stage_with_error_handling(
            job_id, 2, "Reviewing code quality",
            _generate_review, parsed_codebase
        )
        if review is None:
            return

        # Stage 3: Generate documentation via DOCUMENTER agent
        docs = await _run_stage_with_error_handling(
            job_id, 3, "Generating documentation",
            _generate_docs, parsed_codebase
        )
        if docs is None:
            return

        # Stage 4: Generate security report via HARDENER agent
        security = await _run_stage_with_error_handling(
            job_id, 4, "Scanning security",
            _generate_security, parsed_codebase
        )
        if security is None:
            return

        # Stage 5: Compute health score via watsonx.ai
        score = await _run_stage_with_error_handling(
            job_id, 5, "Computing health score",
            generate_score,
            architecture=architecture,
            review=review,
            docs=docs,
            security=security
        )
        if score is None:
            return

        result = AnalysisResult(
            score=score,
            architecture=architecture,
            review=review,
            docs=docs,
            security=security
        )

        set_job_result(job_id, result)

    except Exception as e:
        raise

# Made with Bob

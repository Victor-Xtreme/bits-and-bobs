"""
RepoSense WatsonX AI Integration
Handles all interactions with IBM WatsonX Orchestrate for AI-powered analysis
"""

import json
import asyncio
import logging
from typing import Any, Dict

from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from .models import (
    ParsedCodebase,
    ArchitectureGraph,
    CodeReview,
    Documentation,
    SecurityReport,
    HealthScore,
    GraphNode,
    GraphEdge,
    CodeReviewFinding,
    DocEntry,
    TestEntry,
    SecurityIssue,
    ModernizationItem,
    ScoreBreakdown,
    NodeType,
    EdgeRelationship,
    Severity,
    Effort,
    Grade
)
from .config import settings
from .orchestrate_client import get_orchestrate_client

# Constants for AI analysis limits
MAX_FILES_FOR_ARCHITECTURE = 20
MAX_IMPORTS_PER_FILE = 10
MAX_FILES_FOR_REVIEW = 10
MAX_UNDOCUMENTED_FUNCTIONS_FILES = 5
MAX_FUNCTIONS_PER_FILE = 3
MAX_SAMPLE_IMPORTS = 30
MAX_ARCHITECTURE_NODES = 15
MAX_REVIEW_FINDINGS = 10
MAX_SECURITY_ISSUES = 8
MAX_MODERNIZATION_ITEMS = 5

logger = logging.getLogger(__name__)


def _get_watsonx_model() -> Model:
    """
    Create and return a WatsonX Model instance.
    
    Returns:
        Configured Model instance
    """
    credentials = {
        "url": settings.watsonx_url,
        "apikey": settings.watsonx_api_key
    }
    
    project_id = settings.watsonx_project_id
    
    model = Model(
        model_id=settings.watsonx_model_id,
        credentials=credentials,
        project_id=project_id,
        params={
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 4000,
            GenParams.TEMPERATURE: 0.1,
            GenParams.TOP_P: 1.0,
            GenParams.TOP_K: 50
        }
    )
    
    return model


async def _call_watsonx(prompt: str) -> str:
    """
    Call WatsonX API with a prompt and return the response.
    
    Args:
        prompt: The prompt to send to WatsonX
        
    Returns:
        The generated text response
        
    Raises:
        TimeoutError: If the request times out
        ValueError: For authentication or API errors
        Exception: For other unexpected errors
    """
    model = _get_watsonx_model()
    
    try:
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(None, model.generate_text, prompt),
            timeout=settings.watsonx_timeout
        )
        
        # Ensure response is a string
        if isinstance(response, str):
            return response
        elif isinstance(response, dict):
            # If response is a dict, try to extract the text
            return str(response.get('generated_text', str(response)))
        elif isinstance(response, list):
            # If response is a list, join or take first element
            return str(response[0]) if response else ""
        else:
            return str(response)
    except asyncio.TimeoutError:
        logger.error("WatsonX API request timed out")
        raise TimeoutError("WatsonX API request timed out")
    except ValueError as e:
        # Authentication or API key errors
        logger.error(f"WatsonX authentication error: {str(e)}")
        raise ValueError(f"WatsonX authentication failed: {str(e)}")
    except ConnectionError as e:
        # Network connectivity issues
        logger.error(f"WatsonX connection error: {str(e)}")
        raise ConnectionError(f"Failed to connect to WatsonX: {str(e)}")
    except Exception as e:
        # Log unexpected errors with full context
        logger.error(f"Unexpected WatsonX error: {str(e)}", exc_info=True)
        raise


def _parse_json_response(response: str) -> Dict[str, Any]:
    """
    Parse JSON from WatsonX response, handling markdown code blocks.
    
    Args:
        response: Raw response from WatsonX
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If JSON parsing fails
    """
    # Remove markdown code blocks if present
    response = response.strip()
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    response = response.strip()
    
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {str(e)}")


async def generate_architecture(parsed_codebase: ParsedCodebase) -> ArchitectureGraph:
    """
    Generate architecture graph from parsed codebase using Orchestrate ARCHITECT agent.
    
    Args:
        parsed_codebase: The parsed codebase
        
    Returns:
        ArchitectureGraph with nodes and edges
    """
    # Build a summary of the codebase
    file_summary = []
    for file in parsed_codebase.files[:MAX_FILES_FOR_ARCHITECTURE]:
        file_summary.append({
            "path": file.path,
            "language": file.language,
            "classes": [c.name for c in file.classes],
            "functions": [f.name for f in file.functions],
            "imports": file.imports[:MAX_IMPORTS_PER_FILE]
        })
    
    # Safely handle empty or small import graphs
    import_graph_items = list(parsed_codebase.import_graph.items())
    import_graph_sample = dict(import_graph_items[:MAX_IMPORTS_PER_FILE]) if import_graph_items else {}
    
    prompt = f"""Analyze this codebase structure and generate an architecture graph.

Codebase Summary:
{json.dumps(file_summary, indent=2)}

Import Graph (sample):
{json.dumps(import_graph_sample, indent=2)}

Focus on the main architectural components and their relationships. Limit to {MAX_ARCHITECTURE_NODES} nodes maximum."""

    # Call Orchestrate ARCHITECT agent
    client = get_orchestrate_client()
    data = await client.call_architect_agent(prompt)
    
    # Parse nodes
    nodes = []
    for node_data in data.get("nodes", []):
        nodes.append(GraphNode(
            id=node_data["id"],
            label=node_data["label"],
            type=NodeType(node_data["type"]),
            description=node_data["description"]
        ))
    
    # Parse edges
    edges = []
    for edge_data in data.get("edges", []):
        edges.append(GraphEdge(
            source=edge_data["source"],
            target=edge_data["target"],
            relationship=EdgeRelationship(edge_data["relationship"])
        ))
    
    return ArchitectureGraph(nodes=nodes, edges=edges)


async def generate_review(parsed_codebase: ParsedCodebase) -> CodeReview:
    """
    Generate code review findings from parsed codebase using Orchestrate REVIEWER agent.
    
    Args:
        parsed_codebase: The parsed codebase
        
    Returns:
        CodeReview with findings
    """
    # Sample files for review
    file_samples = []
    for file in parsed_codebase.files[:MAX_FILES_FOR_REVIEW]:
        file_samples.append({
            "path": file.path,
            "language": file.language,
            "classes": len(file.classes),
            "functions": len(file.functions),
            "has_docstrings": any(c.docstring for c in file.classes) or any(f.docstring for f in file.functions)
        })
    
    prompt = f"""Review this codebase and identify code quality issues.

Codebase Files (sample):
{json.dumps(file_samples, indent=2)}

Focus on:
- Missing documentation
- Code complexity
- Naming conventions
- Best practices violations

Limit to {MAX_REVIEW_FINDINGS} most important findings."""

    # Call Orchestrate REVIEWER agent
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


async def generate_docs(parsed_codebase: ParsedCodebase) -> Documentation:
    """
    Generate documentation for key functions using Orchestrate DOCUMENTER agent.
    
    Args:
        parsed_codebase: The parsed codebase
        
    Returns:
        Documentation with doc entries and test entries
    """
    # Collect undocumented functions
    undocumented = []
    for file in parsed_codebase.files[:MAX_UNDOCUMENTED_FUNCTIONS_FILES]:
        for func in file.functions[:MAX_FUNCTIONS_PER_FILE]:
            if not func.docstring:
                undocumented.append({
                    "function_name": func.name,
                    "file": file.path,
                    "params": func.params
                })
    
    if not undocumented:
        # Return empty documentation if all functions are documented
        return Documentation(docs=[], tests=[])
    
    prompt = f"""Generate documentation for these functions.

Functions:
{json.dumps(undocumented, indent=2)}"""

    # Call Orchestrate DOCUMENTER agent
    client = get_orchestrate_client()
    data = await client.call_documenter_agent(prompt)
    
    # Parse docs
    from .models import DocParam, TestCase
    
    docs = []
    for doc_data in data.get("docs", []):
        params = [
            DocParam(
                name=p["name"],
                type=p["type"],
                description=p["description"]
            )
            for p in doc_data.get("params", [])
        ]
        
        docs.append(DocEntry(
            function_name=doc_data["function_name"],
            description=doc_data["description"],
            params=params,
            returns=doc_data["returns"],
            example=doc_data["example"]
        ))
    
    # Parse tests
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


async def generate_security(parsed_codebase: ParsedCodebase) -> SecurityReport:
    """
    Generate security report with issues and modernization suggestions using Orchestrate HARDENER agent.
    
    Args:
        parsed_codebase: The parsed codebase
        
    Returns:
        SecurityReport with security issues and modernization items
    """
    # Build summary for security analysis
    summary = {
        "total_files": len(parsed_codebase.files),
        "languages": list({f.language for f in parsed_codebase.files}),
        "sample_imports": []
    }
    
    # Collect imports for security analysis
    all_imports = []
    for file in parsed_codebase.files:
        all_imports.extend(file.imports)
    
    summary["sample_imports"] = list(set(all_imports))[:MAX_SAMPLE_IMPORTS]
    
    prompt = f"""Analyze this codebase for security issues and modernization opportunities.

Codebase Summary:
{json.dumps(summary, indent=2)}

Focus on:
- Vulnerable dependencies
- Insecure patterns
- Outdated practices
- Missing security features

Limit to {MAX_SECURITY_ISSUES} security issues and {MAX_MODERNIZATION_ITEMS} modernization items."""

    # Call Orchestrate HARDENER agent
    client = get_orchestrate_client()
    data = await client.call_hardener_agent(prompt)
    
    # Parse security issues
    security = []
    for issue_data in data.get("security", []):
        security.append(SecurityIssue(
            issue=issue_data["issue"],
            severity=Severity(issue_data["severity"]),
            file=issue_data["file"],
            fix=issue_data["fix"]
        ))
    
    # Parse modernization items
    modernization = []
    for mod_data in data.get("modernization", []):
        modernization.append(ModernizationItem(
            pattern=mod_data["pattern"],
            suggestion=mod_data["suggestion"],
            effort=Effort(mod_data["effort"])
        ))
    
    return SecurityReport(security=security, modernization=modernization)


async def generate_score(
    architecture: ArchitectureGraph,
    review: CodeReview,
    docs: Documentation,
    security: SecurityReport
) -> HealthScore:
    """
    Generate overall health score based on all analysis results.
    
    Args:
        architecture: Architecture graph
        review: Code review findings
        docs: Documentation
        security: Security report
        
    Returns:
        HealthScore with breakdown and recommendations
    """
    # Build summary for scoring
    summary = {
        "architecture": {
            "nodes": len(architecture.nodes),
            "edges": len(architecture.edges)
        },
        "review": {
            "total_findings": len(review.findings),
            "critical": sum(1 for f in review.findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for f in review.findings if f.severity == Severity.HIGH)
        },
        "docs": {
            "documented_functions": len(docs.docs),
            "test_coverage": len(docs.tests)
        },
        "security": {
            "security_issues": len(security.security),
            "critical_security": sum(1 for s in security.security if s.severity == Severity.CRITICAL),
            "modernization_needed": len(security.modernization)
        }
    }
    
    prompt = f"""You are a code quality analyst. Given analysis from four specialized
agents, produce an overall health scorecard for this codebase.

Architecture analysis: {json.dumps(summary["architecture"], indent=2)}
Code review findings: {json.dumps(summary["review"], indent=2)}
Documentation coverage: {json.dumps(summary["docs"], indent=2)}
Security analysis: {json.dumps(summary["security"], indent=2)}

Score the codebase from 0 to 100:
- Code Quality (30 points): fewer HIGH/CRITICAL review findings = more points
  * Start with 30 points
  * Deduct 5 points per CRITICAL finding
  * Deduct 2 points per HIGH finding
  * Minimum: 0 points
  
- Security (30 points): fewer security issues = more points
  * Start with 30 points
  * Deduct 5 points per CRITICAL security issue
  * Deduct 2 points per HIGH security issue
  * Minimum: 0 points
  
- Documentation (20 points): better coverage = more points
  * 20 points: All functions documented with tests
  * 15 points: Most functions documented
  * 10 points: Some documentation
  * 5 points: Minimal documentation
  * 0 points: No documentation
  
- Architecture (20 points): cleaner, clearer structure = more points
  * 20 points: Clear, well-organized structure
  * 15 points: Good structure with minor issues
  * 10 points: Acceptable structure
  * 5 points: Poor organization
  * 0 points: Chaotic structure

Return ONLY valid JSON. No markdown, no explanation:
{{
  "score": number,
  "grade": "A|B|C|D|F",
  "breakdown": {{
    "quality": number,
    "security": number,
    "documentation": number,
    "architecture": number
  }},
  "summary": "2-3 sentences describing this codebase honestly",
  "top_priorities": [
    "Most important thing to fix first",
    "Second most important",
    "Third most important"
  ]
}}

Grade mapping:
- A: 90-100 (Excellent)
- B: 80-89 (Good)
- C: 70-79 (Fair)
- D: 60-69 (Poor)
- F: 0-59 (Failing)

IMPORTANT: Be honest and specific in your summary. Avoid generic phrases.
Prioritize fixes by impact - what will improve the codebase most."""

    response = await _call_watsonx(prompt)
    data = _parse_json_response(response)
    
    return HealthScore(
        score=data["score"],
        grade=Grade(data["grade"]),
        breakdown=ScoreBreakdown(
            quality=data["breakdown"]["quality"],
            security=data["breakdown"]["security"],
            documentation=data["breakdown"]["documentation"],
            architecture=data["breakdown"]["architecture"]
        ),
        summary=data["summary"],
        top_priorities=data["top_priorities"]
    )

# Made with Bob

"""
RepoSense Pydantic Models
AI-powered codebase health analysis tool for FastAPI backend
"""

from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class Severity(str, Enum):
    """Severity levels for issues and findings"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NodeType(str, Enum):
    """Types of nodes in the architecture graph"""
    entry = "entry"
    service = "service"
    util = "util"
    config = "config"
    test = "test"


class EdgeRelationship(str, Enum):
    """Types of relationships between nodes in the architecture graph"""
    imports = "imports"
    extends = "extends"
    calls = "calls"


class StepStatus(str, Enum):
    """Status of a progress step"""
    done = "done"
    active = "active"
    pending = "pending"


class Effort(str, Enum):
    """Effort level required for modernization items"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Grade(str, Enum):
    """Letter grades for health score"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class PayloadType(str, Enum):
    """Type of payload in API response"""
    request = "request"
    result = "result"
    error = "error"


class ErrorCode(str, Enum):
    """Error codes for analysis failures"""
    PARSE_FAILED = "PARSE_FAILED"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    AGENT_INVALID_JSON = "AGENT_INVALID_JSON"
    WATSONX_UNAVAILABLE = "WATSONX_UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# REQUEST MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request to analyze a local codebase"""
    local_path: str


# ============================================================================
# PROGRESS TRACKING
# ============================================================================

class ProgressStep(BaseModel):
    """Individual step in the analysis progress"""
    name: str
    status: StepStatus
    files_processed: Optional[int] = None
    files_total: Optional[int] = None
    current_file: Optional[str] = None


# ============================================================================
# PARSED CODEBASE MODELS
# ============================================================================

class ParsedFunction(BaseModel):
    """
    Flat representation of a function.
    id follows pattern: file_path::name for top-level
                       file_path::ClassName::method_name for nested
    parent_id is None for top-level, references parent's id for nested
    """
    id: str
    name: str
    parent_id: Optional[str] = None
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    params: list[str]
    returns: Optional[str] = None


class ParsedClass(BaseModel):
    """
    Flat representation of a class.
    id follows pattern: file_path::name for top-level
                       file_path::ParentClass::NestedClass for nested
    parent_id is None for top-level, references parent's id for nested
    """
    id: str
    name: str
    parent_id: Optional[str] = None
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    bases: list[str]


class ParsedFile(BaseModel):
    """
    Parsed file containing flat lists of all classes and functions.
    All nested items are flattened into these lists with proper id/parent_id.
    """
    path: str
    language: str
    imports: list[str]
    classes: list[ParsedClass]
    functions: list[ParsedFunction]


class ParsedCodebase(BaseModel):
    """
    Complete parsed codebase with import graph.
    import_graph maps file paths to lists of file paths they import.
    """
    files: list[ParsedFile]
    import_graph: dict[str, list[str]]


# ============================================================================
# ARCHITECTURE GRAPH
# ============================================================================

class GraphNode(BaseModel):
    """Node in the architecture graph"""
    id: str
    label: str
    type: NodeType
    description: str


class GraphEdge(BaseModel):
    """Edge connecting two nodes in the architecture graph"""
    source: str
    target: str
    relationship: EdgeRelationship


class ArchitectureGraph(BaseModel):
    """Complete architecture graph with nodes and edges"""
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# ============================================================================
# CODE REVIEW
# ============================================================================

class CodeReviewFinding(BaseModel):
    """Individual code review finding"""
    file: str
    line: int
    severity: Severity
    issue: str
    suggestion: str


class CodeReview(BaseModel):
    """Complete code review with all findings"""
    findings: list[CodeReviewFinding]


# ============================================================================
# DOCUMENTATION
# ============================================================================

class DocParam(BaseModel):
    """Parameter documentation"""
    name: str
    type: str
    description: str


class DocEntry(BaseModel):
    """
    Documentation entry for a function.
    function_name references the function being documented.
    """
    function_name: str
    description: str
    params: list[DocParam]
    returns: str
    example: str


class TestCase(BaseModel):
    """Test case for a function"""
    description: str
    input: str
    expected: str


class TestEntry(BaseModel):
    """
    Test entry for a function.
    function_name references the function being tested.
    """
    function_name: str
    test_cases: list[TestCase]


class Documentation(BaseModel):
    """Complete documentation with doc entries and test entries"""
    docs: list[DocEntry]
    tests: list[TestEntry]


# ============================================================================
# SECURITY
# ============================================================================

class SecurityIssue(BaseModel):
    """Security issue found in the codebase"""
    issue: str
    severity: Severity
    file: str
    fix: str


class ModernizationItem(BaseModel):
    """Modernization suggestion for outdated patterns"""
    pattern: str
    suggestion: str
    effort: Effort


class SecurityReport(BaseModel):
    """Complete security report with issues and modernization items"""
    security: list[SecurityIssue]
    modernization: list[ModernizationItem]


# ============================================================================
# HEALTH SCORE
# ============================================================================

class ScoreBreakdown(BaseModel):
    """Breakdown of health score into four categories"""
    quality: int
    security: int
    documentation: int
    architecture: int


class HealthScore(BaseModel):
    """Overall health score with breakdown and recommendations"""
    score: int
    grade: Grade
    breakdown: ScoreBreakdown
    summary: str
    top_priorities: list[str]


# ============================================================================
# FINAL RESULT
# ============================================================================

class AnalysisResult(BaseModel):
    """Complete analysis result composing all sub-reports"""
    score: HealthScore
    architecture: ArchitectureGraph
    review: CodeReview
    docs: Documentation
    security: SecurityReport


# ============================================================================
# ERROR HANDLING
# ============================================================================

class AnalysisError(BaseModel):
    """Error that occurred during analysis"""
    code: ErrorCode
    message: str
    stage: str


# ============================================================================
# UNIVERSAL API RESPONSE ENVELOPE
# ============================================================================

class ApiResponse(BaseModel):
    """
    Universal envelope for all API responses.
    payload can be either AnalysisResult or AnalysisError.
    """
    type: PayloadType
    job_id: str
    progress: list[ProgressStep]
    payload: Optional[Union[AnalysisResult, AnalysisError]] = None

# Made with Bob

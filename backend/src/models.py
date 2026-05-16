"""
RepoSense Data Models
Pydantic models for request/response validation and data structures
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Enums
class NodeType(str, Enum):
    """Types of nodes in the architecture graph"""
    entry = "entry"
    service = "service"
    util = "util"
    config = "config"
    test = "test"


class EdgeRelationship(str, Enum):
    """Types of relationships between nodes"""
    imports = "imports"
    extends = "extends"
    calls = "calls"


class Severity(str, Enum):
    """Severity levels for issues"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Effort(str, Enum):
    """Effort levels for modernization tasks"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Grade(str, Enum):
    """Health score grades"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class StepStatus(str, Enum):
    """Status of analysis steps"""
    pending = "pending"
    active = "active"
    done = "done"
    error = "error"


class ErrorCode(str, Enum):
    """Error codes for analysis failures"""
    PARSE_FAILED = "PARSE_FAILED"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    AGENT_INVALID_JSON = "AGENT_INVALID_JSON"
    WATSONX_UNAVAILABLE = "WATSONX_UNAVAILABLE"
    ORCHESTRATE_UNAVAILABLE = "ORCHESTRATE_UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


# Parsed Codebase Models
class FunctionInfo(BaseModel):
    """Information about a function"""
    name: str
    params: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    line_start: int
    line_end: int


class ClassInfo(BaseModel):
    """Information about a class"""
    name: str
    methods: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    line_start: int
    line_end: int


class FileInfo(BaseModel):
    """Information about a parsed file"""
    path: str
    language: str
    classes: List[ClassInfo] = Field(default_factory=list)
    functions: List[FunctionInfo] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    line_count: int


class ParsedCodebase(BaseModel):
    """Complete parsed codebase structure"""
    files: List[FileInfo]
    import_graph: Dict[str, List[str]] = Field(default_factory=dict)
    total_files: int
    total_lines: int
    languages: List[str]


# Architecture Models
class GraphNode(BaseModel):
    """Node in the architecture graph"""
    id: str
    label: str
    type: NodeType
    description: str


class GraphEdge(BaseModel):
    """Edge in the architecture graph"""
    source: str
    target: str
    relationship: EdgeRelationship


class ArchitectureGraph(BaseModel):
    """Architecture graph with nodes and edges"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# Code Review Models
class CodeReviewFinding(BaseModel):
    """A code review finding"""
    file: str
    line: int
    severity: Severity
    issue: str
    suggestion: str


class CodeReview(BaseModel):
    """Code review results"""
    findings: List[CodeReviewFinding]


# Documentation Models
class DocParam(BaseModel):
    """Documentation parameter"""
    name: str
    type: str
    description: str


class DocEntry(BaseModel):
    """Documentation entry for a function"""
    function_name: str
    description: str
    params: List[DocParam]
    returns: str
    example: str


class TestCase(BaseModel):
    """Test case for a function"""
    description: str
    input: str
    expected: str


class TestEntry(BaseModel):
    """Test entry for a function"""
    function_name: str
    test_cases: List[TestCase]


class Documentation(BaseModel):
    """Documentation and test generation results"""
    docs: List[DocEntry]
    tests: List[TestEntry]


# Security Models
class SecurityIssue(BaseModel):
    """A security issue"""
    issue: str
    severity: Severity
    file: str
    fix: str


class ModernizationItem(BaseModel):
    """A modernization suggestion"""
    pattern: str
    suggestion: str
    effort: Effort


class SecurityReport(BaseModel):
    """Security and modernization report"""
    security: List[SecurityIssue]
    modernization: List[ModernizationItem]


# Health Score Models
class ScoreBreakdown(BaseModel):
    """Breakdown of health score by category"""
    quality: int = Field(ge=0, le=100)
    security: int = Field(ge=0, le=100)
    documentation: int = Field(ge=0, le=100)
    architecture: int = Field(ge=0, le=100)


class HealthScore(BaseModel):
    """Overall health score"""
    score: int = Field(ge=0, le=100)
    grade: Grade
    breakdown: ScoreBreakdown
    summary: str
    top_priorities: List[str]


# Analysis Result Models
class AnalysisResult(BaseModel):
    """Complete analysis result"""
    score: HealthScore
    architecture: ArchitectureGraph
    review: CodeReview
    docs: Documentation
    security: SecurityReport


class AnalysisError(BaseModel):
    """Analysis error information"""
    code: ErrorCode
    message: str
    stage: str


# API Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request to analyze a repository"""
    repo_path: str = Field(..., description="Path to the local repository")


class ProgressStep(BaseModel):
    """Progress step information"""
    name: str
    status: StepStatus


class JobStatus(BaseModel):
    """Job status information"""
    job_id: str
    status: str
    progress: List[ProgressStep]
    result: Optional[AnalysisResult] = None
    error: Optional[AnalysisError] = None


class AnalyzeResponse(BaseModel):
    """Response from analyze endpoint"""
    job_id: str
    message: str


# Made with Bob
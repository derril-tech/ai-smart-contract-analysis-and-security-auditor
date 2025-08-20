"""
Project and analysis schemas for ChainGuard AI
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum
import re


class ProjectType(str, Enum):
    GIT = "git"
    ZIP = "zip"
    ADDRESS = "address"
    MANUAL = "manual"


class ProjectFramework(str, Enum):
    HARDFORK = "hardhat"
    FOUNDRY = "foundry"
    TRUFFLE = "truffle"
    REMIX = "remix"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AnalysisProfile(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class FindingSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class FindingStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    WONT_FIX = "wont_fix"
    DUPLICATE = "duplicate"


class FindingCategory(str, Enum):
    ACCESS_CONTROL = "access_control"
    ARITHMETIC = "arithmetic"
    REENTRANCY = "reentrancy"
    UNCHECKED_CALLS = "unchecked_calls"
    FRONTRUNNING = "frontrunning"
    ORACLE_MANIPULATION = "oracle_manipulation"
    UPGRADEABILITY = "upgradeability"
    GAS_OPTIMIZATION = "gas_optimization"
    LOGIC_ERROR = "logic_error"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    OTHER = "other"


class ArtifactType(str, Enum):
    TRACE = "trace"
    SARIF = "sarif"
    PDF = "pdf"
    POC = "poc"
    TEST = "test"
    PATCH = "patch"
    COVERAGE = "coverage"
    GAS_REPORT = "gas_report"
    STORAGE_LAYOUT = "storage_layout"
    BYTECODE = "bytecode"
    ABI = "abi"
    METADATA = "metadata"


# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    project_type: ProjectType
    framework: Optional[ProjectFramework] = None
    source_url: Optional[HttpUrl] = None
    contract_address: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('contract_address')
    def validate_contract_address(cls, v):
        if v is not None:
            # Basic Ethereum address validation
            if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
                raise ValueError("Invalid Ethereum address format")
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[ProjectStatus] = None
    settings: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    id: str
    tenant_id: str
    status: ProjectStatus
    contract_count: int = 0
    run_count: int = 0
    last_run_at: Optional[datetime] = None
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    size: int
    pages: int


# Contract schemas
class ContractBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    path: Optional[str] = None
    version: Optional[str] = None
    license: Optional[str] = None
    bytecode_hash: Optional[str] = None
    source_code: Optional[str] = None
    abi: Optional[Dict[str, Any]] = None
    storage_layout: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ContractCreate(ContractBase):
    project_id: str


class ContractUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    path: Optional[str] = None
    version: Optional[str] = None
    license: Optional[str] = None
    source_code: Optional[str] = None
    abi: Optional[Dict[str, Any]] = None
    storage_layout: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ContractResponse(ContractBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    finding_count: int = 0
    
    class Config:
        from_attributes = True


# Analysis run schemas
class AnalysisRunBase(BaseModel):
    profile: AnalysisProfile
    settings: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list)


class AnalysisRunCreate(AnalysisRunBase):
    project_id: str


class AnalysisRunUpdate(BaseModel):
    status: Optional[RunStatus] = None
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None


class AnalysisRunResponse(AnalysisRunBase):
    id: str
    project_id: str
    status: RunStatus
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    tool_versions: Dict[str, str] = Field(default_factory=dict)
    checkpoints: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisRunListResponse(BaseModel):
    runs: List[AnalysisRunResponse]
    total: int
    page: int
    size: int
    pages: int


# Finding schemas
class CodeSpan(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    start_column: Optional[int] = None
    end_column: Optional[int] = None
    code_snippet: Optional[str] = None


class Evidence(BaseModel):
    type: str
    description: str
    data: Dict[str, Any]
    file_path: Optional[str] = None
    line_number: Optional[int] = None


class Recommendation(BaseModel):
    title: str
    description: str
    impact: str
    effort: str
    priority: str


class Patch(BaseModel):
    diff: str
    description: str
    test_code: Optional[str] = None
    risk_level: str = "low"


class FindingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    severity: FindingSeverity
    category: FindingCategory
    swc_id: Optional[str] = None
    cwe_id: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    code_spans: List[CodeSpan] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    patches: List[Patch] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FindingCreate(FindingBase):
    run_id: str
    contract_id: Optional[str] = None


class FindingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    severity: Optional[FindingSeverity] = None
    status: Optional[FindingStatus] = None
    category: Optional[FindingCategory] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None


class FindingResponse(FindingBase):
    id: str
    run_id: str
    contract_id: Optional[str]
    status: FindingStatus
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    contract: Optional[ContractResponse] = None
    
    class Config:
        from_attributes = True


class FindingListResponse(BaseModel):
    findings: List[FindingResponse]
    total: int
    page: int
    size: int
    pages: int
    severity_counts: Dict[str, int] = Field(default_factory=dict)
    category_counts: Dict[str, int] = Field(default_factory=dict)


# Artifact schemas
class ArtifactBase(BaseModel):
    kind: ArtifactType
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArtifactCreate(ArtifactBase):
    run_id: str


class ArtifactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None


class ArtifactResponse(ArtifactBase):
    id: str
    run_id: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArtifactListResponse(BaseModel):
    artifacts: List[ArtifactResponse]
    total: int


# Custom rule schemas
class CustomRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    pattern: str = Field(..., min_length=1, max_length=1000)
    severity: FindingSeverity
    category: FindingCategory
    enabled: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)


class CustomRuleCreate(CustomRuleBase):
    project_id: str


class CustomRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    pattern: Optional[str] = Field(None, min_length=1, max_length=1000)
    severity: Optional[FindingSeverity] = None
    category: Optional[FindingCategory] = None
    enabled: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class CustomRuleResponse(CustomRuleBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CustomRuleListResponse(BaseModel):
    rules: List[CustomRuleResponse]
    total: int


# Analysis checkpoint schemas
class AnalysisCheckpointBase(BaseModel):
    stage: str
    status: str
    progress: float = Field(..., ge=0.0, le=1.0)
    data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class AnalysisCheckpointCreate(AnalysisCheckpointBase):
    run_id: str


class AnalysisCheckpointResponse(AnalysisCheckpointBase):
    id: str
    run_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Gas report schemas
class GasReport(BaseModel):
    function_name: str
    contract_name: str
    gas_used: int
    gas_limit: Optional[int] = None
    deployment_cost: Optional[int] = None
    execution_cost: Optional[float] = None
    optimization_suggestions: List[str] = Field(default_factory=list)


class CoverageReport(BaseModel):
    file_path: str
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    uncovered_lines: List[int] = Field(default_factory=list)
    uncovered_branches: List[Dict[str, Any]] = Field(default_factory=list)


# Search schemas
class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    filters: Dict[str, Any] = Field(default_factory=dict)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class SearchResult(BaseModel):
    id: str
    type: str
    title: str
    description: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    page: int
    size: int
    pages: int
    query_time_ms: float


# Dashboard schemas
class DashboardStats(BaseModel):
    total_projects: int
    total_runs: int
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    informational_findings: int
    avg_run_duration_minutes: float
    success_rate: float
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)


class ProjectStats(BaseModel):
    project_id: str
    project_name: str
    run_count: int
    finding_count: int
    critical_findings: int
    high_findings: int
    last_run_at: Optional[datetime] = None
    avg_run_duration_minutes: float


# WebSocket schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RunProgressMessage(WebSocketMessage):
    type: str = "run_progress"
    data: Dict[str, Any]  # Contains run_id, progress, status, etc.


class FindingUpdateMessage(WebSocketMessage):
    type: str = "finding_update"
    data: Dict[str, Any]  # Contains finding_id, updates, etc.


# Update forward references
ProjectResponse.model_rebuild()
ContractResponse.model_rebuild()
AnalysisRunResponse.model_rebuild()
FindingResponse.model_rebuild()
ArtifactResponse.model_rebuild()
CustomRuleResponse.model_rebuild()

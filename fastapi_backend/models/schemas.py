"""
Pydantic Schemas for AutoPM API
Request/Response models for validation and serialization
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ProjectStatus(str, Enum):
    PLANNING = "Planning"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"


class IssueType(str, Enum):
    STORY = "Story"
    BUG = "Bug"
    TASK = "Task"
    EPIC = "Epic"


class TaskStatus(str, Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    DONE = "Done"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class PRStatus(str, Enum):
    OPEN = "Open"
    MERGED = "Merged"
    CLOSED = "Closed"


class BuildStatus(str, Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
    PENDING = "Pending"


class DependencyType(str, Enum):
    INTERNAL = "Internal"
    EXTERNAL = "External"


class DependencyStatus(str, Enum):
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    DELAYED = "Delayed"


class AuditResult(str, Enum):
    PASS = "Pass"
    MINOR_NC = "Minor NC"
    MAJOR_NC = "Major NC"


# ============================================================================
# EMPLOYEE SCHEMAS
# ============================================================================

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = None
    team: Optional[str] = None
    skills: Optional[List[str]] = []
    github_username: Optional[str] = None
    jira_email: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    employee_id: str
    password: str
    manager_id: Optional[str] = None


class EmployeeLogin(BaseModel):
    email: EmailStr
    password: str


class EmployeeResponse(EmployeeBase):
    employee_id: str
    manager_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeWithStats(EmployeeResponse):
    assigned_tasks_count: int = 0
    open_prs_count: int = 0
    total_hours_logged: float = 0.0


# ============================================================================
# PROJECT SCHEMAS
# ============================================================================

class ProjectBase(BaseModel):
    project_name: str
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    compliance_standards: Optional[List[str]] = []
    critical_modules: Optional[List[str]] = []
    team_lead_id: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING


class ProjectCreate(ProjectBase):
    project_id: str
    github_repo_name: Optional[str] = None
    jira_project_key: Optional[str] = None


class ProjectResponse(ProjectBase):
    project_id: str
    actual_end_date: Optional[date] = None
    github_repo_name: Optional[str] = None
    jira_project_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectWithStats(ProjectResponse):
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    todo_tasks: int = 0
    critical_tasks: int = 0
    team_lead_name: Optional[str] = None


# ============================================================================
# JIRA TASK SCHEMAS
# ============================================================================

class JiraTaskBase(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[IssueType] = None
    assignee_id: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[Priority] = Priority.MEDIUM
    story_points: Optional[int] = None
    parent_issue_id: Optional[str] = None
    depends_on: Optional[List[str]] = []
    labels: Optional[List[str]] = []


class JiraTaskCreate(JiraTaskBase):
    issue_id: str
    project_id: str


class JiraTaskResponse(JiraTaskBase):
    issue_id: str
    project_id: str
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    github_pr_id: Optional[str] = None
    last_synced_at: datetime
    
    class Config:
        from_attributes = True


class JiraTaskWithDetails(JiraTaskResponse):
    assignee_name: Optional[str] = None
    project_name: Optional[str] = None


# ============================================================================
# GITHUB ACTIVITY SCHEMAS
# ============================================================================

class GitHubActivityBase(BaseModel):
    title: Optional[str] = None
    author_id: Optional[str] = None
    reviewers: Optional[List[str]] = []
    status: Optional[PRStatus] = PRStatus.OPEN
    associated_issue_id: Optional[str] = None
    build_status: Optional[BuildStatus] = BuildStatus.PENDING


class GitHubActivityCreate(GitHubActivityBase):
    pr_id: str
    project_id: str


class GitHubActivityResponse(GitHubActivityBase):
    pr_id: str
    project_id: str
    created_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    changed_files: int = 0
    additions: int = 0
    deletions: int = 0
    comments_count: int = 0
    test_coverage_delta: Optional[float] = None
    last_synced_at: datetime
    
    class Config:
        from_attributes = True


class GitHubActivityWithDetails(GitHubActivityResponse):
    author_name: Optional[str] = None
    project_name: Optional[str] = None


# ============================================================================
# RESOURCE ALLOCATION SCHEMAS
# ============================================================================

class ResourceAllocationBase(BaseModel):
    employee_id: str
    project_id: str
    week_start_date: date
    overtime_hours: float = 0.0
    planned_hours: float = 0.0
    logged_hours: float = 0.0
    task_ids: Optional[List[str]] = []


class ResourceAllocationCreate(ResourceAllocationBase):
    allocation_id: str


class ResourceAllocationResponse(ResourceAllocationBase):
    allocation_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# COMMUNICATION LOG SCHEMAS
# ============================================================================

class TeamCommunicationBase(BaseModel):
    project_id: str
    sender_id: str
    message_text: str = Field(..., max_length=200)
    is_blocker_signal: bool = False


class TeamCommunicationCreate(TeamCommunicationBase):
    message_id: str
    timestamp: datetime


class TeamCommunicationResponse(TeamCommunicationBase):
    message_id: str
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# HISTORICAL PERFORMANCE SCHEMAS
# ============================================================================

class HistoricalPerformanceBase(BaseModel):
    project_name: str
    original_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    delay_days: Optional[int] = None
    defect_density: Optional[float] = None
    integration_issues_count: int = 0
    root_causes: Optional[List[str]] = []
    compliance_audit_result: Optional[AuditResult] = None


class HistoricalPerformanceCreate(HistoricalPerformanceBase):
    historical_project_id: str


class HistoricalPerformanceResponse(HistoricalPerformanceBase):
    historical_project_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# TASK DEPENDENCY SCHEMAS
# ============================================================================

class TaskDependencyBase(BaseModel):
    dependent_task_id: str
    blocking_task_id: str
    dependency_type: DependencyType
    expected_ready_date: Optional[date] = None
    status: DependencyStatus = DependencyStatus.ON_TRACK


class TaskDependencyCreate(TaskDependencyBase):
    dependency_id: str


class TaskDependencyResponse(TaskDependencyBase):
    dependency_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# SYNC STATUS SCHEMAS
# ============================================================================

class SyncStatus(BaseModel):
    """Status of GitHub and Jira sync operations"""
    last_github_sync: Optional[datetime] = None
    last_jira_sync: Optional[datetime] = None
    github_sync_status: str = "idle"
    jira_sync_status: str = "idle"
    github_synced_items: int = 0
    jira_synced_items: int = 0
    errors: List[str] = []


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================

class DashboardStats(BaseModel):
    """Overall dashboard statistics"""
    total_projects: int
    active_projects: int
    total_employees: int
    total_tasks: int
    completed_tasks: int
    open_prs: int
    critical_issues: int
    blocked_tasks: int


class ProjectHealthScore(BaseModel):
    """Project health indicators"""
    project_id: str
    project_name: str
    health_score: float  # 0-100
    on_time_percentage: float
    team_velocity: float
    critical_issues_count: int
    blocked_tasks_count: int


# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    employee_id: Optional[str] = None

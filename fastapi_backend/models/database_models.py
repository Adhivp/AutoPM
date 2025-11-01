"""
SQLAlchemy Models for AutoPM Database
Defines all database tables and relationships
"""
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Boolean, Text, JSON, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class ProjectMetadata(Base):
    """Project Metadata - Define scope, standards, and timeline"""
    __tablename__ = "project_metadata"
    
    project_id = Column(String(100), primary_key=True)
    project_name = Column(String(255), nullable=False)
    start_date = Column(Date)
    target_end_date = Column(Date)
    actual_end_date = Column(Date)
    compliance_standards = Column(JSON)  # ["ISO 26262", "ASPICE Level 2"]
    critical_modules = Column(JSON)  # ["BrakeControl", "OTAUpdate"]
    team_lead_id = Column(String(100), ForeignKey('employee_profile.employee_id'))
    status = Column(String(50), CheckConstraint("status IN ('Planning', 'In Progress', 'On Hold', 'Completed')"))
    github_repo_name = Column(String(255))
    jira_project_key = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    team_lead = relationship("EmployeeProfile", foreign_keys=[team_lead_id], back_populates="led_projects")
    jira_tasks = relationship("JiraTask", back_populates="project", cascade="all, delete-orphan")
    github_activities = relationship("GitHubActivity", back_populates="project", cascade="all, delete-orphan")
    github_issues = relationship("GitHubIssue", back_populates="project", cascade="all, delete-orphan")
    resource_allocations = relationship("ResourceAllocation", back_populates="project", cascade="all, delete-orphan")
    communication_logs = relationship("TeamCommunicationLog", back_populates="project", cascade="all, delete-orphan")


class EmployeeProfile(Base):
    """Employee Profile - Team member information"""
    __tablename__ = "employee_profile"
    
    employee_id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(100))
    team = Column(String(100))
    skills = Column(JSON)  # ["AUTOSAR", "C++", "CANoe"]
    manager_id = Column(String(100), ForeignKey('employee_profile.employee_id'))
    github_username = Column(String(100))
    jira_email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    manager = relationship("EmployeeProfile", remote_side=[employee_id], back_populates="team_members")
    team_members = relationship("EmployeeProfile", back_populates="manager")
    led_projects = relationship("ProjectMetadata", foreign_keys=[ProjectMetadata.team_lead_id], back_populates="team_lead")
    assigned_tasks = relationship("JiraTask", back_populates="assignee")
    authored_prs = relationship("GitHubActivity", back_populates="author")
    authored_issues = relationship("GitHubIssue", back_populates="author")
    resource_allocations = relationship("ResourceAllocation", back_populates="employee", cascade="all, delete-orphan")
    sent_messages = relationship("TeamCommunicationLog", back_populates="sender", cascade="all, delete-orphan")


class JiraTask(Base):
    """Jira Tasks & Issues - Track work items"""
    __tablename__ = "jira_tasks"
    
    issue_id = Column(String(100), primary_key=True)  # "ECU-123"
    project_id = Column(String(100), ForeignKey('project_metadata.project_id'), nullable=False)
    summary = Column(String(500))
    description = Column(Text)
    issue_type = Column(String(50), CheckConstraint("issue_type IN ('Story', 'Bug', 'Task', 'Epic')"))
    assignee_id = Column(String(100), ForeignKey('employee_profile.employee_id'))
    status = Column(String(50), CheckConstraint("status IN ('To Do', 'In Progress', 'In Review', 'Done')"))
    priority = Column(String(50), CheckConstraint("priority IN ('Low', 'Medium', 'High', 'Critical')"))
    story_points = Column(Integer)
    created_date = Column(DateTime)
    updated_date = Column(DateTime)
    resolved_date = Column(DateTime)
    parent_issue_id = Column(String(100), ForeignKey('jira_tasks.issue_id'))
    depends_on = Column(JSON)  # Array of issue_ids
    labels = Column(JSON)  # Array of labels
    github_pr_id = Column(String(100))
    last_synced_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("ProjectMetadata", back_populates="jira_tasks")
    assignee = relationship("EmployeeProfile", back_populates="assigned_tasks")
    parent_issue = relationship("JiraTask", remote_side=[issue_id], back_populates="subtasks")
    subtasks = relationship("JiraTask", back_populates="parent_issue")
    dependent_tasks = relationship("TaskDependency", foreign_keys="[TaskDependency.dependent_task_id]", back_populates="dependent_task")
    blocking_tasks = relationship("TaskDependency", foreign_keys="[TaskDependency.blocking_task_id]", back_populates="blocking_task")
    github_activities = relationship("GitHubActivity", back_populates="associated_issue")


class GitHubActivity(Base):
    """GitHub Activity - Monitor code progress and collaboration"""
    __tablename__ = "github_activity"
    
    pr_id = Column(String(100), primary_key=True)  # "repo/PR#456"
    project_id = Column(String(100), ForeignKey('project_metadata.project_id'), nullable=False)
    title = Column(String(500))
    author_id = Column(String(100), ForeignKey('employee_profile.employee_id'))
    reviewers = Column(JSON)  # Array of employee_ids
    created_at = Column(DateTime)
    merged_at = Column(DateTime)
    closed_at = Column(DateTime)
    status = Column(String(50), CheckConstraint("status IN ('Open', 'Merged', 'Closed')"))
    associated_issue_id = Column(String(100), ForeignKey('jira_tasks.issue_id'))
    changed_files = Column(Integer, default=0)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    build_status = Column(String(50), CheckConstraint("build_status IN ('Success', 'Failed', 'Pending')"))
    test_coverage_delta = Column(Float)
    last_synced_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("ProjectMetadata", back_populates="github_activities")
    author = relationship("EmployeeProfile", back_populates="authored_prs")
    associated_issue = relationship("JiraTask", back_populates="github_activities")
    associated_github_issue = relationship("GitHubIssue", back_populates="associated_pr")


class GitHubIssue(Base):
    """GitHub Issues - Track GitHub issues separately from PRs"""
    __tablename__ = "github_issues"
    
    issue_id = Column(String(100), primary_key=True)  # "repo/Issue#789"
    project_id = Column(String(100), ForeignKey('project_metadata.project_id'), nullable=False)
    title = Column(String(500))
    author_id = Column(String(100), ForeignKey('employee_profile.employee_id'))
    assignees = Column(JSON)  # Array of employee_ids
    created_at = Column(DateTime)
    closed_at = Column(DateTime)
    status = Column(String(50), CheckConstraint("status IN ('Open', 'Closed')"))
    labels = Column(JSON)  # Array of label names
    issue_type = Column(String(50), CheckConstraint("issue_type IN ('Bug', 'Feature', 'Enhancement', 'Question', 'Documentation')"))
    priority = Column(String(50), CheckConstraint("priority IN ('Low', 'Medium', 'High', 'Critical')"))
    associated_pr_id = Column(String(100), ForeignKey('github_activity.pr_id'))
    comments_count = Column(Integer, default=0)
    last_synced_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("ProjectMetadata", back_populates="github_issues")
    author = relationship("EmployeeProfile", back_populates="authored_issues")
    associated_pr = relationship("GitHubActivity", back_populates="associated_github_issue")


class ResourceAllocation(Base):
    """Resource Allocation & Time Tracking"""
    __tablename__ = "resource_allocation"
    
    allocation_id = Column(String(100), primary_key=True)
    employee_id = Column(String(100), ForeignKey('employee_profile.employee_id'), nullable=False)
    project_id = Column(String(100), ForeignKey('project_metadata.project_id'), nullable=False)
    week_start_date = Column(Date, nullable=False)
    overtime_hours = Column(Float, default=0.0)
    planned_hours = Column(Float, default=0.0)
    logged_hours = Column(Float, default=0.0)
    task_ids = Column(JSON)  # Array of Jira issue_ids
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("EmployeeProfile", back_populates="resource_allocations")
    project = relationship("ProjectMetadata", back_populates="resource_allocations")


class TeamCommunicationLog(Base):
    """Team Communication Logs - Capture blockers and urgency"""
    __tablename__ = "team_communication_logs"
    
    message_id = Column(String(100), primary_key=True)
    project_id = Column(String(100), ForeignKey('project_metadata.project_id'), nullable=False)
    sender_id = Column(String(100), ForeignKey('employee_profile.employee_id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    message_text = Column(Text)  # ≤200 chars
    is_blocker_signal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("ProjectMetadata", back_populates="communication_logs")
    sender = relationship("EmployeeProfile", back_populates="sent_messages")


class HistoricalProjectPerformance(Base):
    """Historical Project Performance - Train risk prediction models"""
    __tablename__ = "historical_project_performance"
    
    historical_project_id = Column(String(100), primary_key=True)
    project_name = Column(String(255), nullable=False)
    original_end_date = Column(Date)
    actual_end_date = Column(Date)
    delay_days = Column(Integer)  # actual - original
    defect_density = Column(Float)  # Bugs per KLOC
    integration_issues_count = Column(Integer, default=0)
    root_causes = Column(JSON)  # ["late_dependency", "resource_shortage"]
    compliance_audit_result = Column(String(50), CheckConstraint("compliance_audit_result IN ('Pass', 'Minor NC', 'Major NC')"))
    created_at = Column(DateTime, default=func.now())


class TaskDependency(Base):
    """Task Dependencies - Track blocking relationships"""
    __tablename__ = "task_dependencies"
    
    dependency_id = Column(String(100), primary_key=True)
    dependent_task_id = Column(String(100), ForeignKey('jira_tasks.issue_id'), nullable=False)
    blocking_task_id = Column(String(100), ForeignKey('jira_tasks.issue_id'), nullable=False)
    dependency_type = Column(String(50), CheckConstraint("dependency_type IN ('Internal', 'External')"))
    expected_ready_date = Column(Date)
    status = Column(String(50), CheckConstraint("status IN ('On Track', 'At Risk', 'Delayed')"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    dependent_task = relationship("JiraTask", foreign_keys=[dependent_task_id], back_populates="dependent_tasks")
    blocking_task = relationship("JiraTask", foreign_keys=[blocking_task_id], back_populates="blocking_tasks")


class SyncControl(Base):
    """Control table to persist desired sync state across restarts"""
    __tablename__ = "sync_control"

    id = Column(Integer, primary_key=True, default=1)
    desired_state = Column(String(50), CheckConstraint("desired_state IN ('running','stopped')"), nullable=False, default='running')
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class GitHubComment(Base):
    """GitHub Comments - Store comments from PRs and Issues"""
    __tablename__ = "github_comments"
    
    comment_id = Column(String(100), primary_key=True)  # GitHub comment ID
    pr_id = Column(String(100), ForeignKey('github_activity.pr_id'), nullable=True)
    issue_id = Column(String(100), ForeignKey('github_issues.issue_id'), nullable=True)
    author_id = Column(String(100), ForeignKey('employee_profile.employee_id'))
    body = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    reactions = Column(JSON)  # {"thumbs_up": 5, "thumbs_down": 0, "laugh": 2}
    last_synced_at = Column(DateTime, default=func.now())


class JiraComment(Base):
    """Jira Comments - Store comments from Jira issues"""
    __tablename__ = "jira_comments"
    
    comment_id = Column(String(100), primary_key=True)  # Jira comment ID
    issue_id = Column(String(100), ForeignKey('jira_tasks.issue_id'), nullable=False)
    author_id = Column(String(100), ForeignKey('employee_profile.employee_id'))
    body = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_synced_at = Column(DateTime, default=func.now())


class SyncLog(Base):
    """Sync Log - Track sync operations for auditing and debugging"""
    __tablename__ = "sync_logs"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    sync_type = Column(String(50))  # 'github_pr', 'github_issue', 'jira_issue'
    project_id = Column(String(100), ForeignKey('project_metadata.project_id'))
    status = Column(String(50))  # 'started', 'completed', 'failed'
    items_synced = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)


class VectorEmbedding(Base):
    """Vector Embeddings - Store embeddings for semantic search"""
    __tablename__ = "vector_embeddings"
    
    embedding_id = Column(String(100), primary_key=True)
    content_type = Column(String(50))  # 'pr', 'issue', 'jira_task', 'comment'
    content_id = Column(String(100))  # Reference to the actual content
    project_id = Column(String(100), ForeignKey('project_metadata.project_id'))
    title = Column(String(500))
    content_text = Column(Text)  # The text that was embedded
    content_metadata = Column(JSON)  # Additional metadata (author, date, labels, etc.)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ChatHistory(Base):
    """Chat History - Store chat conversations with AI"""
    __tablename__ = "chat_history"
    
    chat_id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey('employee_profile.employee_id'))
    message = Column(Text)
    response = Column(Text)
    context_items = Column(JSON)  # IDs of items retrieved from vector DB
    timestamp = Column(DateTime, default=func.now())

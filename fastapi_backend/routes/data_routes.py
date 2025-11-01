"""
Data Routes - CRUD operations for all entities
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.database_models import (
    ProjectMetadata, EmployeeProfile, JiraTask, GitHubActivity, GitHubIssue,
    ResourceAllocation, TeamCommunicationLog, HistoricalProjectPerformance,
    TaskDependency
)
from models.schemas import (
    ProjectResponse, ProjectCreate, ProjectWithStats,
    EmployeeResponse, EmployeeCreate, EmployeeWithStats,
    JiraTaskResponse, JiraTaskCreate, JiraTaskWithDetails,
    GitHubActivityResponse, GitHubActivityCreate, GitHubActivityWithDetails,
    GitHubIssueResponse, GitHubIssueCreate, GitHubIssueWithDetails,
    ResourceAllocationResponse, ResourceAllocationCreate,
    TeamCommunicationResponse, TeamCommunicationCreate,
    HistoricalPerformanceResponse, HistoricalPerformanceCreate,
    TaskDependencyResponse, TaskDependencyCreate,
    DashboardStats
)
from services.auth_service import get_current_user
from sqlalchemy import func, case

router = APIRouter(prefix="/api/data", tags=["Data Management"])


# ============================================================================
# PROJECT ENDPOINTS
# ============================================================================

@router.get("/projects", response_model=List[ProjectWithStats])
def get_all_projects(
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get all projects with statistics"""
    projects = db.query(ProjectMetadata).all()
    
    result = []
    for project in projects:
        # Calculate statistics
        tasks = db.query(JiraTask).filter(JiraTask.project_id == project.project_id).all()
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == 'Done')
        in_progress_tasks = sum(1 for t in tasks if t.status == 'In Progress')
        todo_tasks = sum(1 for t in tasks if t.status == 'To Do')
        critical_tasks = sum(1 for t in tasks if t.priority == 'Critical')
        
        # Get team lead name
        team_lead_name = None
        if project.team_lead:
            team_lead_name = project.team_lead.name
        
        project_dict = {
            **project.__dict__,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'todo_tasks': todo_tasks,
            'critical_tasks': critical_tasks,
            'team_lead_name': team_lead_name
        }
        result.append(project_dict)
    
    return result


@router.get("/projects/{project_id}", response_model=ProjectWithStats)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get a specific project by ID"""
    project = db.query(ProjectMetadata).filter(
        ProjectMetadata.project_id == project_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate statistics
    tasks = db.query(JiraTask).filter(JiraTask.project_id == project.project_id).all()
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == 'Done')
    in_progress_tasks = sum(1 for t in tasks if t.status == 'In Progress')
    todo_tasks = sum(1 for t in tasks if t.status == 'To Do')
    critical_tasks = sum(1 for t in tasks if t.priority == 'Critical')
    
    team_lead_name = None
    if project.team_lead:
        team_lead_name = project.team_lead.name
    
    return {
        **project.__dict__,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'todo_tasks': todo_tasks,
        'critical_tasks': critical_tasks,
        'team_lead_name': team_lead_name
    }


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Create a new project"""
    # Check if project already exists
    existing = db.query(ProjectMetadata).filter(
        ProjectMetadata.project_id == project.project_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Project ID already exists")
    
    new_project = ProjectMetadata(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project


# ============================================================================
# EMPLOYEE ENDPOINTS
# ============================================================================

@router.get("/employees", response_model=List[EmployeeWithStats])
def get_all_employees(
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get all employees with workload statistics"""
    employees = db.query(EmployeeProfile).filter(
        EmployeeProfile.is_active == True
    ).all()
    
    result = []
    for emp in employees:
        # Calculate statistics
        assigned_tasks = db.query(JiraTask).filter(
            JiraTask.assignee_id == emp.employee_id,
            JiraTask.status != 'Done'
        ).count()
        
        open_prs = db.query(GitHubActivity).filter(
            GitHubActivity.author_id == emp.employee_id,
            GitHubActivity.status == 'Open'
        ).count()
        
        total_hours = db.query(func.sum(ResourceAllocation.logged_hours)).filter(
            ResourceAllocation.employee_id == emp.employee_id
        ).scalar() or 0.0
        
        emp_dict = {
            **emp.__dict__,
            'assigned_tasks_count': assigned_tasks,
            'open_prs_count': open_prs,
            'total_hours_logged': float(total_hours)
        }
        result.append(emp_dict)
    
    return result


@router.get("/employees/{employee_id}", response_model=EmployeeWithStats)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get a specific employee by ID"""
    emp = db.query(EmployeeProfile).filter(
        EmployeeProfile.employee_id == employee_id
    ).first()
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Calculate statistics
    assigned_tasks = db.query(JiraTask).filter(
        JiraTask.assignee_id == emp.employee_id,
        JiraTask.status != 'Done'
    ).count()
    
    open_prs = db.query(GitHubActivity).filter(
        GitHubActivity.author_id == emp.employee_id,
        GitHubActivity.status == 'Open'
    ).count()
    
    total_hours = db.query(func.sum(ResourceAllocation.logged_hours)).filter(
        ResourceAllocation.employee_id == emp.employee_id
    ).scalar() or 0.0
    
    return {
        **emp.__dict__,
        'assigned_tasks_count': assigned_tasks,
        'open_prs_count': open_prs,
        'total_hours_logged': float(total_hours)
    }


# ============================================================================
# JIRA TASK ENDPOINTS
# ============================================================================

@router.get("/tasks")
def get_all_tasks(
    project_id: str = None,
    assignee_id: str = None,
    status: str = None,
    priority: str = None,
    issue_type: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get all Jira tasks with optional filters and pagination"""
    query = db.query(JiraTask)
    
    # Apply filters
    if project_id:
        query = query.filter(JiraTask.project_id == project_id)
    if assignee_id:
        query = query.filter(JiraTask.assignee_id == assignee_id)
    if status:
        query = query.filter(JiraTask.status == status)
    if priority:
        query = query.filter(JiraTask.priority == priority)
    if issue_type:
        query = query.filter(JiraTask.issue_type == issue_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    tasks = query.order_by(JiraTask.updated_date.desc()).offset(offset).limit(page_size).all()
    
    result = []
    for task in tasks:
        assignee_name = task.assignee.name if task.assignee else None
        reporter_name = None
        project_name = task.project.project_name if task.project else None
        
        task_dict = {
            **task.__dict__,
            'assignee_name': assignee_name,
            'reporter_name': reporter_name,
            'project_name': project_name
        }
        result.append(task_dict)
    
    return {
        'data': result,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }


@router.get("/tasks/{issue_id}", response_model=JiraTaskWithDetails)
def get_task(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get a specific Jira task by ID"""
    task = db.query(JiraTask).filter(JiraTask.issue_id == issue_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    assignee_name = task.assignee.name if task.assignee else None
    project_name = task.project.project_name if task.project else None
    
    return {
        **task.__dict__,
        'assignee_name': assignee_name,
        'project_name': project_name
    }


# ============================================================================
# GITHUB ACTIVITY ENDPOINTS
# ============================================================================

@router.get("/github/prs")
def get_all_pull_requests(
    project_id: str = None,
    author_id: str = None,
    status: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get all GitHub pull requests with optional filters and pagination"""
    query = db.query(GitHubActivity)
    
    # Apply filters
    if project_id:
        query = query.filter(GitHubActivity.project_id == project_id)
    if author_id:
        query = query.filter(GitHubActivity.author_id == author_id)
    if status:
        query = query.filter(GitHubActivity.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    prs = query.order_by(GitHubActivity.created_at.desc()).offset(offset).limit(page_size).all()
    
    result = []
    for pr in prs:
        author_name = pr.author.name if pr.author else None
        project_name = pr.project.project_name if pr.project else None
        
        pr_dict = {
            **pr.__dict__,
            'author_name': author_name,
            'project_name': project_name,
            'description': pr.title,  # Add description field
            'source_branch': 'main',  # Default values - update if you have these fields in DB
            'target_branch': 'develop',
            'pr_number': pr.pr_id.split('#')[-1] if '#' in pr.pr_id else pr.pr_id,
            'html_url': None  # Add if available in DB
        }
        result.append(pr_dict)
    
    return {
        'data': result,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }


@router.get("/github/prs/{pr_id}", response_model=GitHubActivityWithDetails)
def get_pull_request(
    pr_id: str,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get a specific pull request by ID"""
    pr = db.query(GitHubActivity).filter(GitHubActivity.pr_id == pr_id).first()
    
    if not pr:
        raise HTTPException(status_code=404, detail="Pull request not found")
    
    author_name = pr.author.name if pr.author else None
    project_name = pr.project.project_name if pr.project else None
    
    return {
        **pr.__dict__,
        'author_name': author_name,
        'project_name': project_name
    }


# ============================================================================
# GITHUB ISSUES ENDPOINTS
# ============================================================================

@router.get("/github/issues")
def get_all_github_issues(
    project_id: str = None,
    author_id: str = None,
    status: str = None,
    issue_type: str = None,
    priority: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get all GitHub issues with optional filters and pagination"""
    query = db.query(GitHubIssue)
    
    # Apply filters
    if project_id:
        query = query.filter(GitHubIssue.project_id == project_id)
    if author_id:
        query = query.filter(GitHubIssue.author_id == author_id)
    if status:
        query = query.filter(GitHubIssue.status == status)
    if issue_type:
        query = query.filter(GitHubIssue.issue_type == issue_type)
    if priority:
        query = query.filter(GitHubIssue.priority == priority)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    issues = query.order_by(GitHubIssue.created_at.desc()).offset(offset).limit(page_size).all()
    
    result = []
    for issue in issues:
        author_name = issue.author.name if issue.author else None
        project_name = issue.project.project_name if issue.project else None
        
        issue_dict = {
            **issue.__dict__,
            'author_name': author_name,
            'project_name': project_name
        }
        result.append(issue_dict)
    
    return {
        'data': result,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }


@router.get("/github/issues/{issue_id}", response_model=GitHubIssueWithDetails)
def get_github_issue(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get a specific GitHub issue by ID"""
    issue = db.query(GitHubIssue).filter(GitHubIssue.issue_id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="GitHub issue not found")
    
    author_name = issue.author.name if issue.author else None
    project_name = issue.project.project_name if issue.project else None
    
    return {
        **issue.__dict__,
        'author_name': author_name,
        'project_name': project_name
    }


# ============================================================================
# RESOURCE ALLOCATION ENDPOINTS
# ============================================================================

@router.get("/allocations", response_model=List[ResourceAllocationResponse])
def get_resource_allocations(
    employee_id: str = None,
    project_id: str = None,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get resource allocations with optional filters"""
    query = db.query(ResourceAllocation)
    
    if employee_id:
        query = query.filter(ResourceAllocation.employee_id == employee_id)
    if project_id:
        query = query.filter(ResourceAllocation.project_id == project_id)
    
    return query.all()


@router.post("/allocations", response_model=ResourceAllocationResponse, status_code=status.HTTP_201_CREATED)
def create_allocation(
    allocation: ResourceAllocationCreate,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Create a new resource allocation"""
    new_allocation = ResourceAllocation(**allocation.dict())
    db.add(new_allocation)
    db.commit()
    db.refresh(new_allocation)
    
    return new_allocation


# ============================================================================
# COMMUNICATION LOG ENDPOINTS
# ============================================================================

@router.get("/communications", response_model=List[TeamCommunicationResponse])
def get_communications(
    project_id: str = None,
    is_blocker: bool = None,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get team communication logs with optional filters"""
    query = db.query(TeamCommunicationLog)
    
    if project_id:
        query = query.filter(TeamCommunicationLog.project_id == project_id)
    if is_blocker is not None:
        query = query.filter(TeamCommunicationLog.is_blocker_signal == is_blocker)
    
    return query.order_by(TeamCommunicationLog.timestamp.desc()).all()


@router.post("/communications", response_model=TeamCommunicationResponse, status_code=status.HTTP_201_CREATED)
def create_communication(
    comm: TeamCommunicationCreate,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Create a new communication log"""
    new_comm = TeamCommunicationLog(**comm.dict())
    db.add(new_comm)
    db.commit()
    db.refresh(new_comm)
    
    return new_comm


# ============================================================================
# TASK DEPENDENCY ENDPOINTS
# ============================================================================

@router.get("/dependencies", response_model=List[TaskDependencyResponse])
def get_dependencies(
    task_id: str = None,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get task dependencies with optional filters"""
    query = db.query(TaskDependency)
    
    if task_id:
        query = query.filter(
            (TaskDependency.dependent_task_id == task_id) |
            (TaskDependency.blocking_task_id == task_id)
        )
    
    return query.all()


@router.post("/dependencies", response_model=TaskDependencyResponse, status_code=status.HTTP_201_CREATED)
def create_dependency(
    dependency: TaskDependencyCreate,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Create a new task dependency"""
    new_dependency = TaskDependency(**dependency.dict())
    db.add(new_dependency)
    db.commit()
    db.refresh(new_dependency)
    
    return new_dependency


# ============================================================================
# HISTORICAL PERFORMANCE ENDPOINTS
# ============================================================================

@router.get("/historical", response_model=List[HistoricalPerformanceResponse])
def get_historical_performance(
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get historical project performance data"""
    return db.query(HistoricalProjectPerformance).all()


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get overall dashboard statistics"""
    total_projects = db.query(ProjectMetadata).count()
    active_projects = db.query(ProjectMetadata).filter(
        ProjectMetadata.status.in_(['Planning', 'In Progress'])
    ).count()
    
    total_employees = db.query(EmployeeProfile).filter(
        EmployeeProfile.is_active == True
    ).count()
    
    total_tasks = db.query(JiraTask).count()
    completed_tasks = db.query(JiraTask).filter(JiraTask.status == 'Done').count()
    
    open_prs = db.query(GitHubActivity).filter(
        GitHubActivity.status == 'Open'
    ).count()
    
    critical_issues = db.query(JiraTask).filter(
        JiraTask.priority == 'Critical',
        JiraTask.status != 'Done'
    ).count()
    
    blocked_tasks = db.query(TeamCommunicationLog).filter(
        TeamCommunicationLog.is_blocker_signal == True
    ).count()
    
    return {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_employees': total_employees,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'open_prs': open_prs,
        'critical_issues': critical_issues,
        'blocked_tasks': blocked_tasks
    }

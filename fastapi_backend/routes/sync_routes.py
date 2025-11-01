"""
Sync Routes - Endpoints to trigger and monitor GitHub/Jira synchronization
Enhanced with parallel processing and comprehensive data syncing
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from services.enhanced_sync_service import sync_all_projects_parallel
from services.sync_service import sync_all_projects  # Keep for backward compatibility
from models.schemas import SyncStatus
from models.database_models import EmployeeProfile
from services.auth_service import get_current_user
from datetime import datetime
from typing import Dict, Any
from services import sync_manager

router = APIRouter(prefix="/api/sync", tags=["Synchronization"])

# Global sync status tracking with enhanced metrics
sync_status_data: Dict[str, Any] = {
    'last_github_sync': None,
    'last_jira_sync': None,
    'github_sync_status': 'idle',
    'jira_sync_status': 'idle',
    'github_prs_synced': 0,
    'github_issues_synced': 0,
    'github_comments_synced': 0,
    'jira_synced_items': 0,
    'jira_comments_synced': 0,
    'duration_seconds': 0,
    'errors': []
}


def perform_sync(db: Session, use_enhanced: bool = True):
    """Background task to perform sync with enhanced parallel processing"""
    global sync_status_data
    
    # Update status to running
    sync_status_data['github_sync_status'] = 'running'
    sync_status_data['jira_sync_status'] = 'running'
    sync_status_data['errors'] = []
    
    try:
        # Perform sync (use enhanced parallel version by default)
        if use_enhanced:
            results = sync_all_projects_parallel(db, max_workers=5)
        else:
            results = sync_all_projects(db)
        
        # Update status with results
        sync_status_data['last_github_sync'] = datetime.utcnow()
        sync_status_data['last_jira_sync'] = datetime.utcnow()
        sync_status_data['github_prs_synced'] = results.get('github_prs_synced', 0)
        sync_status_data['github_issues_synced'] = results.get('github_issues_synced', 0)
        sync_status_data['github_comments_synced'] = results.get('github_comments_synced', 0)
        sync_status_data['jira_synced_items'] = results.get('jira_issues_synced', 0)
        sync_status_data['jira_comments_synced'] = results.get('jira_comments_synced', 0)
        sync_status_data['duration_seconds'] = results.get('duration_seconds', 0)
        sync_status_data['errors'] = results.get('errors', [])
        
        # Update status
        if results.get('status') == 'success':
            sync_status_data['github_sync_status'] = 'success'
            sync_status_data['jira_sync_status'] = 'success'
        else:
            sync_status_data['github_sync_status'] = 'error'
            sync_status_data['jira_sync_status'] = 'error'

        print(f"✓ Enhanced sync completed in {results.get('duration_seconds', 0):.2f}s: "
              f"{results.get('github_prs_synced', 0)} PRs, "
              f"{results.get('github_issues_synced', 0)} issues, "
              f"{results.get('github_comments_synced', 0)} GitHub comments, "
              f"{results.get('jira_issues_synced', 0)} Jira tasks, "
              f"{results.get('jira_comments_synced', 0)} Jira comments")

    except Exception as e:
        sync_status_data['github_sync_status'] = 'error'
        sync_status_data['jira_sync_status'] = 'error'
        sync_status_data['errors'].append(f"Sync failed: {str(e)}")
        print(f"✗ Sync error: {str(e)}")


def perform_jira_sync(db: Session):
    """Background task to perform Jira-only sync"""
    global sync_status_data
    from config import settings
    from services.enhanced_sync_service import EnhancedJiraSyncService
    from models.database_models import ProjectMetadata
    
    # Update status to running
    sync_status_data['jira_sync_status'] = 'running'
    sync_status_data['errors'] = []
    
    start_time = datetime.utcnow()
    
    try:
        # Get Jira credentials
        jira_url = settings.JIRA_URL
        jira_email = settings.JIRA_EMAIL
        jira_token = settings.JIRA_API_TOKEN
        
        if not all([jira_url, jira_email, jira_token]):
            raise ValueError("Missing Jira credentials in settings")
        
        # Initialize Jira service
        jira_service = EnhancedJiraSyncService(jira_url, jira_email, jira_token)
        
        # Get all projects
        projects = db.query(ProjectMetadata).all()
        
        total_issues = 0
        total_comments = 0
        errors = []
        
        # Sync Jira for each project
        for project in projects:
            if project.jira_project_key:
                try:
                    print(f"Syncing Jira for project: {project.project_name} ({project.jira_project_key})")
                    result = jira_service.sync_issues_with_details(db, project)
                    total_issues += result.get('issues', 0)
                    total_comments += result.get('comments', 0)
                    print(f"✓ Synced {result.get('issues', 0)} issues and {result.get('comments', 0)} comments for {project.project_name}")
                except Exception as e:
                    error_msg = f"Error syncing Jira for project {project.project_id}: {str(e)}"
                    print(f"✗ {error_msg}")
                    errors.append(error_msg)
        
        # Update status with results
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        sync_status_data['last_jira_sync'] = end_time
        sync_status_data['jira_synced_items'] = total_issues
        sync_status_data['jira_comments_synced'] = total_comments
        sync_status_data['duration_seconds'] = duration
        sync_status_data['errors'] = errors
        
        # Update status
        if errors:
            sync_status_data['jira_sync_status'] = 'error'
        else:
            sync_status_data['jira_sync_status'] = 'success'

        print(f"✓ Jira sync completed in {duration:.2f}s: "
              f"{total_issues} issues, {total_comments} comments")

    except Exception as e:
        sync_status_data['jira_sync_status'] = 'error'
        sync_status_data['errors'].append(f"Jira sync failed: {str(e)}")
        print(f"✗ Jira sync error: {str(e)}")


def perform_github_sync(db: Session):
    """Background task to perform GitHub-only sync"""
    global sync_status_data
    from config import settings
    from services.enhanced_sync_service import EnhancedGitHubSyncService
    from models.database_models import ProjectMetadata
    
    # Update status to running
    sync_status_data['github_sync_status'] = 'running'
    sync_status_data['errors'] = []
    
    start_time = datetime.utcnow()
    
    try:
        # Get GitHub credentials
        github_token = settings.GITHUB_TOKEN
        
        if not github_token:
            raise ValueError("Missing GitHub credentials in settings")
        
        # Initialize GitHub service
        github_service = EnhancedGitHubSyncService(github_token)
        
        # Get all projects
        projects = db.query(ProjectMetadata).all()
        
        total_prs = 0
        total_issues = 0
        total_comments = 0
        errors = []
        
        # Sync GitHub for each project
        for project in projects:
            if project.github_repo_name:
                try:
                    print(f"Syncing GitHub for project: {project.project_name} ({project.github_repo_name})")
                    
                    # Sync PRs
                    pr_result = github_service.sync_pull_requests_with_details(db, project)
                    total_prs += pr_result.get('prs', 0)
                    total_comments += pr_result.get('comments', 0)
                    
                    # Sync Issues
                    issue_result = github_service.sync_issues_with_details(db, project)
                    total_issues += issue_result.get('issues', 0)
                    total_comments += issue_result.get('comments', 0)
                    
                    print(f"✓ Synced {pr_result.get('prs', 0)} PRs, {issue_result.get('issues', 0)} issues for {project.project_name}")
                except Exception as e:
                    error_msg = f"Error syncing GitHub for project {project.project_id}: {str(e)}"
                    print(f"✗ {error_msg}")
                    errors.append(error_msg)
        
        # Update status with results
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        sync_status_data['last_github_sync'] = end_time
        sync_status_data['github_prs_synced'] = total_prs
        sync_status_data['github_issues_synced'] = total_issues
        sync_status_data['github_comments_synced'] = total_comments
        sync_status_data['duration_seconds'] = duration
        sync_status_data['errors'] = errors
        
        # Update status
        if errors:
            sync_status_data['github_sync_status'] = 'error'
        else:
            sync_status_data['github_sync_status'] = 'success'

        print(f"✓ GitHub sync completed in {duration:.2f}s: "
              f"{total_prs} PRs, {total_issues} issues, {total_comments} comments")

    except Exception as e:
        sync_status_data['github_sync_status'] = 'error'
        sync_status_data['errors'].append(f"GitHub sync failed: {str(e)}")
        print(f"✗ GitHub sync error: {str(e)}")


@router.post("/trigger")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Manually trigger a sync operation"""
    global sync_status_data
    
    # Check if sync is already running
    if sync_status_data['github_sync_status'] == 'running' or sync_status_data['jira_sync_status'] == 'running':
        return {
            'message': 'Sync is already running',
            'status': sync_status_data
        }
    
    # Add sync task to background
    background_tasks.add_task(perform_sync, db)
    
    return {
        'message': 'Sync started in background',
        'status': sync_status_data
    }


@router.post("/trigger/jira-only")
async def trigger_jira_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Manually trigger Jira-only sync operation"""
    global sync_status_data
    
    # Check if Jira sync is already running
    if sync_status_data['jira_sync_status'] == 'running':
        return {
            'message': 'Jira sync is already running',
            'status': sync_status_data
        }
    
    # Add Jira sync task to background
    background_tasks.add_task(perform_jira_sync, db)
    
    return {
        'message': 'Jira sync started in background',
        'status': sync_status_data
    }


@router.post("/trigger/github-only")
async def trigger_github_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Manually trigger GitHub-only sync operation"""
    global sync_status_data
    
    # Check if GitHub sync is already running
    if sync_status_data['github_sync_status'] == 'running':
        return {
            'message': 'GitHub sync is already running',
            'status': sync_status_data
        }
    
    # Add GitHub sync task to background
    background_tasks.add_task(perform_github_sync, db)
    
    return {
        'message': 'GitHub sync started in background',
        'status': sync_status_data
    }


@router.post("/trigger/stop")
async def stop_sync(
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Stop any ongoing sync operation"""
    global sync_status_data
    
    # Update sync status to idle
    sync_status_data['github_sync_status'] = 'idle'
    sync_status_data['jira_sync_status'] = 'idle'
    
    return {
        'message': 'Sync stopped',
        'status': sync_status_data
    }


@router.post("/start")
def start_periodic(
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Start the background periodic sync task."""
    started = sync_manager.start_periodic_sync()
    if started:
        return {"message": "Periodic sync started"}
    return {"message": "Periodic sync already running"}


@router.post("/stop")
async def stop_periodic(
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Stop the background periodic sync task."""
    # stop and persist desired_state to 'stopped'
    stopped = await sync_manager.stop_periodic_sync(set_desired=True)
    if stopped:
        return {"message": "Periodic sync stopped"}
    return {"message": "Periodic sync was not running"}


@router.get("/status", response_model=SyncStatus)
def get_sync_status(
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get current sync status"""
    return sync_status_data


@router.get("/history")
def get_sync_history(
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get sync history (last sync timestamps for all projects)"""
    from models.database_models import ProjectMetadata, JiraTask, GitHubActivity
    from sqlalchemy import func
    
    projects = db.query(ProjectMetadata).all()
    
    history = []
    for project in projects:
        # Get last sync time for Jira tasks
        last_jira_sync = db.query(func.max(JiraTask.last_synced_at)).filter(
            JiraTask.project_id == project.project_id
        ).scalar()
        
        # Get last sync time for GitHub activities
        last_github_sync = db.query(func.max(GitHubActivity.last_synced_at)).filter(
            GitHubActivity.project_id == project.project_id
        ).scalar()
        
        history.append({
            'project_id': project.project_id,
            'project_name': project.project_name,
            'last_jira_sync': last_jira_sync,
            'last_github_sync': last_github_sync,
            'jira_project_key': project.jira_project_key,
            'github_repo_name': project.github_repo_name
        })
    
    return history


@router.get("/logs")
def get_sync_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get detailed sync operation logs for auditing and debugging"""
    from models.database_models import SyncLog
    
    logs = db.query(SyncLog).order_by(SyncLog.log_id.desc()).limit(limit).all()
    
    return [{
        'log_id': log.log_id,
        'sync_type': log.sync_type,
        'project_id': log.project_id,
        'status': log.status,
        'items_synced': log.items_synced,
        'error_message': log.error_message,
        'started_at': log.started_at,
        'completed_at': log.completed_at,
        'duration_seconds': log.duration_seconds
    } for log in logs]


@router.get("/stats")
def get_sync_stats(
    db: Session = Depends(get_db),
    current_user: EmployeeProfile = Depends(get_current_user)
):
    """Get comprehensive sync statistics"""
    from models.database_models import (
        GitHubActivity, GitHubIssue, GitHubComment, 
        JiraTask, JiraComment, SyncLog
    )
    from sqlalchemy import func
    
    stats = {
        'github': {
            'total_prs': db.query(func.count(GitHubActivity.pr_id)).scalar() or 0,
            'total_issues': db.query(func.count(GitHubIssue.issue_id)).scalar() or 0,
            'total_comments': db.query(func.count(GitHubComment.comment_id)).scalar() or 0,
            'last_sync': db.query(func.max(GitHubActivity.last_synced_at)).scalar()
        },
        'jira': {
            'total_tasks': db.query(func.count(JiraTask.issue_id)).scalar() or 0,
            'total_comments': db.query(func.count(JiraComment.comment_id)).scalar() or 0,
            'last_sync': db.query(func.max(JiraTask.last_synced_at)).scalar()
        },
        'sync_logs': {
            'total_syncs': db.query(func.count(SyncLog.log_id)).scalar() or 0,
            'failed_syncs': db.query(func.count(SyncLog.log_id)).filter(
                SyncLog.status == 'failed'
            ).scalar() or 0,
            'avg_duration': db.query(func.avg(SyncLog.duration_seconds)).filter(
                SyncLog.status == 'completed'
            ).scalar() or 0
        },
        'current_status': sync_status_data
    }
    
    return stats

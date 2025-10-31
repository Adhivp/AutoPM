"""
Sync Routes - Endpoints to trigger and monitor GitHub/Jira synchronization
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from services.sync_service import sync_all_projects
from models.schemas import SyncStatus
from models.database_models import EmployeeProfile
from services.auth_service import get_current_user
from datetime import datetime
from typing import Dict, Any
from services import sync_manager

router = APIRouter(prefix="/api/sync", tags=["Synchronization"])

# Global sync status tracking
sync_status_data: Dict[str, Any] = {
    'last_github_sync': None,
    'last_jira_sync': None,
    'github_sync_status': 'idle',
    'jira_sync_status': 'idle',
    'github_synced_items': 0,
    'jira_synced_items': 0,
    'errors': []
}


def perform_sync(db: Session):
    """Background task to perform sync"""
    global sync_status_data
    
    # Update status to running
    sync_status_data['github_sync_status'] = 'running'
    sync_status_data['jira_sync_status'] = 'running'
    sync_status_data['errors'] = []
    
    try:
        # Perform sync
        results = sync_all_projects(db)
        
        # Update status with results
        sync_status_data['last_github_sync'] = datetime.utcnow()
        sync_status_data['last_jira_sync'] = datetime.utcnow()
        sync_status_data['github_synced_items'] = results.get('github_prs_synced', 0)
        sync_status_data['jira_synced_items'] = results.get('jira_issues_synced', 0)
        sync_status_data['errors'] = results.get('errors', [])
        
        # Update status
        if results.get('status') == 'success':
            sync_status_data['github_sync_status'] = 'success'
            sync_status_data['jira_sync_status'] = 'success'
        else:
            sync_status_data['github_sync_status'] = 'error'
            sync_status_data['jira_sync_status'] = 'error'

        print(f"✓ Sync completed: {results.get('github_prs_synced', 0)} PRs, {results.get('jira_issues_synced', 0)} issues")

    except Exception as e:
        sync_status_data['github_sync_status'] = 'error'
        sync_status_data['jira_sync_status'] = 'error'
        sync_status_data['errors'].append(f"Sync failed: {str(e)}")
        print(f"✗ Sync error: {str(e)}")


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

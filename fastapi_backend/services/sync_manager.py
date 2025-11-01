"""Sync manager to control the periodic background sync task.

Provides start/stop/status APIs for the periodic sync so it can be controlled at runtime.
Enhanced with parallel processing support.
"""
import asyncio
from typing import Optional
from datetime import datetime
from services.enhanced_sync_service import sync_all_projects_parallel
from database import SessionLocal
from models.database_models import SyncControl


def _get_sync_control_row(db):
    """Return the single SyncControl row; create if missing."""
    sc = db.query(SyncControl).first()
    if not sc:
        sc = SyncControl(desired_state='running')
        db.add(sc)
        db.commit()
        db.refresh(sc)
    return sc


_sync_task: Optional[asyncio.Task] = None


async def _periodic_sync_loop():
    """Internal coroutine that runs periodic sync every 60s with enhanced parallel processing."""
    while True:
        try:
            db = SessionLocal()
            try:
                # Use enhanced parallel sync
                results = sync_all_projects_parallel(db, max_workers=5)
                if results.get('status') == 'success':
                    github_prs = results.get('github_prs_synced', 0)
                    github_issues = results.get('github_issues_synced', 0)
                    github_comments = results.get('github_comments_synced', 0)
                    jira_issues = results.get('jira_issues_synced', 0)
                    jira_comments = results.get('jira_comments_synced', 0)
                    duration = results.get('duration_seconds', 0)
                    print(f"⏰ Periodic sync completed in {duration:.2f}s: "
                          f"{github_prs} PRs, {github_issues} issues, "
                          f"{github_comments} GitHub comments, "
                          f"{jira_issues} Jira tasks, {jira_comments} Jira comments")
                else:
                    print(f"✗ Periodic sync error: {results.get('message')}")
            finally:
                db.close()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"✗ Periodic sync exception: {str(e)}")

        await asyncio.sleep(60)


def start_periodic_sync(loop: Optional[asyncio.AbstractEventLoop] = None) -> bool:
    """Start the periodic sync task if not already running.

    Returns True if started, False if already running.
    """
    global _sync_task
    if _sync_task and not _sync_task.done():
        return False

    # Use provided loop or current loop
    if loop is None:
        loop = asyncio.get_event_loop()

    _sync_task = loop.create_task(_periodic_sync_loop())
    print(f"🔄 Periodic sync started at {datetime.utcnow().isoformat()}")
    # Persist desired state to 'running'
    try:
        db = SessionLocal()
        try:
            sc = _get_sync_control_row(db)
            sc.desired_state = 'running'
            db.add(sc)
            db.commit()
        finally:
            db.close()
    except Exception:
        # Non-fatal if DB not available at this moment
        pass
    return True


async def stop_periodic_sync(set_desired: bool = True) -> bool:
    """Stop the periodic sync task if running.

    Returns True if it was running and is now cancelled, False if it was not running.
    """
    global _sync_task
    if not _sync_task or _sync_task.done():
        return False

    _sync_task.cancel()
    try:
        await _sync_task
    except asyncio.CancelledError:
        pass
    _sync_task = None
    print(f"⏹ Periodic sync stopped at {datetime.utcnow().isoformat()}")
    # Persist desired state to 'stopped' if requested
    if set_desired:
        try:
            db = SessionLocal()
            try:
                sc = _get_sync_control_row(db)
                sc.desired_state = 'stopped'
                db.add(sc)
                db.commit()
            finally:
                db.close()
        except Exception:
            pass
    return True


def is_running() -> bool:
    return bool(_sync_task and not _sync_task.done())


def get_desired_state() -> str:
    """Return desired state persisted in DB. If DB missing, default to 'running'."""
    try:
        db = SessionLocal()
        try:
            sc = db.query(SyncControl).first()
            if sc:
                return sc.desired_state
            return 'running'
        finally:
            db.close()
    except Exception:
        return 'running'

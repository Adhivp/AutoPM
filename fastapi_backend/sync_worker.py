"""
Standalone sync worker for AutoPM

Run this script separately (not inside the FastAPI server). It will:
- Initialize DB models (if not already)
- Periodically (default 60s) check SyncControl.desired_state and run sync_all_projects when desired_state == 'running'
- Respect SIGINT/SIGTERM for graceful shutdown
- Log results and errors to stdout

Usage:
    python sync_worker.py

You can run it in the background (macOS/Linux):
    nohup python sync_worker.py &

Or create a launchd/systemd/service to ensure it starts on boot.
"""
from __future__ import annotations
import time
import signal
import sys
import threading
import logging
import os
from datetime import datetime

from database import SessionLocal, init_db
from services.sync_service import sync_all_projects
from models.database_models import SyncControl
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("sync_worker")

# Read interval from env if provided, default to 60 seconds
SYNC_INTERVAL = int(os.getenv("AUTOPM_SYNC_INTERVAL", "60"))

# Control flag for graceful shutdown
_should_stop = threading.Event()


def _signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, stopping sync worker...")
    _should_stop.set()


def get_desired_state(db):
    try:
        sc = db.query(SyncControl).get(1)
        if not sc:
            # If not present, default to running
            sc = SyncControl(id=1, desired_state='running')
            db.add(sc)
            db.commit()
            db.refresh(sc)
        return sc.desired_state
    except Exception as e:
        logger.exception("Error reading SyncControl, defaulting to 'running'")
        return 'running'


def run_once(db):
    """Run a single sync cycle and return the result dict"""
    try:
        result = sync_all_projects(db)
        return result
    except Exception as e:
        logger.exception("Exception during sync_all_projects")
        return {'status': 'error', 'message': str(e), 'timestamp': datetime.utcnow().isoformat()}


def main_loop():
    logger.info("Starting AutoPM sync worker")
    init_db()  # ensure tables exist

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    while not _should_stop.is_set():
        db = SessionLocal()
        try:
            desired_state = get_desired_state(db)
            logger.debug(f"Desired sync state: {desired_state}")

            if desired_state == 'running':
                logger.info("Triggering sync cycle")
                result = run_once(db)
                status = result.get('status') if isinstance(result, dict) else 'unknown'
                github_count = result.get('github_prs_synced', 0) if isinstance(result, dict) else 0
                jira_count = result.get('jira_issues_synced', 0) if isinstance(result, dict) else 0
                logger.info(f"Sync result: status={status} projects_synced={result.get('projects_synced', 0)} github_prs={github_count} jira_issues={jira_count}")
                if result.get('errors'):
                    for err in result.get('errors'):
                        logger.error(f"Sync error: {err}")
            else:
                logger.info("Sync is currently stopped (desired_state != 'running'). Sleeping and will check again later.")

        except Exception:
            logger.exception("Unhandled exception in sync worker main loop")
        finally:
            try:
                db.close()
            except Exception:
                pass

        # Sleep, but wake earlier if stopping
        for _ in range(SYNC_INTERVAL):
            if _should_stop.is_set():
                break
            time.sleep(1)

    logger.info("Sync worker stopped gracefully")


if __name__ == '__main__':
    main_loop()

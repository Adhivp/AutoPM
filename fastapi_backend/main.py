"""
AutoPM - AI-Powered Automotive Project Management Assistant
FastAPI Backend with Authentication and OAuth2 Integrations
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from database import init_db, SessionLocal
from routes import auth_routes, integration_routes, data_routes, sync_routes, chat_routes
from routes import debug_routes
import asyncio
from services.sync_service import sync_all_projects
from services import sync_manager


# Background sync task
async def periodic_sync():
    """Run sync every 1 minute"""
    while True:
        try:
            print("⏰ Starting periodic sync...")
            db = SessionLocal()
            try:
                results = sync_all_projects(db)
                if results.get('status') == 'success':
                    github_synced = results.get('github_prs_synced', 0)
                    jira_synced = results.get('jira_issues_synced', 0)
                    print(f"✓ Periodic sync completed: {github_synced} PRs, {jira_synced} issues")
                else:
                    print(f"✗ Periodic sync error: {results.get('message')}")
            finally:
                db.close()
        except Exception as e:
            print(f"✗ Periodic sync error: {str(e)}")
        
        # Wait for 1 minute (60 seconds)
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup: Initialize database
    print("🚀 Starting AutoPM Backend...")
    init_db()
    print("✅ Database initialized!")
    
    # Start background sync task via sync_manager only if desired_state == 'running'
    try:
        desired = sync_manager.get_desired_state()
    except Exception:
        desired = 'running'

    print(f"🔄 Desired periodic sync state on startup: {desired}")
    if desired == 'running':
        try:
            sync_manager.start_periodic_sync()
        except Exception as e:
            print(f"⚠️ Could not start periodic sync: {str(e)}")
    print("✅ AutoPM Backend is ready!")
    
    yield
    
    # Shutdown
    print("⏹ Stopping background sync...")
    try:
        await sync_manager.stop_periodic_sync()
    except Exception as e:
        print(f"⚠️ Error stopping periodic sync: {str(e)}")
    print("👋 AutoPM Backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI backend with JWT authentication and OAuth2 integrations for GitHub and Jira",
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(integration_routes.router)
app.include_router(data_routes.router)
app.include_router(sync_routes.router)
app.include_router(chat_routes.router)
app.include_router(debug_routes.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

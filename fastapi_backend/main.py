"""
AutoPM - AI-Powered Automotive Project Management Assistant
FastAPI Backend with Authentication and OAuth2 Integrations
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from database import init_db
from routes import auth_routes, integration_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup: Initialize database
    print("🚀 Starting AutoPM Backend...")
    init_db()
    print("✅ AutoPM Backend is ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down AutoPM Backend...")


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

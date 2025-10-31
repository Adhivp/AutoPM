"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import settings
from models.base import Base

# Create database engine
# For SQLite, we need to add connect_args to enable check_same_thread=False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency function to get database session
    Yields a database session and ensures it's closed after use
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables
    Call this function when starting the application
    """
    # Import all models to ensure they're registered
    from models import User, IntegrationToken
    from models.database_models import (
        ProjectMetadata, EmployeeProfile, JiraTask, GitHubActivity,
        ResourceAllocation, TeamCommunicationLog, HistoricalProjectPerformance,
        TaskDependency
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def drop_all_tables():
    """
    Drop all tables (use with caution, only for development)
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped")

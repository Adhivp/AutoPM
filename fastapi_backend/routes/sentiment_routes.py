"""
Sentiment Analysis Routes
API endpoints for analyzing sentiment from comments
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.user import User
from services.auth_service import get_current_user
from services.sentiment_service import get_sentiment_service

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])


@router.get("/projects")
def get_project_sentiment(
    project_id: Optional[str] = Query(None, description="Filter by specific project ID"),
    days_back: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sentiment analysis for all projects or a specific project
    
    Query Parameters:
    - project_id: Optional project ID to filter by
    - days_back: Number of days to look back (default: 90, max: 365)
    
    Returns:
    - List of projects with sentiment scores and breakdowns
    """
    sentiment_service = get_sentiment_service()
    
    try:
        results = sentiment_service.analyze_project_sentiment(
            db=db,
            project_id=project_id,
            days_back=days_back
        )
        
        return {
            "success": True,
            "total_projects": len(results),
            "analysis_period_days": days_back,
            "projects": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze project sentiment: {str(e)}"
        )


@router.get("/employees")
def get_employee_sentiment(
    project_id: Optional[str] = Query(None, description="Filter by specific project ID"),
    employee_id: Optional[str] = Query(None, description="Filter by specific employee ID"),
    days_back: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sentiment analysis by employee
    
    Query Parameters:
    - project_id: Optional project ID to filter by
    - employee_id: Optional employee ID to filter by
    - days_back: Number of days to look back (default: 90, max: 365)
    
    Returns:
    - List of employees with their sentiment scores and project breakdowns
    """
    sentiment_service = get_sentiment_service()
    
    try:
        results = sentiment_service.analyze_employee_sentiment(
            db=db,
            project_id=project_id,
            employee_id=employee_id,
            days_back=days_back
        )
        
        return {
            "success": True,
            "total_employees": len(results),
            "analysis_period_days": days_back,
            "employees": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze employee sentiment: {str(e)}"
        )


@router.get("/trends/{project_id}")
def get_sentiment_trends(
    project_id: str,
    days_back: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sentiment trends over time for a specific project
    
    Path Parameters:
    - project_id: The project ID to analyze
    
    Query Parameters:
    - days_back: Number of days to look back (default: 90, max: 365)
    
    Returns:
    - Weekly sentiment trend data
    """
    sentiment_service = get_sentiment_service()
    
    try:
        results = sentiment_service.get_sentiment_trends(
            db=db,
            project_id=project_id,
            days_back=days_back
        )
        
        return {
            "success": True,
            **results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sentiment trends: {str(e)}"
        )


@router.get("/summary")
def get_sentiment_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall sentiment summary across all projects
    
    Returns:
    - Aggregated sentiment statistics
    """
    sentiment_service = get_sentiment_service()
    
    try:
        project_sentiments = sentiment_service.analyze_project_sentiment(
            db=db,
            days_back=90
        )
        
        if not project_sentiments:
            return {
                "success": True,
                "overall_sentiment": "neutral",
                "average_score": 0.0,
                "total_projects": 0,
                "total_comments": 0,
                "positive_projects": 0,
                "negative_projects": 0,
                "neutral_projects": 0
            }
        
        # Calculate overall statistics
        total_comments = sum(p['total_comments'] for p in project_sentiments)
        avg_score = sum(p['sentiment_score'] * p['total_comments'] for p in project_sentiments) / total_comments if total_comments > 0 else 0
        
        positive_projects = sum(1 for p in project_sentiments if p['sentiment_label'] == 'positive')
        negative_projects = sum(1 for p in project_sentiments if p['sentiment_label'] == 'negative')
        neutral_projects = sum(1 for p in project_sentiments if p['sentiment_label'] == 'neutral')
        
        # Overall label
        if avg_score > 0.15:
            overall_label = 'positive'
        elif avg_score < -0.15:
            overall_label = 'negative'
        else:
            overall_label = 'neutral'
        
        return {
            "success": True,
            "overall_sentiment": overall_label,
            "average_score": round(avg_score, 3),
            "total_projects": len(project_sentiments),
            "total_comments": total_comments,
            "positive_projects": positive_projects,
            "negative_projects": negative_projects,
            "neutral_projects": neutral_projects,
            "projects_with_data": len([p for p in project_sentiments if p['total_comments'] > 0])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sentiment summary: {str(e)}"
        )

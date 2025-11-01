"""
AI Insights Routes - Generate intelligent insights using semantic search and Gemini
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models.user import User
from services.auth_service import get_current_user
from services.ai_insights_service import get_insights_service

router = APIRouter(prefix="/api/insights", tags=["AI Insights"])


# Request/Response Models
class InsightRequest(BaseModel):
    insight_types: List[str]
    project_ids: Optional[List[str]] = None


class InsightResponse(BaseModel):
    success: bool
    insight_type: str
    insight: str
    context_count: int
    search_terms: List[str]
    timestamp: str


@router.get("/generate", response_model=List[InsightResponse])
def generate_insights(
    insight_types: Optional[str] = None,
    project_ids: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI insights using semantic search and Gemini
    
    Query Parameters:
    - insight_types: Comma-separated list of insight types (default: all 6 types)
    - project_ids: Comma-separated list of project IDs to filter by
    
    Available insight types:
    - project_health: Overall project status and health
    - team_performance: Team velocity and productivity
    - code_quality: Code review and build status
    - blockers: Identified blockers and impediments
    - upcoming_risks: Potential risks and issues
    - recent_achievements: Recent wins and completions
    """
    
    # Default to all 6 insight types
    default_types = [
        "project_health",
        "team_performance",
        "code_quality",
        "blockers",
        "upcoming_risks",
        "recent_achievements"
    ]
    
    # Parse insight types
    if insight_types:
        types_list = [t.strip() for t in insight_types.split(',')]
    else:
        types_list = default_types
    
    # Parse project IDs
    project_list = None
    if project_ids:
        project_list = [p.strip() for p in project_ids.split(',')]
    
    # Generate insights
    insights_service = get_insights_service()
    insights = insights_service.generate_multiple_insights(
        db=db,
        insight_types=types_list,
        project_ids=project_list,
        user_id=str(current_user.id)
    )
    
    return insights


@router.post("/generate-batch", response_model=List[InsightResponse])
def generate_insights_batch(
    request: InsightRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate multiple AI insights in a batch request
    
    Body:
    - insight_types: List of insight types to generate
    - project_ids: Optional list of project IDs to filter by
    """
    
    insights_service = get_insights_service()
    insights = insights_service.generate_multiple_insights(
        db=db,
        insight_types=request.insight_types,
        project_ids=request.project_ids,
        user_id=str(current_user.id)
    )
    
    return insights


@router.get("/types")
def get_available_insight_types(
    current_user: User = Depends(get_current_user)
):
    """Get list of available insight types with descriptions"""
    
    return {
        "insight_types": [
            {
                "type": "project_health",
                "name": "Project Health",
                "description": "Overall project status, task completion rates, and health indicators",
                "icon": "activity"
            },
            {
                "type": "team_performance",
                "name": "Team Performance",
                "description": "Team velocity, collaboration patterns, and workload distribution",
                "icon": "users"
            },
            {
                "type": "code_quality",
                "name": "Code Quality",
                "description": "PR review status, build health, and code review patterns",
                "icon": "code"
            },
            {
                "type": "blockers",
                "name": "Blockers & Impediments",
                "description": "Identified blockers, dependencies, and stuck work items",
                "icon": "alert-circle"
            },
            {
                "type": "upcoming_risks",
                "name": "Upcoming Risks",
                "description": "Potential risks, approaching deadlines, and critical priorities",
                "icon": "alert-triangle"
            },
            {
                "type": "recent_achievements",
                "name": "Recent Achievements",
                "description": "Completed tasks, merged PRs, and resolved issues",
                "icon": "trophy"
            }
        ]
    }

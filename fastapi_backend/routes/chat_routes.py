"""
AI Chat Routes - Gemini-powered chat with RAG
Endpoints for chat, embeddings, and semantic search
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from services.auth_service import get_current_user
from services.chat_service import get_chat_service
from services.vector_service import get_vector_service
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/ai", tags=["AI Chat"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    project_ids: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    success: bool
    chat_id: Optional[str] = None
    response: str
    context_items: List[Dict[str, Any]]
    context_count: int
    timestamp: str
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    content_types: Optional[List[str]] = None
    project_ids: Optional[List[str]] = None
    n_results: int = 10


class EmbedAllRequest(BaseModel):
    force_reindex: bool = False


class ProjectSummaryRequest(BaseModel):
    project_id: str


# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with AI assistant using RAG (Retrieval Augmented Generation)
    
    The AI has access to all synced GitHub PRs, Issues, Jira tasks, and comments.
    It will search for relevant context based on your question and provide informed answers.
    
    Example questions:
    - "What are the current open PRs that need review?"
    - "Show me high priority issues in project X"
    - "What are the blocked tasks?"
    - "Summarize the status of sprint tasks"
    """
    try:
        chat_service = get_chat_service()
        
        result = chat_service.chat(
            db=db,
            user_id=str(current_user.id),
            message=request.message,
            project_ids=request.project_ids,
            content_types=request.content_types,
            conversation_history=request.conversation_history
        )
        
        # Check if the service returned an error
        if not result.get("success", True):
            error_msg = result.get("error", "Unknown error occurred")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Add timestamp if not present
        if "timestamp" not in result:
            result["timestamp"] = datetime.utcnow().isoformat()
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/chat/history")
def get_chat_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's chat history"""
    try:
        chat_service = get_chat_service()
        history = chat_service.get_conversation_history(
            db=db,
            user_id=str(current_user.id),
            limit=limit
        )
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/suggestions")
def get_suggested_questions(
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get suggested questions to ask the AI"""
    try:
        chat_service = get_chat_service()
        suggestions = chat_service.get_suggested_questions(db, project_id)
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SEMANTIC SEARCH ENDPOINTS
# ============================================================================

@router.post("/search")
def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform semantic search across all synced data
    
    Search across PRs, issues, tasks, and comments using natural language.
    Results are ranked by semantic similarity.
    
    content_types options: ['pr', 'issue', 'jira_task', 'comment']
    """
    try:
        vector_service = get_vector_service()
        
        results = vector_service.semantic_search(
            query=request.query,
            content_types=request.content_types,
            project_ids=request.project_ids,
            n_results=request.n_results
        )
        
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


# ============================================================================
# EMBEDDING MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/embeddings/generate-all")
def generate_all_embeddings(
    request: EmbedAllRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate embeddings for all existing data in the database
    
    This should be run:
    1. After initial data sync
    2. When force_reindex is needed
    
    Note: This can take several minutes depending on data volume.
    """
    try:
        vector_service = get_vector_service()
        
        print("🔄 Starting embedding generation for all data...")
        stats = vector_service.embed_all_data(db)
        
        return {
            "success": True,
            "message": "All embeddings generated successfully",
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")


@router.get("/embeddings/stats")
def get_embedding_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics about embeddings in the system"""
    try:
        from models.database_models import VectorEmbedding
        from sqlalchemy import func
        
        total_embeddings = db.query(func.count(VectorEmbedding.embedding_id)).scalar()
        
        by_type = {}
        for content_type in ['pr', 'issue', 'jira_task', 'comment']:
            count = db.query(func.count(VectorEmbedding.embedding_id)).filter(
                VectorEmbedding.content_type == content_type
            ).scalar()
            by_type[content_type] = count or 0
        
        return {
            "success": True,
            "total_embeddings": total_embeddings or 0,
            "by_type": by_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROJECT ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/analyze/project-summary")
def analyze_project_summary(
    request: ProjectSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered project status summary
    
    Analyzes all PRs, issues, tasks, and comments for a project
    and provides comprehensive status overview with recommendations.
    """
    try:
        chat_service = get_chat_service()
        
        result = chat_service.summarize_project_status(
            db=db,
            project_id=request.project_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/analyze/sentiment")
def analyze_sentiment(
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze sentiment of text (comments, messages, etc.)
    
    Returns sentiment classification and whether it indicates
    a blocker or critical issue.
    """
    try:
        chat_service = get_chat_service()
        
        result = chat_service.analyze_sentiment(text)
        
        return {
            "success": True,
            "text": text,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis error: {str(e)}")


# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================

@router.get("/status")
def get_ai_system_status(
    current_user: User = Depends(get_current_user)
):
    """Get AI system status and health"""
    try:
        vector_service = get_vector_service()
        
        # Check if vector service is working
        test_embedding = vector_service.generate_embedding("test")
        embedding_service_ok = len(test_embedding) > 0
        
        return {
            "success": True,
            "services": {
                "embedding": "operational" if embedding_service_ok else "error",
                "vector_db": "operational",
                "chat": "operational"
            },
            "embedding_dimensions": len(test_embedding),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "services": {
                "embedding": "error",
                "vector_db": "error",
                "chat": "error"
            }
        }

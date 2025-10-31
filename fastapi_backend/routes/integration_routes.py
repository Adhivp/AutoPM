"""
Integration routes for OAuth2 connections (GitHub, Jira)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging
from database import get_db
from models.user import User
from models.integration_token import IntegrationToken
from services import integration_service
from routes.auth_routes import get_current_user

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/integrations", tags=["integrations"])


# Pydantic models for request/response validation
class OAuthCallbackRequest(BaseModel):
    """OAuth callback request with authorization code"""
    code: str


class IntegrationResponse(BaseModel):
    """Integration response model"""
    id: int
    provider: str
    provider_user_id: Optional[str]
    provider_email: Optional[str]
    connected_at: str
    
    class Config:
        from_attributes = True


class IntegrationStatusResponse(BaseModel):
    """Integration connection status"""
    provider: str
    connected: bool
    provider_user_id: Optional[str] = None
    provider_email: Optional[str] = None


@router.post("/connect/github", response_model=IntegrationResponse)
async def connect_github(
    callback_data: OAuthCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect GitHub account using OAuth2 authorization code
    
    Steps:
    1. Frontend redirects user to GitHub OAuth
    2. User authorizes the app
    3. GitHub redirects back with code
    4. Frontend sends code to this endpoint
    5. Backend exchanges code for access token and stores it encrypted
    
    Args:
        callback_data: OAuth callback with authorization code
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created/updated integration token information
    """
    logger.info(f"GitHub connect request from user: {current_user.email}")
    logger.info(f"Code received (first 20 chars): {callback_data.code[:20]}...")
    
    try:
        integration = await integration_service.connect_github(db, current_user, callback_data.code)
        logger.info(f"Successfully connected GitHub for user: {current_user.email}")
    except Exception as e:
        logger.error(f"Error connecting GitHub: {str(e)}", exc_info=True)
        raise
    
    return {
        "id": integration.id,
        "provider": integration.provider,
        "provider_user_id": integration.provider_user_id,
        "provider_email": integration.provider_email,
        "connected_at": integration.created_at.isoformat()
    }


@router.post("/connect/jira", response_model=IntegrationResponse)
async def connect_jira(
    callback_data: OAuthCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect Jira account using OAuth2 authorization code
    
    Steps:
    1. Frontend redirects user to Jira OAuth
    2. User authorizes the app
    3. Jira redirects back with code
    4. Frontend sends code to this endpoint
    5. Backend exchanges code for access token and stores it encrypted
    
    Args:
        callback_data: OAuth callback with authorization code
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created/updated integration token information
    """
    logger.info(f"Jira connect request from user: {current_user.email}")
    logger.info(f"Code received (first 20 chars): {callback_data.code[:20]}...")
    
    try:
        integration = await integration_service.connect_jira(db, current_user, callback_data.code)
        logger.info(f"Successfully connected Jira for user: {current_user.email}")
    except Exception as e:
        logger.error(f"Error connecting Jira: {str(e)}", exc_info=True)
        raise
    
    return {
        "id": integration.id,
        "provider": integration.provider,
        "provider_user_id": integration.provider_user_id,
        "provider_email": integration.provider_email,
        "connected_at": integration.created_at.isoformat()
    }


@router.delete("/disconnect/{provider}")
async def disconnect_integration(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect an integration (remove stored tokens)
    
    Args:
        provider: Provider name ('github' or 'jira')
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If provider is invalid or integration not found
    """
    if provider not in ["github", "jira"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider. Must be 'github' or 'jira'"
        )
    
    success = integration_service.disconnect_integration(db, current_user, provider)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {provider} integration found for this user"
        )
    
    return {
        "message": f"Successfully disconnected {provider} integration",
        "provider": provider
    }


@router.get("/status", response_model=List[IntegrationStatusResponse])
async def get_integration_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get connection status for all supported integrations
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of integration statuses (connected/disconnected)
    """
    integrations = integration_service.get_user_integrations(db, current_user)
    
    # Create a map of connected integrations
    connected_map = {integration.provider: integration for integration in integrations}
    
    # Return status for all supported providers
    statuses = []
    for provider in ["github", "jira"]:
        if provider in connected_map:
            integration = connected_map[provider]
            statuses.append({
                "provider": provider,
                "connected": True,
                "provider_user_id": integration.provider_user_id,
                "provider_email": integration.provider_email
            })
        else:
            statuses.append({
                "provider": provider,
                "connected": False
            })
    
    return statuses


@router.get("/list", response_model=List[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all connected integrations for the current user
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of connected integrations
    """
    integrations = integration_service.get_user_integrations(db, current_user)
    
    return [
        {
            "id": integration.id,
            "provider": integration.provider,
            "provider_user_id": integration.provider_user_id,
            "provider_email": integration.provider_email,
            "connected_at": integration.created_at.isoformat()
        }
        for integration in integrations
    ]


@router.get("/github/url")
async def get_github_oauth_url():
    """
    Get GitHub OAuth authorization URL for frontend redirect
    
    Returns:
        GitHub OAuth URL with client_id and redirect_uri
    """
    from config import settings
    
    oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=repo,user:email"
    )
    
    return {"url": oauth_url}


@router.get("/jira/url")
async def get_jira_oauth_url():
    """
    Get Jira OAuth authorization URL for frontend redirect
    
    Returns:
        Jira OAuth URL with client_id and redirect_uri
    """
    from config import settings
    
    oauth_url = (
        f"https://auth.atlassian.com/authorize"
        f"?audience=api.atlassian.com"
        f"&client_id={settings.JIRA_CLIENT_ID}"
        f"&scope=read:me read:jira-user read:jira-work write:jira-work offline_access"
        f"&redirect_uri={settings.JIRA_REDIRECT_URI}"
        f"&response_type=code"
        f"&prompt=consent"
    )
    
    return {"url": oauth_url}

"""
OAuth2 integration service for GitHub and Jira
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import httpx
import logging
from models.integration_token import IntegrationToken
from models.user import User
from utils.encryption import encrypt_token, decrypt_token
from config import settings

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def exchange_github_code(code: str) -> Dict[str, Any]:
    """
    Exchange GitHub OAuth code for access token
    
    Args:
        code: OAuth authorization code from GitHub
    
    Returns:
        Dictionary containing access_token and other GitHub OAuth response data
    
    Raises:
        HTTPException: If token exchange fails
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange GitHub code for token"
            )
        
        return response.json()


async def get_github_user_info(access_token: str) -> Dict[str, Any]:
    """
    Get GitHub user information using access token
    
    Args:
        access_token: GitHub access token
    
    Returns:
        Dictionary containing GitHub user information
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch GitHub user information"
            )
        
        return response.json()


async def exchange_jira_code(code: str) -> Dict[str, Any]:
    """
    Exchange Jira OAuth code for access token
    
    Args:
        code: OAuth authorization code from Jira
    
    Returns:
        Dictionary containing access_token, refresh_token, and expiry info
    
    Raises:
        HTTPException: If token exchange fails
    """
    logger.info(f"Exchanging Jira code for token. Code length: {len(code)}")
    logger.info(f"Jira Client ID: {settings.JIRA_CLIENT_ID[:10]}...")
    logger.info(f"Jira Redirect URI: {settings.JIRA_REDIRECT_URI}")
    
    async with httpx.AsyncClient() as client:
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.JIRA_CLIENT_ID,
            "client_secret": settings.JIRA_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.JIRA_REDIRECT_URI
        }
        logger.info(f"Request payload (without secret): {dict((k, v) for k, v in payload.items() if k != 'client_secret')}")
        
        response = await client.post(
            "https://auth.atlassian.com/oauth/token",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        logger.info(f"Jira token exchange response status: {response.status_code}")
        logger.info(f"Jira token exchange response body: {response.text}")
        
        if response.status_code != 200:
            logger.error(f"Failed to exchange Jira code. Status: {response.status_code}, Body: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange Jira code for token: {response.text}"
            )
        
        return response.json()


async def get_jira_user_info(access_token: str) -> Dict[str, Any]:
    """
    Get Jira user information using access token
    
    Args:
        access_token: Jira access token
    
    Returns:
        Dictionary containing Jira user information
    """
    logger.info("Fetching Jira user info")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.atlassian.com/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        logger.info(f"Jira user info response status: {response.status_code}")
        logger.info(f"Jira user info response body: {response.text}")
        
        if response.status_code != 200:
            logger.error(f"Failed to get Jira user info. Status: {response.status_code}, Body: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch Jira user information"
            )
        
        return response.json()


async def connect_github(db: Session, user: User, code: str) -> IntegrationToken:
    """
    Connect GitHub account for a user
    
    Args:
        db: Database session
        user: User object
        code: GitHub OAuth code
    
    Returns:
        Created or updated IntegrationToken object
    """
    # Exchange code for token
    token_data = await exchange_github_code(code)
    access_token = token_data.get("access_token")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token received from GitHub"
        )
    
    # Get GitHub user info
    github_user = await get_github_user_info(access_token)
    
    # Encrypt the token before storing
    encrypted_token = encrypt_token(access_token)
    
    # Check if integration already exists
    existing_integration = db.query(IntegrationToken).filter(
        IntegrationToken.user_id == user.id,
        IntegrationToken.provider == "github"
    ).first()
    
    if existing_integration:
        # Update existing integration
        existing_integration.encrypted_access_token = encrypted_token
        existing_integration.provider_user_id = str(github_user.get("id"))
        existing_integration.provider_email = github_user.get("email")
        existing_integration.scopes = token_data.get("scope", "")
        existing_integration.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_integration)
        return existing_integration
    else:
        # Create new integration
        new_integration = IntegrationToken(
            user_id=user.id,
            provider="github",
            encrypted_access_token=encrypted_token,
            provider_user_id=str(github_user.get("id")),
            provider_email=github_user.get("email"),
            scopes=token_data.get("scope", "")
        )
        db.add(new_integration)
        db.commit()
        db.refresh(new_integration)
        return new_integration


async def connect_jira(db: Session, user: User, code: str) -> IntegrationToken:
    """
    Connect Jira account for a user
    
    Args:
        db: Database session
        user: User object
        code: Jira OAuth code
    
    Returns:
        Created or updated IntegrationToken object
    """
    logger.info(f"Starting Jira connection for user: {user.email}")
    logger.info(f"Received Jira code (first 20 chars): {code[:20]}...")
    
    # Exchange code for token
    token_data = await exchange_jira_code(code)
    logger.info(f"Token data keys: {token_data.keys()}")
    
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")
    
    if not access_token:
        logger.error(f"No access token in response. Full response: {token_data}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token received from Jira"
        )
    
    logger.info(f"Access token received (length: {len(access_token)})")
    
    # Get Jira user info
    jira_user = await get_jira_user_info(access_token)
    logger.info(f"Jira user info: {jira_user}")
    
    # Encrypt tokens before storing
    encrypted_access_token = encrypt_token(access_token)
    encrypted_refresh_token = encrypt_token(refresh_token) if refresh_token else None
    
    # Calculate expiration time
    token_expires_at = None
    if expires_in:
        token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    # Check if integration already exists
    existing_integration = db.query(IntegrationToken).filter(
        IntegrationToken.user_id == user.id,
        IntegrationToken.provider == "jira"
    ).first()
    
    if existing_integration:
        # Update existing integration
        existing_integration.encrypted_access_token = encrypted_access_token
        existing_integration.encrypted_refresh_token = encrypted_refresh_token
        existing_integration.token_expires_at = token_expires_at
        existing_integration.provider_user_id = jira_user.get("account_id")
        existing_integration.provider_email = jira_user.get("email")
        existing_integration.scopes = token_data.get("scope", "")
        existing_integration.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_integration)
        return existing_integration
    else:
        # Create new integration
        new_integration = IntegrationToken(
            user_id=user.id,
            provider="jira",
            encrypted_access_token=encrypted_access_token,
            encrypted_refresh_token=encrypted_refresh_token,
            token_expires_at=token_expires_at,
            provider_user_id=jira_user.get("account_id"),
            provider_email=jira_user.get("email"),
            scopes=token_data.get("scope", "")
        )
        db.add(new_integration)
        db.commit()
        db.refresh(new_integration)
        return new_integration


def disconnect_integration(db: Session, user: User, provider: str) -> bool:
    """
    Disconnect an integration for a user
    
    Args:
        db: Database session
        user: User object
        provider: Provider name ('github' or 'jira')
    
    Returns:
        True if disconnected, False if integration not found
    """
    integration = db.query(IntegrationToken).filter(
        IntegrationToken.user_id == user.id,
        IntegrationToken.provider == provider
    ).first()
    
    if integration:
        db.delete(integration)
        db.commit()
        return True
    
    return False


def get_user_integrations(db: Session, user: User) -> list[IntegrationToken]:
    """
    Get all integrations for a user
    
    Args:
        db: Database session
        user: User object
    
    Returns:
        List of IntegrationToken objects
    """
    return db.query(IntegrationToken).filter(IntegrationToken.user_id == user.id).all()


def get_decrypted_token(db: Session, user: User, provider: str) -> Optional[str]:
    """
    Get decrypted access token for a provider
    
    Args:
        db: Database session
        user: User object
        provider: Provider name ('github' or 'jira')
    
    Returns:
        Decrypted access token if found, None otherwise
    """
    integration = db.query(IntegrationToken).filter(
        IntegrationToken.user_id == user.id,
        IntegrationToken.provider == provider
    ).first()
    
    if integration:
        return decrypt_token(integration.encrypted_access_token)
    
    return None

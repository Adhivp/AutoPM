"""
IntegrationToken model for storing encrypted OAuth2 tokens
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class IntegrationToken(Base):
    """
    Model for storing encrypted OAuth2 tokens for external integrations
    Supports GitHub, Jira, and other future integrations
    """
    __tablename__ = "integration_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # 'github', 'jira', etc.
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=True)  # Some providers may not have refresh tokens
    token_expires_at = Column(DateTime, nullable=True)  # Token expiration time
    provider_user_id = Column(String, nullable=True)  # User ID from the provider (e.g., GitHub username)
    provider_email = Column(String, nullable=True)  # Email from the provider
    scopes = Column(Text, nullable=True)  # OAuth scopes granted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    user = relationship("User", back_populates="integration_tokens")

    def __repr__(self):
        return f"<IntegrationToken user_id={self.user_id} provider={self.provider}>"

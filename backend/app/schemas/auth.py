"""
Authentication schemas — request and response models for auth endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Request body for user signup."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response containing JWT access token."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User information response."""
    id: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

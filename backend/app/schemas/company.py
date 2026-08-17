"""
Company schemas — request and response models for company endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    """Request body for creating a company."""
    name: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., min_length=1, max_length=255)
    icp: str = Field(..., description="Ideal Customer Profile")
    brand_voice: str = Field(..., description="Brand voice and tone guidelines")


class CompanyResponse(BaseModel):
    """Company information response."""
    id: str
    owner_id: str
    name: str
    industry: str
    icp: str
    brand_voice: str
    created_at: datetime
    
    class Config:
        from_attributes = True

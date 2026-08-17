"""
Companies routers — create and retrieve company profiles.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.company import Company
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.company import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    request: CompanyCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CompanyResponse:
    """
    Create a new company for the current user (onboarding).
    
    Args:
        request: Company details (name, industry, ICP, brand voice)
        current_user: Authenticated user from JWT
        db: Database session
        
    Returns:
        Created company information
        
    Raises:
        HTTPException: 400 if user already has a company
    """
    # Check if user already has a company
    existing_company = db.query(Company).filter(Company.owner_id == current_user.id).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a company. Use PUT to update.",
        )
    
    # Create new company
    company = Company(
        owner_id=current_user.id,
        name=request.name,
        industry=request.industry,
        icp=request.icp,
        brand_voice=request.brand_voice,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return CompanyResponse(
        id=company.id,
        owner_id=company.owner_id,
        name=company.name,
        industry=company.industry,
        icp=company.icp,
        brand_voice=company.brand_voice,
        created_at=company.created_at,
    )


@router.get("/me", response_model=CompanyResponse | None)
def get_my_company(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CompanyResponse | None:
    """
    Get the current users company.
    
    Args:
        current_user: Authenticated user from JWT
        db: Database session
        
    Returns:
        Company information, or None if user has no company yet
    """
    company = db.query(Company).filter(Company.owner_id == current_user.id).first()
    
    if not company:
        return None
    
    return CompanyResponse(
        id=company.id,
        owner_id=company.owner_id,
        name=company.name,
        industry=company.industry,
        icp=company.icp,
        brand_voice=company.brand_voice,
        created_at=company.created_at,
    )

"""
Authorization helpers — ownership checks and permission guards.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.company import Company


def assert_owns_company(user_id: str, company_id: str, db: Session) -> None:
    """
    Verify that *user_id* owns *company_id*. Raise HTTP 403 if not.
    
    This is the single source of truth for company ownership checks.
    Every router that touches company-scoped data MUST call this function.
    
    Args:
        user_id: The authenticated users ID
        company_id: The company ID being accessed
        db: SQLAlchemy session
        
    Raises:
        HTTPException: 403 Forbidden if user does not own the company
        HTTPException: 404 Not Found if company does not exist
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company {company_id} not found",
        )
    
    if company.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this company",
        )

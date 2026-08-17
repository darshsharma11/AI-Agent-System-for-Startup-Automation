"""
Agents routers — coordinator and individual agent endpoints.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.authz import assert_owns_company
from app.agents import run_coordinator, AGENTS


router = APIRouter(prefix="/agents", tags=["agents"])


# ── Request/Response Schemas ─────────────────────────────────────────────
class CoordinatorRequest(BaseModel):
    """Request to coordinate a task."""
    company_id: str
    message: str


class AgentRequest(BaseModel):
    """Request to run a specific agent."""
    company_id: str
    message: str
    ticket_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Response from an agent."""
    summary: str
    data: dict | None
    log_entry: str


# ── Endpoints ────────────────────────────────────────────────────────────
@router.post("/coordinator", response_model=AgentResponse)
def coordinate(
    request: CoordinatorRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AgentResponse:
    """
    Route a message through the coordinator to determine the appropriate agent.
    
    Args:
        request: Coordinator request with company_id and message
        current_user: Authenticated user
        db: Database session
        
    Returns:
        AgentResponse with coordination result
    """
    # Verify user owns this company
    assert_owns_company(current_user.id, request.company_id, db)
    
    # Run coordinator
    result = run_coordinator(request.company_id, request.message, db)
    
    # Log the activity
    activity = ActivityLog(
        company_id=request.company_id,
        agent="coordinator",
        instruction=request.message,
        summary=result.summary,
    )
    db.add(activity)
    db.commit()
    
    return AgentResponse(
        summary=result.summary,
        data=result.data,
        log_entry=result.log_entry,
    )


@router.post("/support", response_model=AgentResponse)
def run_support_agent(
    request: AgentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AgentResponse:
    """
    Run the customer support agent directly.
    
    Args:
        request: Agent request with company_id, message, and optional ticket_id
        current_user: Authenticated user
        db: Database session
        
    Returns:
        AgentResponse with support agent result
    """
    # Verify user owns this company
    assert_owns_company(current_user.id, request.company_id, db)
    
    # Get the customer support agent function
    support_agent = AGENTS.get("customer_support")
    if not support_agent:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Customer support agent not available"
        )
    
    # Run the agent
    result = support_agent(
        company_id=request.company_id,
        instruction=request.message,
        db=db,
        ticket_id=request.ticket_id,
    )
    
    # Log the activity
    activity = ActivityLog(
        company_id=request.company_id,
        agent="customer_support",
        instruction=request.message,
        summary=result.summary,
    )
    db.add(activity)
    db.commit()
    
    return AgentResponse(
        summary=result.summary,
        data=result.data,
        log_entry=result.log_entry,
    )

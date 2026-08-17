"""
Base infrastructure for all agents.

Defines shared types and the agent registry.
"""

from typing import Any, Callable
from pydantic import BaseModel


class AgentResult(BaseModel):
    """Standard result returned by all agents."""
    summary: str  # One-sentence summary of what the agent did
    data: dict[str, Any] | None = None  # Optional structured data
    log_entry: str  # Detailed log message for ActivityLog table


# Global registry of available agents
# Key: agent name (e.g., "customer_support")
# Value: Callable that takes (company_id: str, instruction: str, db: Session) -> AgentResult
AGENTS: dict[str, Callable] = {}


def register_agent(name: str):
    """
    Decorator to register an agent function in the global registry.
    
    Usage:
        @register_agent("customer_support")
        def handle_customer_support(company_id: str, instruction: str, db: Session) -> AgentResult:
            ...
    """
    def decorator(func: Callable) -> Callable:
        AGENTS[name] = func
        return func
    return decorator

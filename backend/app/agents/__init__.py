"""
AI Agents package.

Import all agents here so they self-register in the AGENTS registry.
"""

from app.agents.base import AGENTS, AgentResult, register_agent
from app.agents.llm import llm
from app.agents.coordinator import run_coordinator

# Import agents so they self-register
from app.agents import customer_support, sales_outreach

__all__ = [
    "AGENTS",
    "AgentResult",
    "register_agent",
    "llm",
    "run_coordinator",
    "customer_support",
    "sales_outreach",
]

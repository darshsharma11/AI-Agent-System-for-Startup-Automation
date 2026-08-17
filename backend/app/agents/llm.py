"""
Shared LLM instance for all agents.

Uses Claude Sonnet 4 via langchain-anthropic.
"""

from langchain_anthropic import ChatAnthropic

from app.core.config import settings

# Shared ChatAnthropic instance for all agents
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    anthropic_api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.7,
    max_tokens=4096,
)

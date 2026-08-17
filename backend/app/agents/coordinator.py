"""
Coordinator agent — routes user messages to the appropriate specialized agent.

Uses CrewAI to classify the intent and determine which agent(s) should handle the task.
"""

import json
import re
from typing import Any

from crewai import Agent, Crew, Task
from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.agents.llm import llm
from app.models.activity_log import ActivityLog


def coordinate_task(company_id: str, message: str, db: Session) -> dict[str, Any]:
    """
    Classify user message and route to appropriate agent(s).
    
    Args:
        company_id: The company making the request
        message: User message to classify
        db: Database session
        
    Returns:
        Dictionary with agent, reasoning, and subtasks
    """
    # Define the coordinator agent
    coordinator = Agent(
        role="Task Coordinator",
        goal="Classify user requests and route them to the appropriate specialized agent",
        backstory="""You are an intelligent coordinator that analyzes user requests and 
        determines which AI agent should handle them. You understand the capabilities of:
        
        - customer_support: Handle customer inquiries, support tickets, bug reports, technical issues
          Examples: "Help with login", "Bug report", "Account problem", "Technical issue"
        
        - sales_outreach: Manage leads, create outreach sequences, prospecting, cold emails
          Examples: "Generate leads", "Create outreach for [company]", "Send cold emails", "Prospect new customers"
        
        - content_creation: Generate blog posts, social media, landing pages (NOT YET IMPLEMENTED)
        - marketing_ads: Create ad campaigns, budget allocation (NOT YET IMPLEMENTED)
        - analytics: Data analysis, reporting, insights (NOT YET IMPLEMENTED)
        - multi: Complex tasks requiring multiple agents (NOT YET IMPLEMENTED)
        
        Focus on routing to customer_support or sales_outreach based on the intent.""",
        llm=llm,
        verbose=True,
    )
    
    # Define the classification task
    task = Task(
        description=f"""Analyze this user message and determine which agent should handle it:
        
        Message: {message}
        
        Routing Guidelines:
        - Use "customer_support" for: support tickets, bugs, technical help, customer questions
        - Use "sales_outreach" for: lead generation, cold outreach, prospecting, sales sequences
        - Use "content_creation" for: blog posts, social media, content generation (not yet available)
        - Use "marketing_ads" for: ad campaigns, marketing strategy (not yet available)
        
        Return ONLY valid JSON in this exact format (no markdown, no code fences):
        {{
            "agent": "customer_support|sales_outreach|content_creation|marketing_ads|analytics|multi",
            "reasoning": "brief explanation of why this agent was chosen",
            "subtasks": [
                {{
                    "agent": "customer_support|sales_outreach",
                    "instruction": "the specific instruction for this agent"
                }}
            ]
        }}
        
        IMPORTANT: Return ONLY the JSON object, no other text or formatting.""",
        agent=coordinator,
        expected_output="JSON object with agent, reasoning, and subtasks fields",
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[coordinator],
        tasks=[task],
        verbose=True,
    )
    
    result = crew.kickoff()
    
    # Parse the result
    result_text = str(result)
    
    # Try to extract JSON from the result
    try:
        # Remove markdown code fences if present
        cleaned = re.sub(r'```json\s*|\s*```', '', result_text)
        cleaned = cleaned.strip()
        
        # Parse JSON
        parsed = json.loads(cleaned)
        
        # Validate required fields
        if "agent" not in parsed or "reasoning" not in parsed:
            raise ValueError("Missing required fields")
        
        # Ensure subtasks exists
        if "subtasks" not in parsed:
            parsed["subtasks"] = [{
                "agent": parsed["agent"],
                "instruction": message
            }]
        
        return parsed
        
    except (json.JSONDecodeError, ValueError) as e:
        # Fallback to customer_support if parsing fails
        print(f"Failed to parse coordinator result: {e}")
        print(f"Raw result: {result_text}")
        
        return {
            "agent": "customer_support",
            "reasoning": f"Fallback due to parsing error: {str(e)[:100]}",
            "subtasks": [{
                "agent": "customer_support",
                "instruction": message
            }]
        }


def run_coordinator(company_id: str, message: str, db: Session) -> AgentResult:
    """
    Run the coordinator and log the result.
    
    Args:
        company_id: The company making the request
        message: User message to route
        db: Database session
        
    Returns:
        AgentResult with coordination decision and execution results
    """
    # Get routing decision
    decision = coordinate_task(company_id, message, db)
    target_agent_name = decision.get("agent", "customer_support")
    
    # Log the coordination activity
    activity = ActivityLog(
        company_id=company_id,
        agent="coordinator",
        instruction=message,
        summary=f"Routed to {target_agent_name}: {decision.get('reasoning', '')}",
    )
    db.add(activity)
    db.commit()
    
    # Dispatch to the appropriate agent
    from app.agents import AGENTS
    
    agent_results = []
    
    if target_agent_name in ["customer_support", "sales_outreach"]:
        target_agent = AGENTS.get(target_agent_name)
        if target_agent:
            # We assume subtasks has at least one instruction
            subtasks = decision.get("subtasks", [])
            for task in subtasks:
                if task.get("agent") == target_agent_name:
                    # Run the agent
                    res = target_agent(
                        company_id=company_id,
                        instruction=task.get("instruction", message),
                        db=db
                    )
                    agent_results.append(res)
    
    if agent_results:
        # Combine results
        return AgentResult(
            summary=f"Routed to {target_agent_name}. {agent_results[0].summary}",
            data={
                "coordination": decision,
                "execution": [r.data for r in agent_results]
            },
            log_entry=f"Coordinator routed to {target_agent_name}. Execution log: {agent_results[0].log_entry}"
        )

    return AgentResult(
        summary=f"Routed to {target_agent_name} (Not implemented or failed to run)",
        data=decision,
        log_entry=f"Coordinator analyzed message and routed to {target_agent_name}. "
                  f"Reasoning: {decision.get('reasoning', '')}"
    )

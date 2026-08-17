"""
Customer Support Agent — handles customer inquiries and support tickets.

Uses LangChain to analyze messages, search similar tickets, and generate responses.
"""

import json
import re
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from app.agents.base import AgentResult, register_agent
from app.agents.llm import llm
from app.models.company import Company
from app.models.support_ticket import SupportTicket


def search_similar_tickets(company_id: str, message: str, db: Session, limit: int = 3) -> list[SupportTicket]:
    """
    Simple keyword-based search for similar support tickets.
    
    Args:
        company_id: Company to search within
        message: Message to search for
        db: Database session
        limit: Maximum number of results
        
    Returns:
        List of similar SupportTicket objects
    """
    # Get all tickets for this company
    tickets = db.query(SupportTicket).filter(
        SupportTicket.company_id == company_id
    ).order_by(SupportTicket.created_at.desc()).limit(50).all()
    
    if not tickets:
        return []
    
    # Simple keyword matching (lowercased)
    message_lower = message.lower()
    keywords = set(message_lower.split())
    
    # Score each ticket by keyword overlap
    scored_tickets = []
    for ticket in tickets:
        ticket_text = f"{ticket.customer_message} {ticket.ai_reply or ''}".lower()
        ticket_keywords = set(ticket_text.split())
        overlap = len(keywords & ticket_keywords)
        if overlap > 0:
            scored_tickets.append((overlap, ticket))
    
    # Sort by score and return top results
    scored_tickets.sort(reverse=True, key=lambda x: x[0])
    return [ticket for _, ticket in scored_tickets[:limit]]


@register_agent("customer_support")
def handle_customer_support(
    company_id: str,
    instruction: str,
    db: Session,
    ticket_id: Optional[str] = None,
) -> AgentResult:
    """
    Handle a customer support inquiry.
    
    Args:
        company_id: Company receiving the support request
        instruction: The customer message
        db: Database session
        ticket_id: Optional existing ticket ID to update
        
    Returns:
        AgentResult with summary and ticket data
    """
    # Get company info for context
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"Company {company_id} not found")
    
    # Search for similar tickets
    similar_tickets = search_similar_tickets(company_id, instruction, db)
    
    # Build context from similar tickets
    similar_context = ""
    if similar_tickets:
        similar_context = "\n\nSimilar past tickets:\n"
        for i, ticket in enumerate(similar_tickets, 1):
            similar_context += f"{i}. Customer: {ticket.customer_message[:100]}...\n"
            if ticket.ai_reply:
                similar_context += f"   Response: {ticket.ai_reply[:100]}...\n"
    
    # Create prompt for Claude
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful customer support agent for {company_name}, a {industry} company.
        Brand voice: {brand_voice}
        
        Your job is to:
        1. Draft a helpful, empathetic response to the customer
        2. Classify the issue (billing, bug, onboarding, or other)
        3. Decide if this needs human escalation (set escalated: true if very complex or angry)
        
        Return your response as valid JSON (no markdown) in this format:
        {{
            "reply": "your helpful response to the customer",
            "tag": "billing|bug|onboarding|other",
            "escalated": true or false,
            "reasoning": "brief internal note about your decision"
        }}
        
        {similar_context}"""),
        ("user", "{message}"),
    ])
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    # Run the chain
    result_text = chain.invoke({
        "company_name": company.name,
        "industry": company.industry,
        "brand_voice": company.brand_voice,
        "similar_context": similar_context,
        "message": instruction,
    })
    
    # Parse result
    try:
        # Clean markdown if present
        cleaned = re.sub(r'```json\s*|\s*```', '', result_text)
        cleaned = cleaned.strip()
        response_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Fallback response
        response_data = {
            "reply": "Thank you for contacting us. We've received your message and will get back to you shortly.",
            "tag": "other",
            "escalated": True,
            "reasoning": f"Failed to parse AI response: {str(e)}"
        }
    
    # Create or update ticket
    if ticket_id:
        # Update existing ticket
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if ticket:
            ticket.ai_reply = response_data["reply"]
            ticket.tag = response_data["tag"]
            ticket.escalated = response_data["escalated"]
            ticket.status = "resolved" if not response_data["escalated"] else "escalated"
        else:
            raise ValueError(f"Ticket {ticket_id} not found")
    else:
        # Create new ticket
        ticket = SupportTicket(
            company_id=company_id,
            customer_message=instruction,
            ai_reply=response_data["reply"],
            tag=response_data["tag"],
            escalated=response_data["escalated"],
            status="resolved" if not response_data["escalated"] else "escalated",
        )
        db.add(ticket)
    
    db.commit()
    db.refresh(ticket)
    
    # Build result
    summary = f"{'Updated' if ticket_id else 'Created'} support ticket: {response_data['tag']} - {'escalated' if response_data['escalated'] else 'resolved'}"
    
    return AgentResult(
        summary=summary,
        data={
            "ticket_id": ticket.id,
            "reply": response_data["reply"],
            "tag": response_data["tag"],
            "escalated": response_data["escalated"],
            "status": ticket.status,
        },
        log_entry=f"Customer Support Agent processed inquiry. "
                  f"Tag: {response_data['tag']}, Escalated: {response_data['escalated']}. "
                  f"Reasoning: {response_data.get('reasoning', 'N/A')}"
    )

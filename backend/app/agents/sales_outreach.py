"""
Sales Outreach Agent — generates personalized outreach sequences for leads.

Uses LangChain to create cold emails and multi-day follow-up cadences.
"""

import json
import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from app.agents.base import AgentResult, register_agent
from app.agents.llm import llm
from app.models.company import Company
from app.models.lead import Lead
from app.models.sequence import Sequence


@register_agent("sales_outreach")
def handle_sales_outreach(
    company_id: str,
    instruction: str,
    db: Session,
    icp: str | None = None,
    leads: list[dict[str, Any]] | None = None,
) -> AgentResult:
    """
    Generate personalized sales outreach sequences for leads.
    
    Args:
        company_id: Company performing outreach
        instruction: General instruction or context
        db: Database session
        icp: Ideal Customer Profile (optional, uses company ICP if not provided)
        leads: List of lead dicts with name, company_name, email
        
    Returns:
        AgentResult with outreach summary and lead data
    """
    # Get company info
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"Company {company_id} not found")
    
    # Use provided ICP or fall back to company ICP
    target_icp = icp or company.icp
    
    # If no leads provided, try to parse from instruction
    if not leads:
        leads = []
    
    if not leads:
        return AgentResult(
            summary="No leads provided for outreach",
            data={"leads_processed": 0},
            log_entry="Sales outreach called but no leads were provided"
        )
    
    created_leads = []
    
    for lead_info in leads:
        # Create prompt for this lead
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a sales outreach expert for {company_name}, a {industry} company.
            Brand voice: {brand_voice}
            Target ICP: {icp}
            
            Your task is to create a personalized cold outreach sequence for a lead.
            
            Generate:
            1. A personalized cold email (subject + body)
            2. A 4-5 day follow-up cadence with specific actions per day
            3. A tier score (Tier 1 = high priority, Tier 2 = medium, Tier 3 = low)
            
            Return ONLY valid JSON (no markdown) in this format:
            {{
                "initial_email": {{
                    "subject": "email subject line",
                    "body": "email body with personalization"
                }},
                "sequence": [
                    {{"day": 1, "channel": "email", "content": "Day 1 email content"}},
                    {{"day": 2, "channel": "social", "content": "LinkedIn connection request message"}},
                    {{"day": 3, "channel": "email", "content": "Follow-up email"}},
                    {{"day": 4, "channel": "social", "content": "LinkedIn comment or DM"}},
                    {{"day": 5, "channel": "email", "content": "Final follow-up email"}}
                ],
                "tier": "Tier 1|Tier 2|Tier 3",
                "tier_reasoning": "one-line explanation of tier score"
            }}"""),
            ("user", """Lead details:
            Name: {lead_name}
            Company: {lead_company}
            Email: {lead_email}
            
            Additional context: {instruction}
            
            Generate a personalized outreach sequence for this lead."""),
        ])
        
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Run the chain
        result_text = chain.invoke({
            "company_name": company.name,
            "industry": company.industry,
            "brand_voice": company.brand_voice,
            "icp": target_icp,
            "lead_name": lead_info.get("name", "Unknown"),
            "lead_company": lead_info.get("company_name", "Unknown"),
            "lead_email": lead_info.get("email", ""),
            "instruction": instruction,
        })
        
        # Parse result
        try:
            cleaned = re.sub(r'```json\s*|\s*```', '', result_text)
            cleaned = cleaned.strip()
            outreach_data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Fallback
            outreach_data = {
                "initial_email": {
                    "subject": f"Quick question about {lead_info.get('company_name')}",
                    "body": f"Hi {lead_info.get('name')}, I wanted to reach out..."
                },
                "sequence": [
                    {"day": 1, "channel": "email", "content": "Initial outreach"},
                    {"day": 3, "channel": "email", "content": "Follow-up"},
                    {"day": 5, "channel": "email", "content": "Final check-in"},
                ],
                "tier": "Tier 3",
                "tier_reasoning": f"Failed to parse AI response: {str(e)[:50]}"
            }
        
        # Create or update lead
        existing_lead = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.email == lead_info.get("email", "")
        ).first()
        
        if existing_lead:
            # Update existing lead
            existing_lead.name = lead_info.get("name", existing_lead.name)
            existing_lead.company_name = lead_info.get("company_name", existing_lead.company_name)
            existing_lead.tier = outreach_data.get("tier", "Tier 3")
            lead = existing_lead
        else:
            # Create new lead
            lead = Lead(
                company_id=company_id,
                name=lead_info.get("name", "Unknown"),
                company_name=lead_info.get("company_name", "Unknown"),
                email=lead_info.get("email", ""),
                tier=outreach_data.get("tier", "Tier 3"),
                stage="Open",
            )
            db.add(lead)
        
        db.commit()
        db.refresh(lead)
        
        # Create sequence entries
        for seq_item in outreach_data.get("sequence", []):
            sequence = Sequence(
                lead_id=lead.id,
                day=seq_item.get("day", 1),
                channel=seq_item.get("channel", "email"),
                content=seq_item.get("content", ""),
                sent=False,
            )
            db.add(sequence)
        
        db.commit()
        
        created_leads.append({
            "lead_id": lead.id,
            "name": lead.name,
            "company": lead.company_name,
            "tier": lead.tier,
            "tier_reasoning": outreach_data.get("tier_reasoning", ""),
            "initial_email": outreach_data.get("initial_email"),
            "sequence_count": len(outreach_data.get("sequence", [])),
        })
    
    summary = f"Created outreach for {len(created_leads)} lead(s)"
    if created_leads:
        tiers = [l["tier"] for l in created_leads]
        summary += f" - Tiers: {', '.join(tiers)}"
    
    return AgentResult(
        summary=summary,
        data={
            "leads_processed": len(created_leads),
            "leads": created_leads,
        },
        log_entry=f"Sales Outreach Agent processed {len(created_leads)} lead(s). "
                  f"Generated personalized sequences with ICP: {target_icp[:50]}..."
    )

"""
Test suite for sales outreach agent and coordinator routing.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.models.user import User
from app.models.company import Company
from app.models.lead import Lead
from app.models.sequence import Sequence
from app.agents.sales_outreach import handle_sales_outreach
from app.agents.coordinator import coordinate_task

# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Check if we have a valid API key
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
HAS_VALID_API_KEY = ANTHROPIC_API_KEY and not ANTHROPIC_API_KEY.startswith("sk-ant-XXX")


@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_company(db):
    """Create a test user and company."""
    user = User(
        email="test_sales@example.com",
        hashed_password="fake_hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    company = Company(
        owner_id=user.id,
        name="Test Sales Company",
        industry="SaaS",
        icp="CTOs of mid-size tech companies",
        brand_voice="Professional and direct",
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company


@pytest.mark.skipif(not HAS_VALID_API_KEY, reason="No valid Anthropic API key")
def test_create_sales_outreach_with_llm(db, test_company):
    """Test that sales outreach agent creates leads and sequences."""
    leads = [
        {
            "name": "Jane Doe",
            "company_name": "TechCorp",
            "email": "jane@techcorp.example.com"
        }
    ]
    
    result = handle_sales_outreach(
        company_id=test_company.id,
        instruction="Pitch our new AI product that saves 20 hours a week.",
        db=db,
        icp="VPs of Engineering",
        leads=leads
    )
    
    assert result.summary is not None
    assert "Created outreach" in result.summary
    assert result.data is not None
    assert result.data["leads_processed"] == 1
    
    # Verify lead was created in database
    lead = db.query(Lead).filter(
        Lead.company_id == test_company.id
    ).first()
    
    assert lead is not None
    assert lead.name == "Jane Doe"
    assert lead.company_name == "TechCorp"
    assert lead.tier in ["Tier 1", "Tier 2", "Tier 3"]
    
    # Verify sequences
    sequences = db.query(Sequence).filter(Sequence.lead_id == lead.id).all()
    assert len(sequences) > 0, "Should have generated follow-up sequence"
    assert any(s.channel == "email" for s in sequences)
    
    print("\n[PASS] Test passed: Sales outreach sequence created successfully")
    print(f"  Lead Tier: {lead.tier}")
    print(f"  Sequence steps: {len(sequences)}")


@pytest.mark.skipif(not HAS_VALID_API_KEY, reason="No valid Anthropic API key")
def test_coordinator_routing(db, test_company):
    """Test that the coordinator correctly routes prompts to different agents."""
    
    # 1. Test Customer Support routing
    support_msg = "A customer is complaining that they cannot log into their account. Please help them."
    decision1 = coordinate_task(test_company.id, support_msg, db)
    
    assert decision1["agent"] == "customer_support", f"Expected customer_support, got {decision1['agent']}"
    
    # 2. Test Sales Outreach routing
    sales_msg = "Generate an outreach email for John Smith at Acme Corp regarding our new tool."
    decision2 = coordinate_task(test_company.id, sales_msg, db)
    
    assert decision2["agent"] == "sales_outreach", f"Expected sales_outreach, got {decision2['agent']}"
    
    print("\n[PASS] Test passed: Coordinator routing logic works for both agents")
    print(f"  Routed support msg to: {decision1['agent']} (Reasoning: {decision1.get('reasoning')})")
    print(f"  Routed sales msg to: {decision2['agent']} (Reasoning: {decision2.get('reasoning')})")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

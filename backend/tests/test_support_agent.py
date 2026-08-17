"""
Test suite for customer support agent.

Tests the agent function directly without HTTP layer.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.models.user import User
from app.models.company import Company
from app.models.support_ticket import SupportTicket
from app.agents.customer_support import handle_customer_support, search_similar_tickets


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
    # Create user
    user = User(
        email="test@example.com",
        hashed_password="fake_hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create company
    company = Company(
        owner_id=user.id,
        name="Test Company",
        industry="SaaS",
        icp="B2B software companies",
        brand_voice="Professional and friendly",
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company


def test_similar_ticket_search_basic(db, test_company):
    """Test that similar ticket search works without LLM."""
    # Create some tickets manually with specific keywords
    ticket1 = SupportTicket(
        company_id=test_company.id,
        customer_message="I cant access my account",
        ai_reply="Try resetting your password",
        tag="bug",
        escalated=False,
        status="resolved",
    )
    ticket2 = SupportTicket(
        company_id=test_company.id,
        customer_message="Billing question about my invoice",
        ai_reply="Your invoice is available in settings",
        tag="billing",
        escalated=False,
        status="resolved",
    )
    db.add_all([ticket1, ticket2])
    db.commit()
    
    # Search for similar tickets using matching keywords
    results = search_similar_tickets(
        test_company.id,
        "account password",  # Will match "account" in ticket1 and "password" in reply
        db,
        limit=3
    )
    
    assert len(results) > 0, "Should find tickets with matching keywords"
    assert any("account" in t.customer_message.lower() for t in results)
    
    print("\n[PASS] Test passed: Similar ticket search works")
    print(f"  Found {len(results)} similar tickets")
    for i, ticket in enumerate(results, 1):
        print(f"  {i}. {ticket.customer_message[:50]}...")


@pytest.mark.skipif(not HAS_VALID_API_KEY, reason="No valid Anthropic API key")
def test_create_support_ticket_with_llm(db, test_company):
    """Test that customer support agent creates a support ticket (requires API key)."""
    # Run the agent
    result = handle_customer_support(
        company_id=test_company.id,
        instruction="I cant log in to my account. Keep getting an error.",
        db=db,
    )
    
    # Verify result
    assert result.summary is not None
    assert "ticket" in result.summary.lower()
    assert result.data is not None
    assert "ticket_id" in result.data
    assert "reply" in result.data
    assert "tag" in result.data
    assert result.log_entry is not None
    
    # Verify ticket was created in database
    ticket = db.query(SupportTicket).filter(
        SupportTicket.id == result.data["ticket_id"]
    ).first()
    
    assert ticket is not None
    assert ticket.company_id == test_company.id
    assert ticket.customer_message == "I cant log in to my account. Keep getting an error."
    assert ticket.ai_reply is not None
    assert ticket.tag in ["billing", "bug", "onboarding", "other"]
    assert ticket.escalated in [True, False]
    assert ticket.status in ["open", "resolved", "escalated"]
    
    print("\n[PASS] Test passed: Support ticket created successfully")
    print(f"  Ticket ID: {ticket.id}")
    print(f"  Tag: {ticket.tag}")
    print(f"  Escalated: {ticket.escalated}")
    print(f"  Status: {ticket.status}")
    print(f"  AI Reply: {ticket.ai_reply[:100]}...")


def test_agent_registry():
    """Test that customer support agent is registered."""
    from app.agents import AGENTS
    
    assert "customer_support" in AGENTS
    assert callable(AGENTS["customer_support"])
    
    print("\n[PASS] Test passed: Customer support agent is registered")
    print(f"  Available agents: {list(AGENTS.keys())}")


def test_support_ticket_creation_without_llm(db, test_company):
    """Test that we can create support tickets manually (database test)."""
    ticket = SupportTicket(
        company_id=test_company.id,
        customer_message="Test message",
        ai_reply="Test reply",
        tag="other",
        escalated=False,
        status="resolved",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    assert ticket.id is not None
    assert ticket.company_id == test_company.id
    assert ticket.customer_message == "Test message"
    
    # Verify we can query it back
    found = db.query(SupportTicket).filter(SupportTicket.id == ticket.id).first()
    assert found is not None
    assert found.customer_message == "Test message"
    
    print("\n[PASS] Test passed: Support ticket database operations work")
    print(f"  Ticket ID: {ticket.id}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])


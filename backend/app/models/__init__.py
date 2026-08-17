"""
ORM models package.

Import all models here so Alembic can discover them via Base.metadata.
"""

from app.core.db import Base

# Import all models for Alembic auto-discovery
from app.models.user import User
from app.models.company import Company
from app.models.activity_log import ActivityLog
from app.models.support_ticket import SupportTicket
from app.models.lead import Lead
from app.models.sequence import Sequence
from app.models.content_item import ContentItem
from app.models.campaign import Campaign

__all__ = [
    "Base",
    "User",
    "Company",
    "ActivityLog",
    "SupportTicket",
    "Lead",
    "Sequence",
    "ContentItem",
    "Campaign",
]

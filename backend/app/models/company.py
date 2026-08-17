"""
Company model — each user owns one or more companies.
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    owner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(255), nullable=False)
    icp: Mapped[str] = mapped_column(Text, nullable=False)  # Ideal Customer Profile
    brand_voice: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="companies")
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    support_tickets: Mapped[list["SupportTicket"]] = relationship(
        "SupportTicket",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    content_items: Mapped[list["ContentItem"]] = relationship(
        "ContentItem",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id!r}, name={self.name!r})>"

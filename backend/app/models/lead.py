"""
Lead model — sales leads with tier and stage tracking.
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    tier: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        # Valid values: "Tier 1", "Tier 2", "Tier 3"
    )
    stage: Mapped[str] = mapped_column(
        String(50),
        default="Open",
        nullable=False,
        # Valid values: Open, Trying to Contact, Contacted, Consult, Pitch,
        # Verbal Commit, Closed Won, Closed Lost
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="leads")
    sequences: Mapped[list["Sequence"]] = relationship(
        "Sequence",
        back_populates="lead",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Lead(id={self.id!r}, name={self.name!r}, tier={self.tier!r})>"

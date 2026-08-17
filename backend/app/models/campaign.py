"""
Campaign model — marketing campaigns with budget and channel tracking.
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.db import Base


class Campaign(Base):
    __tablename__ = "campaigns"

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
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    budget: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    channel_mix: Mapped[dict] = mapped_column(JSON, nullable=False)
    ad_variants: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="campaigns")

    def __repr__(self) -> str:
        return f"<Campaign(id={self.id!r}, budget={self.budget})>"

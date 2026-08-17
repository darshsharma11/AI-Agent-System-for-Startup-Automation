"""
Sequence model — scheduled outreach messages for leads.
"""

from uuid import uuid4

from sqlalchemy import String, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Sequence(Base):
    __tablename__ = "sequences"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    lead_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        # Valid values: email, social, dm
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="sequences")

    def __repr__(self) -> str:
        return f"<Sequence(id={self.id!r}, day={self.day}, channel={self.channel!r})>"

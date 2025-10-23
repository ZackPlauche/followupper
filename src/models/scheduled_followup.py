"""Scheduled follow-up model for tracking automated messages."""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class ScheduledFollowup(Base):
    """Scheduled follow-up model for tracking automated messages."""

    __tablename__ = 'scheduled_followups'

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey('message_templates.id'), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), default='pending', index=True)  # 'pending', 'sent', 'failed', 'cancelled'
    platform = Column(String(50), nullable=False, index=True)
    sent_date = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    contact = relationship("Contact", back_populates="scheduled_followups")
    template = relationship("MessageTemplate", back_populates="scheduled_followups")

    def __repr__(self):
        return f"<ScheduledFollowup(id={self.id}, contact_id={self.contact_id}, status='{self.status}')>"

    @property
    def is_overdue(self):
        """Check if the follow-up is overdue."""
        return self.status == 'pending' and datetime.now(timezone.utc) > self.scheduled_date

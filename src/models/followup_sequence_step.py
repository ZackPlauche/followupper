"""Follow-up sequence step model for individual steps in a sequence."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class FollowupSequenceStep(Base):
    """Individual step in a follow-up sequence."""

    __tablename__ = 'followup_sequence_steps'

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey('followup_sequences.id'), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    delay_days = Column(Integer, nullable=False)  # Days after previous step (or start)
    template_id = Column(Integer, ForeignKey('message_templates.id'), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    sequence = relationship("FollowupSequence", back_populates="sequence_steps")
    template = relationship("MessageTemplate")

    def __repr__(self):
        return f"<FollowupSequenceStep(id={self.id}, sequence_id={self.sequence_id}, step={self.step_number})>"

    @property
    def total_delay_days(self):
        """Calculate total delay from sequence start."""
        # This would need to be calculated based on all previous steps
        # For now, just return the delay_days
        return self.delay_days

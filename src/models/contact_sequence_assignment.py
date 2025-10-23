"""Contact sequence assignment model for assigning follow-up sequences to contacts."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class ContactSequenceAssignment(Base):
    """Assignment of a follow-up sequence to a contact."""

    __tablename__ = 'contact_sequence_assignments'

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False, index=True)
    sequence_id = Column(Integer, ForeignKey('followup_sequences.id'), nullable=False, index=True)
    status = Column(String(50), default='active', index=True)  # 'active', 'paused', 'completed', 'cancelled'
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    current_step = Column(Integer, default=1)  # Which step they're currently on
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    contact = relationship("Contact", back_populates="sequence_assignments")
    sequence = relationship("FollowupSequence", back_populates="contact_assignments")

    def __repr__(self):
        return f"<ContactSequenceAssignment(id={self.id}, contact_id={self.contact_id}, sequence_id={self.sequence_id})>"

    @property
    def next_step_date(self):
        """Calculate when the next step should be executed."""
        if not self.sequence or not self.sequence.sequence_steps:
            return None

        # Find the current step
        current_step = next(
            (step for step in self.sequence.sequence_steps if step.step_number == self.current_step),
            None
        )

        if not current_step:
            return None

        # Calculate delay from the last contact date or assignment start
        from datetime import timedelta
        base_date = self.contact.last_contact_date or self.started_at
        return base_date + timedelta(days=current_step.delay_days)

    @property
    def is_overdue(self):
        """Check if the current step is overdue."""
        next_date = self.next_step_date
        if not next_date:
            return False
        return datetime.now(timezone.utc) > next_date

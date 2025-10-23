"""Follow-up sequence model for managing multi-step follow-up campaigns."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class FollowupSequence(Base):
    """Follow-up sequence model for managing multi-step follow-up campaigns."""

    __tablename__ = 'followup_sequences'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    platform = Column(String(50), nullable=False, index=True)  # 'email', 'codementor', 'both'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    sequence_steps = relationship("FollowupSequenceStep", back_populates="sequence", cascade="all, delete-orphan")
    contact_assignments = relationship("ContactSequenceAssignment", back_populates="sequence", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FollowupSequence(id={self.id}, name='{self.name}', platform='{self.platform}')>"

    @property
    def total_duration_days(self):
        """Calculate total duration of the sequence in days."""
        if not self.sequence_steps:
            return 0
        return max(step.delay_days for step in self.sequence_steps)

    @property
    def step_count(self):
        """Get the number of steps in this sequence."""
        return len(self.sequence_steps)

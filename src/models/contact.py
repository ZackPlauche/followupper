"""Contact model for managing client information."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class Contact(Base):
    """Contact model for storing client information."""

    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    codementor_username = Column(String(255), unique=True, index=True)
    platform_preference = Column(String(50), default='email')  # 'email', 'codementor', 'both'
    last_contact_date = Column(DateTime)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    scheduled_followups = relationship("ScheduledFollowup", back_populates="contact", cascade="all, delete-orphan")
    sequence_assignments = relationship("ContactSequenceAssignment", back_populates="contact", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', email='{self.email}')>"

    @property
    def active_sequences(self):
        """Get all active sequence assignments for this contact."""
        return [assignment for assignment in self.sequence_assignments if assignment.is_active and assignment.status == 'active']

    @property
    def next_followup_date(self):
        """Calculate the next follow-up date from active sequences."""
        active_assignments = self.active_sequences
        if not active_assignments:
            return None

        # Find the earliest next step date
        next_dates = [assignment.next_step_date for assignment in active_assignments if assignment.next_step_date]
        if not next_dates:
            return None

        return min(next_dates)

    @property
    def first_name(self):
        """Extract first name from full name."""
        if not self.name:
            return ""
        return self.name.split()[0] if self.name else ""

    @property
    def last_name(self):
        """Extract last name from full name."""
        if not self.name:
            return ""
        name_parts = self.name.split()
        return name_parts[-1] if len(name_parts) > 1 else ""

    @property
    def display_name(self):
        """Get display name for templates."""
        return self.name or "Unknown"

    @property
    def email_domain(self):
        """Extract email domain for templates."""
        if not self.email or "@" not in self.email:
            return ""
        return self.email.split("@")[1]

    def get_template_data(self):
        """Get contact data formatted for template substitution."""
        return {
            'user': {
                'name': self.name or '',
                'first_name': self.first_name,
                'last_name': self.last_name,
                'display_name': self.display_name,
                'email': self.email or '',
                'email_domain': self.email_domain,
                'codementor_username': self.codementor_username or '',
                'platform_preference': self.platform_preference or 'email',
                'notes': self.notes or '',
                'is_active': self.is_active,
                'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
                'updated_at': self.updated_at.strftime('%Y-%m-%d') if self.updated_at else ''
            },
            'contact': {
                'name': self.name or '',
                'first_name': self.first_name,
                'last_name': self.last_name,
                'display_name': self.display_name,
                'email': self.email or '',
                'email_domain': self.email_domain,
                'codementor_username': self.codementor_username or '',
                'platform_preference': self.platform_preference or 'email',
                'notes': self.notes or '',
                'is_active': self.is_active,
                'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
                'updated_at': self.updated_at.strftime('%Y-%m-%d') if self.updated_at else ''
            }
        }

"""Message template model for follow-up messages."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class MessageTemplate(Base):
    """Message template model for storing follow-up message templates."""

    __tablename__ = 'message_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    scheduled_followups = relationship("ScheduledFollowup", back_populates="template")

    def __repr__(self):
        return f"<MessageTemplate(id={self.id}, name='{self.name}')>"

    def render_template(self, contact_data):
        """Render the template with contact data substitution."""
        import re
        import emoji

        # Get the template data from contact
        template_data = contact_data.get_template_data()

        # Render subject
        rendered_subject = self.subject or ""
        if rendered_subject:
            for key, value in template_data['user'].items():
                rendered_subject = rendered_subject.replace(f"{{user.{key}}}", str(value))
            for key, value in template_data['contact'].items():
                rendered_subject = rendered_subject.replace(f"{{contact.{key}}}", str(value))
            # Process emojis
            rendered_subject = emoji.emojize(rendered_subject, use_aliases=True)

        # Render body
        rendered_body = self.body or ""
        if rendered_body:
            for key, value in template_data['user'].items():
                rendered_body = rendered_body.replace(f"{{user.{key}}}", str(value))
            for key, value in template_data['contact'].items():
                rendered_body = rendered_body.replace(f"{{contact.{key}}}", str(value))
            # Process emojis
            rendered_body = emoji.emojize(rendered_body, use_aliases=True)

        return {
            'subject': rendered_subject,
            'body': rendered_body
        }

    def get_available_variables(self):
        """Get list of available template variables."""
        return {
            'user': {
                'name': 'Full name',
                'first_name': 'First name',
                'last_name': 'Last name',
                'display_name': 'Display name',
                'email': 'Email address',
                'email_domain': 'Email domain',
                'codementor_username': 'Codementor username',
                'platform_preference': 'Platform preference',
                'notes': 'Notes',
                'is_active': 'Active status',
                'created_at': 'Created date',
                'updated_at': 'Updated date'
            },
            'contact': {
                'name': 'Full name',
                'first_name': 'First name',
                'last_name': 'Last name',
                'display_name': 'Display name',
                'email': 'Email address',
                'email_domain': 'Email domain',
                'codementor_username': 'Codementor username',
                'platform_preference': 'Platform preference',
                'notes': 'Notes',
                'is_active': 'Active status',
                'created_at': 'Created date',
                'updated_at': 'Updated date'
            }
        }

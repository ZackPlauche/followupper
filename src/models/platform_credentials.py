"""Platform credentials model for storing encrypted API credentials."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime, timezone
from .database import Base


class PlatformCredentials(Base):
    """Platform credentials model for storing encrypted API credentials."""

    __tablename__ = 'platform_credentials'

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, unique=True, index=True)  # 'gmail', 'codementor'
    encrypted_credentials = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PlatformCredentials(id={self.id}, platform='{self.platform}')>"

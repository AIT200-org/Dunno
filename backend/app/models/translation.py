from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base
import datetime


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True, index=True)
    source_lang = Column(String, nullable=False)
    target_lang = Column(String, nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    user = relationship("User", back_populates="translations")
    message = relationship("Message", back_populates="translations")

    __table_args__ = (
        UniqueConstraint("message_id", "target_lang", name="uq_translation_message_target"),
        Index("ix_translation_message_target", "message_id", "target_lang"),
    )

    def __repr__(self):
        return f"<Translation(id={self.id}, message_id={self.message_id})>"

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import datetime


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    source_lang = Column(String, nullable=False)
    target_lang = Column(String, nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="translations")
    message = relationship("Message", back_populates="translations")

    def __repr__(self):
        return f"<Translation(id={self.id}, message_id={self.message_id})>"

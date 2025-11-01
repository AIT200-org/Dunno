from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import datetime


class SpeechData(Base):
    __tablename__ = "speech_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    audio_path = Column(String, nullable=False)
    duration = Column(Float, nullable=True)
    language = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="speech_data")
    message = relationship("Message", back_populates="speech")

    def __repr__(self):
        return f"<SpeechData(id={self.id}, path={self.audio_path})>"

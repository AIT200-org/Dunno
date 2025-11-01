from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from .base import Base
import datetime


class Message(Base):
	__tablename__ = "messages"

	id = Column(Integer, primary_key=True, index=True)
	content = Column(Text, nullable=False)
	language = Column(String, nullable=True)
	created_at = Column(DateTime, default=datetime.datetime.utcnow)
	owner_id = Column(Integer, ForeignKey("users.id"))
	group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
	# flag marking if message has been auto-translated
	is_translated = Column(Boolean, default=False)

	# relationships
	owner = relationship("User", back_populates="messages")
	translations = relationship("Translation", back_populates="message")
	speech = relationship("SpeechData", back_populates="message")

	def __repr__(self):
		return f"<Message(id={self.id}, owner_id={self.owner_id})>"


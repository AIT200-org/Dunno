from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from .base import Base
import datetime


class Message(Base):
	__tablename__ = "messages"

	id = Column(Integer, primary_key=True, index=True)
	content = Column(Text, nullable=False)
	language = Column(String, nullable=True)
	created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
	owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
	group_id = Column(Integer, ForeignKey("groups.id", ondelete="SET NULL"), nullable=True, index=True)
	# flag marking if message has been auto-translated
	is_translated = Column(Boolean, default=False)

	# relationships
	owner = relationship("User", back_populates="messages")
	translations = relationship("Translation", back_populates="message", cascade="all, delete-orphan")
	speech = relationship("SpeechData", back_populates="message", cascade="all, delete-orphan")
	# relationship to Group
	group = relationship("Group", back_populates="messages")

	def __repr__(self):
		return f"<Message(id={self.id}, owner_id={self.owner_id})>"


# Index to support queries like: messages by owner ordered by created_at
from sqlalchemy import Index
Index("ix_messages_owner_created", Message.__table__.c.owner_id, Message.__table__.c.created_at)


from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import datetime


class Message(Base):
	__tablename__ = "messages"

	id = Column(Integer, primary_key=True, index=True)
	content = Column(Text, nullable=False)
	created_at = Column(DateTime, default=datetime.datetime.utcnow)
	owner_id = Column(Integer, ForeignKey("users.id"))

	# relationship to User (owner)
	owner = relationship("User")

	def __repr__(self):
		return f"<Message(id={self.id}, owner_id={self.owner_id})>"


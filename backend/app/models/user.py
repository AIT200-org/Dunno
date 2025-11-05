from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, index=True, nullable=False)
	email = Column(String, unique=True, index=True, nullable=False)
	# preferred language for UI and messages
	preferred_language = Column(String, default="en", index=True)
	# whether the user wants messages auto-translated to their preferred language
	translate_enabled = Column(Boolean, default=False)

	# relationships
	groups = relationship("Group", secondary="user_groups", back_populates="members")
	messages = relationship("Message", back_populates="owner")
	translations = relationship("Translation", back_populates="user")
	speech_data = relationship("SpeechData", back_populates="user")

	def __repr__(self):
		return f"<User(id={self.id}, username={self.username})>"


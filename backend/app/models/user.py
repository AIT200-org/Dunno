from sqlalchemy import Column, Integer, String
from .base import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, index=True, nullable=False)
	email = Column(String, unique=True, index=True, nullable=False)
	language = Column(String, default="en")

	def __repr__(self):
		return f"<User(id={self.id}, username={self.username})>"


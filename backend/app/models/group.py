from sqlalchemy import Column, Integer, String
from .base import Base


class Group(Base):
	__tablename__ = "groups"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, nullable=False)

	def __repr__(self):
		return f"<Group(id={self.id}, name={self.name})>"


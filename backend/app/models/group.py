from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Group(Base):
	__tablename__ = "groups"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, nullable=False)
	description = Column(String, nullable=True)

	# many-to-many members
	members = relationship("User", secondary="user_groups", back_populates="groups")

	def __repr__(self):
		return f"<Group(id={self.id}, name={self.name})>"


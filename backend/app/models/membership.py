from sqlalchemy import Table, Column, Integer, ForeignKey
from .base import Base


# Association table for many-to-many User <-> Group
user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
)

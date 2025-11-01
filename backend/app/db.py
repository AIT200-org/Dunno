#db.py

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models.base import Base 

DATABASE_URL = "sqlite:///dunno.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}  # nécessaire pour SQLite
)

# Active les clés étrangères dans SQLite
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create database tables for all models. Call this from a setup script or REPL.

    This keeps table creation explicit (not automatic on import).
    """
    from models.base import Base

    Base.metadata.create_all(bind=engine)


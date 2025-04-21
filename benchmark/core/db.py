from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from benchmark.config import DATABASE_URL
from benchmark.core.models import Base

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)
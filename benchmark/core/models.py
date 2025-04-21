import json
import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from benchmark.config import TEST_CASES_FILE

# Pydantic model for test cases
class TestCase(BaseModel):
    id: str
    description: Optional[str] = None
    template_image: Optional[str] = None
    avatars: Optional[List[str]] = []

def load_test_cases() -> List[TestCase]:
    """Load test cases from JSON file."""
    if TEST_CASES_FILE.exists():
        with open(TEST_CASES_FILE, 'r') as f:
            data = json.load(f)
        return [TestCase(**item) for item in data]
    return []

# SQLAlchemy models for persistence
Base = declarative_base()

class Run(Base):
    __tablename__ = 'runs'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    items = relationship('RunItem', back_populates='run')

class RunItem(Base):
    __tablename__ = 'run_items'
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('runs.id'))
    case_id = Column(String)
    tool_id = Column(String)
    status = Column(String)
    image_url = Column(String)
    score = Column(String)
    run = relationship('Run', back_populates='items')

class HumanScore(Base):
    __tablename__ = 'human_scores'
    id = Column(Integer, primary_key=True)
    run_item_id = Column(Integer, ForeignKey('run_items.id'))
    stars = Column(Integer)
    run_item = relationship('RunItem')
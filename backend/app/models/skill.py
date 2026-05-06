from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    summary = Column(Text)
    domain = Column(String)
    usage = Column(String)
    difficulty = Column(String, default="medium")
    tags = Column(Text)
    tools = Column(Text)
    languages = Column(Text)
    tech_stack = Column(Text)
    key_points = Column(Text)
    repo_path = Column(String)
    raw_content = Column(Text)

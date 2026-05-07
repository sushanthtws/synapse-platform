from sqlalchemy import Boolean, Column, Integer, String, Text
from app.db.base import Base


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    slug = Column(String, index=True)
    summary = Column(Text)
    domain = Column(String)
    usage = Column(String)
    tags = Column(Text)
    tools = Column(Text)
    languages = Column(Text)
    tech_stack = Column(Text)
    key_points = Column(Text)
    artifacts = Column(Text)  # JSON array of {path, type, size}
    where_to_use = Column(Text)
    why_to_use = Column(Text)
    how_to_use = Column(Text)
    is_in_use = Column(Boolean, default=False, nullable=False)
    used_at = Column(String)
    repo_path = Column(String)
    raw_content = Column(Text)
    is_complete = Column(Boolean, default=False, nullable=False)

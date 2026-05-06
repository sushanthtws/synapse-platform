from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    owner_id = Column(Integer)

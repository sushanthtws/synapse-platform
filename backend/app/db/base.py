from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_engine(settings.database_url)
Base = declarative_base()

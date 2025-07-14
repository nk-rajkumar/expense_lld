from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


class TimestampMixin:
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

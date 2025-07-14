from db import Base
from base.models import TimestampMixin
from sqlalchemy import Column, String, Float, Date, Text


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    amount = Column(Float, nullable=False)
    description = Column(Text)
    category = Column(String)
    expense_date = Column(Date, nullable=False)

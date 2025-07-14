from base.repository import BaseRepository
from expense.models import Expense
from typing import Any, Dict, List, Optional
from db import get_db
from sqlalchemy.orm import Session


class ExpenseRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, model_instances: List[Expense]) -> List[str]:
        return super().create(model_instances)

    def get_by_id(self, model, record_id):
        return super().get_by_id(model, record_id)

    def update_by_id(self, model, record_id, fields_to_update):
        return super().update_by_id(model, record_id, fields_to_update)

    def delete_by_id(self, model, record_id):
        return super().delete_by_id(model, record_id)

    def list(
        self,
        *,
        model,
        columns=None,
        filters=None,
        sort_by=None,
        skip=0,
        limit=100,
        include_deleted=False
    ):
        return super().list(
            model=model,
            columns=columns,
            filters=filters,
            sort_by=sort_by,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
        )

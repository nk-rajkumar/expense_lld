import logging
from fastapi import Query
from sqlalchemy import Column, desc, asc
from typing import Optional, Dict, Any, List, Type, TypeVar, Generic, Union
from sqlalchemy.orm import DeclarativeBase
from base.schemas.request import SortBy
from db import get_db
from base.utils.short_id import generate_primary_key
from sqlalchemy import asc, desc


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def _generate_id(prefix: str = "Exp") -> str:
        return generate_primary_key(prefix)

    def create(self, model_instances: List[T]) -> List[str]:
        if not isinstance(model_instances, list):
            raise ValueError("model_instances must be a list, even for single records")
        created_expenses = []
        for model_instance in model_instances:
            model_instance.id = self._generate_id()
            self.db.add(model_instance)
            created_expenses.append(model_instance.id)
        self.db.commit()
        return created_expenses

    def get_by_id(self, model: Type[T], record_id: str) -> Optional[Dict[str, Any]]:
        record = self.db.get(model, record_id)
        if record:
            return self._model_to_dict(record)
        return None

    def update_by_id(self, model: Type[T], record_id: str, fields_to_update: T) -> str:
        if not isinstance(fields_to_update, model):
            raise ValueError(
                f"fields_to_update must be an instance of {model.__name__}"
            )

        record = self.db.get(model, record_id)
        if not record:
            raise ValueError(f"Record with ID {record_id} not found for update.")

        for key, value in fields_to_update.__dict__.items():
            if not key.startswith("_"):
                setattr(record, key, value)

        self.db.commit()
        return {"id": record.id, "modified_at": record.modified_at}

    def delete_by_id(self, model: Type[T], record_id: str) -> int:
        record = self.db.get(model, record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return 1
        return 0

    # ------------------------------------------------------------------ #
    # MAIN LIST METHOD
    # ------------------------------------------------------------------ #
    def list(
        self,
        *,
        model,
        columns: Optional[List] = None,
        filters: Optional[Dict[str, Dict[str, Any]]] = None,
        sort_by: Optional[List[Dict[str, Any]]] = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Dict[str, Any]:
        # start query
        query = self.db.query(*(columns if columns else [model]))

        # filters -------------------------------------------------------
        if filters:
            query = self._apply_filters(query, filters, model)

        total_count = query.count()

        # sorting -------------------------------------------------------
        if sort_by:
            query = self._apply_sorting(query, sort_by, model)

        # pagination ----------------------------------------------------
        query_data = query.offset(skip).limit(limit).all()

        # serialise -----------------------------------------------------
        if columns:
            data = [self._row_to_dict(row, columns) for row in query_data]
        else:
            data = [self._model_to_dict(row) for row in query_data]

        print("✅ Final query before execution:", query)
        return {"data": data, "total_count": total_count}

    # ------------------------------------------------------------------ #
    # FILTER HELPER
    # ------------------------------------------------------------------ #
    def _apply_filters(
        self,
        query: Query,
        filters: Dict[str, Dict[str, Any]],
        model,
    ) -> Query:
        for field_name, spec in filters.items():
            if not spec:  # safety‑check
                continue

            column = getattr(model, field_name)  # resolve str → column
            op = spec["op"]
            value = spec["value"]

            if op == "eq":
                query = query.filter(column == value)
            elif op == "gt":
                query = query.filter(column > value)
            elif op == "gte":
                query = query.filter(column >= value)
            elif op == "lt":
                query = query.filter(column < value)
            elif op == "lte":
                query = query.filter(column <= value)
            elif (
                op == "between" and isinstance(value, (list, tuple)) and len(value) == 2
            ):
                query = query.filter(column.between(value[0], value[1]))
            elif op == "startswith":
                query = query.filter(column.startswith(value))
        return query

    # ------------------------------------------------------------------ #
    # SORT HELPER  ← this is the one that was missing
    # ------------------------------------------------------------------ #
    def _apply_sorting(
        self,
        query: Query,
        sort_specs: List[Dict[str, Any]],
        model,
    ) -> Query:
        for spec in sort_specs:
            column = spec["field"]
            order = spec["order"]
            if not hasattr(model, column):
                continue
            # column = getattr(model, field_name)
            query = query.order_by(desc(column) if order == "desc" else asc(column))
        return query

    # ------------------------------------------------------------------ #
    # SERIALISERS
    # ------------------------------------------------------------------ #
    def _to_serializable(self, value):
        """Convert value to a JSON-serializable format if needed."""
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return value

    def _model_to_dict(self, model) -> Dict[str, Any]:
        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            result[column.name] = self._to_serializable(value)
        return result

    def _row_to_dict(self, row_data, columns: List) -> Dict[str, Any]:
        result = {}
        if len(columns) == 1:
            column_name = columns[0].name
            result[column_name] = self._to_serializable(row_data)
        else:
            for i, column in enumerate(columns):
                column_name = column.name
                result[column_name] = self._to_serializable(row_data[i])
        return result

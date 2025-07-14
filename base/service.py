import logging
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict, Type
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from db import get_db
from base.repository import BaseRepository
from sqlalchemy.orm import Session


from base.schemas.request import (
    PaginationRequest,
    BaseFilters,
    SortBy,
    FilterExpression,
    DateRange,
)


logger = logging.getLogger(__name__)


class BaseService(ABC):

    def __init__(self, db: Session):
        self.db = db
        self.repository = self._get_repository()

    @abstractmethod
    def _get_repository(self) -> BaseRepository:
        pass

    def _convert_single_to_sqlalchemy(
        self, pydantic_obj: BaseModel, model_class: Type
    ) -> Any:
        data = pydantic_obj.model_dump(exclude_none=True)
        return model_class(**data)

    def create(self, model_class: Type, pydantic_obj: BaseModel) -> str:
        try:
            sqlalchemy_obj = self._convert_single_to_sqlalchemy(
                pydantic_obj, model_class
            )
            created_ids = self.repository.create([sqlalchemy_obj])
            return created_ids[0]
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}._create_one: {str(e)}")
            from logging import exception

            exception(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    def get_by_id(self, model_class: Type, record_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.repository.get_by_id(model_class, record_id)
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}.get_by_id: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    def update_by_id(
        self, model_class: Type, record_id: str, fields_to_update: BaseModel
    ) -> Optional[Dict[str, Any]]:
        try:
            sqlalchemy_obj_data = self._convert_single_to_sqlalchemy(
                fields_to_update, model_class
            )
            return self.repository.update_by_id(
                model_class, record_id, sqlalchemy_obj_data
            )
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}.update_by_id: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    def delete_by_id(self, model_class: Type, record_id: str):
        try:
            return self.repository.delete_by_id(model_class, record_id)
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}.delete_by_id: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    def list(
        self,
        model_class: Type,
        pagination: PaginationRequest,
        sort_by: List[SortBy] = None,
        filters: Optional[BaseFilters] = None,
        include_deleted: Optional[bool] = False,
        columns: Optional[List] = None,
    ) -> Dict[str, Any]:
        try:
            page, limit = self._validate_pagination(pagination.page, pagination.limit)
            offset = pagination.offset
            print("Received filters raw:", filters)
            filters = self._process_filters(model_class, filters)
            sort_by = self._process_sort_by(model_class, sort_by)

            return self.repository.list(
                model=model_class,
                filters=filters,
                sort_by=sort_by,
                skip=offset,
                limit=limit,
                include_deleted=include_deleted,
                columns=columns,
            )
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}.list: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    def _validate_pagination(self, page, limit) -> tuple[int, int]:
        page = max(1, page)
        limit = min(max(1, limit), 1000)
        return page, limit

    def _process_sort_by(
        self, model: Any, sort_by: List[SortBy]
    ) -> List[Optional[Dict[str, Any]]]:
        if not sort_by:
            return []

        processed_sort = []

        for sort_spec in sort_by:
            field = sort_spec.field
            order = sort_spec.order
            if hasattr(model, field):
                processed_sort.append(
                    {"field": field, "order": order}  # ✅ keep it string only
                )

        return processed_sort

    def _process_filters(
        self, model: Any, filters: BaseFilters
    ) -> Dict[str, Dict[str, Any]]:
        """
        Convert filter specifications from request payload to dictionary of
        field names and filter criteria (used by repository).
        """
        if not filters:
            return {}

        processed_filters = {}

        for field_name in filters.__annotations__.keys():
            field_value = getattr(filters, field_name, None)
            print(f"Checking field: {field_name} with value: {field_value}")

            if isinstance(field_value, FilterExpression):
                processed_filters[field_name] = {
                    "op": field_value.op,
                    "value": field_value.value,
                }

            elif isinstance(field_value, DateRange):
                processed_filters[field_name] = {
                    "op": "between",
                    "value": [field_value.from_, field_value.to],
                }

        print("✅ Processed filters:", processed_filters)
        return processed_filters

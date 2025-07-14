from typing import Union, List, Literal, Optional, Any
from datetime import date
from pydantic import BaseModel, Field


class FilterExpression(BaseModel):
    op: Literal["eq", "gt", "gte", "lt", "lte", "in", "nin", "between", "startswith"]
    value: Union[str, float, int, List[Any], date, List[date]]


class DateRange(BaseModel):
    from_: date = Field(..., alias="from")
    to: date


class BaseFilters(BaseModel):
    pass


class SortBy(BaseModel):
    field: Literal["created_at", "modified_at"]
    order: Literal["asc", "desc"]


class PaginationRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

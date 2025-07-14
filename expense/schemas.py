from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List, Literal
from datetime import datetime, date

from base.schemas.request import (
    BaseFilters,
    FilterExpression,
    DateRange,
    PaginationRequest,
    SortBy,
)
from base.schemas.response import PaginatedResponse


class ExpenseRecord(BaseModel):
    id: str = Field(description="Unique identifier for the expense")
    amount: float = Field(description="Amount of the expense")
    description: Optional[str] = Field(
        default=None, description="Description of the template"
    )
    category: str = Field(description="Category of the expense")
    created_at: Optional[str] = Field(
        default=None, description="Timestamp when the expense was created"
    )
    modified_at: Optional[str] = Field(
        default=None, description="Timestamp when the expense was last modified"
    )


class GetExpenseResponse(BaseModel):
    data: ExpenseRecord = Field(description="Details of the expense")


class CreateExpenseRequest(BaseModel):
    amount: float
    description: Optional[str]
    category: Optional[str]
    expense_date: date


class CreateExpenseResponse(BaseModel):
    message: str
    id: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Item created successfully", "id": "ABC12345"}
        }
    )


class UpdateExpenseRequest(BaseModel):
    amount: Optional[float]
    description: Optional[str]
    category: Optional[str]
    expense_date: Optional[date]


class UpdateExpenseResponse(BaseModel):
    message: str
    id: str
    modified_at: datetime


class DeleteExpenseResponse(BaseModel):
    message: str


class CategoryFilterExpression(BaseModel):
    op: Literal["eq", "startswith"]
    value: str


class ExpenseFilters(BaseFilters):
    amount: Optional[FilterExpression] = None
    expense_date: Optional[DateRange] = None
    category: Optional[CategoryFilterExpression] = None


class ExpenseSortBy(SortBy):
    field: str
    order: str

    @field_validator("field")
    def validate_sort_field(cls, v):
        if v not in {"created_at", "modified_at"}:
            raise ValueError("Can only sort by 'created_at' or 'modified_at'")
        return v


class ListExpenseRequest(BaseModel):
    filters: Optional[ExpenseFilters] = Field(default=None)
    sort_by: Optional[List[ExpenseSortBy]] = Field(default_factory=list)
    pagination: PaginationRequest = Field(default_factory=PaginationRequest)

    @model_validator(mode="before")
    def coerce_filters(cls, values):
        filters = values.get("filters")
        if filters:
            if isinstance(filters.get("amount"), dict):
                filters["amount"] = FilterExpression(**filters["amount"])
            if isinstance(filters.get("category"), dict):
                filters["category"] = CategoryFilterExpression(**filters["category"])
            if isinstance(filters.get("expense_date"), dict):
                filters["expense_date"] = DateRange(**filters["expense_date"])
            values["filters"] = ExpenseFilters(**filters)
        return values


class ListExpenseResponse(PaginatedResponse):
    data: List[ExpenseRecord]

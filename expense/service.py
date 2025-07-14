import logging
from fastapi import HTTPException, status
from typing import Any, Dict, List, Optional, Type
from expense.models import Expense
from expense.schemas import (
    ExpenseRecord,
    CreateExpenseRequest,
    UpdateExpenseRequest,
    ListExpenseRequest,
    ListExpenseResponse,
)
from sqlalchemy.orm import Session
from expense.repository import ExpenseRepository
from base.service import BaseService


logger = logging.getLogger(__name__)


class ExpenseService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = self._get_repository()

    def _get_repository(self) -> ExpenseRepository:
        return ExpenseRepository(self.db)

    def create_expense(self, request: CreateExpenseRequest) -> str:
        id = self.create(model_class=Expense, pydantic_obj=request)
        return id

    def get_expense_by_id(self, expense_id: str) -> ExpenseRecord:
        expense = self.get_by_id(model_class=Expense, record_id=expense_id)
        if not expense:
            logger.error(f"Expense with ID {expense_id} not found.")
            raise ValueError(f"Expense with ID {expense_id} not found.")
        return ExpenseRecord(**expense)

    def update_expense(
        self, expense_id: str, request: UpdateExpenseRequest
    ) -> Dict[str, str]:
        updated_record = self.update_by_id(
            model_class=Expense, record_id=expense_id, fields_to_update=request
        )
        return updated_record

    def delete_expense_by_id(self, expense_id: str) -> ExpenseRecord:
        expense = self.delete_by_id(model_class=Expense, record_id=expense_id)
        if not expense:
            logger.error(f"Expense with ID {expense_id} not found.")
            raise ValueError(f"Expense with ID {expense_id} not found.")
        return f"Expense with ID {expense_id} deleted successfully"

    def list_expense(self, request: ListExpenseRequest) -> ListExpenseResponse:
        try:
            repo_result = self.list(
                model_class=Expense,
                pagination=request.pagination,
                sort_by=request.sort_by,
                filters=request.filters,
                include_deleted=request.include_deleted,
            )
            return ListExpenseResponse.from_repository_result(
                repo_result=repo_result,
                page=request.pagination.page,
                limit=request.pagination.limit,
                record_model=ExpenseRecord,
            )
        except Exception as e:
            logger.error(f"Error in list_expenses: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

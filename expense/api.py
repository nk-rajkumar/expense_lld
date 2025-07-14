import logging
from fastapi import APIRouter, HTTPException, Depends
from expense.schemas import (
    GetExpenseResponse,
    CreateExpenseRequest,
    CreateExpenseResponse,
    UpdateExpenseRequest,
    UpdateExpenseResponse,
    DeleteExpenseResponse,
    ListExpenseRequest,
    ListExpenseResponse,
)
from db import get_db
from sqlalchemy.orm import Session
from expense.service import ExpenseService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expense", tags=["Expense"])


@router.post("/", response_model=CreateExpenseResponse)
async def create_expense(
    request: CreateExpenseRequest, db: Session = Depends(get_db)
) -> CreateExpenseResponse:
    try:
        service = ExpenseService(db)
        result = service.create_expense(request)
        return CreateExpenseResponse(id=result, message="Expense created successfully")
    except Exception as e:
        logger.error(f"Error in create_expense: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{expense_id}", response_model=GetExpenseResponse)
async def get_expense(
    expense_id: str, db: Session = Depends(get_db)
) -> GetExpenseResponse:
    try:
        service = ExpenseService(db)
        result = service.get_expense_by_id(expense_id)
        return GetExpenseResponse(data=result)
    except Exception as e:
        logger.error(f"Error in get_expense: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{expense_id}", response_model=UpdateExpenseResponse)
async def update_expense(
    expense_id: str, request: UpdateExpenseRequest, db: Session = Depends(get_db)
) -> UpdateExpenseResponse:
    try:
        service = ExpenseService(db)
        result = service.update_expense(expense_id, request)
        return UpdateExpenseResponse(
            id=result["id"],
            modified_at=result["modified_at"],
            message="Expense updated successfully",
        )
    except Exception as e:
        logger.error(f"Error in update_expense: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{expense_id}", response_model=DeleteExpenseResponse)
async def delete_expense(
    expense_id: str, db: Session = Depends(get_db)
) -> DeleteExpenseResponse:
    try:
        service = ExpenseService(db)
        result = service.delete_expense_by_id(expense_id)
        return DeleteExpenseResponse(message=result)
    except Exception as e:
        logger.error(f"Error in get_expense: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/list", response_model=ListExpenseResponse)
async def list_expense(
    request: ListExpenseRequest, db: Session = Depends(get_db)
) -> ListExpenseResponse:
    try:
        service = ExpenseService(db)
        return service.list_expense(request)

    except Exception as e:
        logger.error(f"Error in list_expenses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

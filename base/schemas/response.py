from typing import List, Type, Dict, Any
from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    data: List[Any]
    total_count: int
    page: int
    limit: int

    @classmethod
    def from_repository_result(
        cls,
        repo_result: Dict[str, Any],
        page: int,
        limit: int,
        record_model: Type[BaseModel],
    ) -> "PaginatedResponse":
        return cls(
            data=[record_model(**record) for record in repo_result["data"]],
            total_count=repo_result["total_count"],
            page=page,
            limit=limit,
        )

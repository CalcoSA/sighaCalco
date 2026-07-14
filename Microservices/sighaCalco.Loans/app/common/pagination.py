from typing import Generic, List, TypeVar
from dataclasses import dataclass
from math import ceil

T = TypeVar("T")

@dataclass
class PaginationParams:
    page: int = 1
    pageSize: int = 10
    search: str | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.pageSize

@dataclass
class PaginatedResult(Generic[T]):
    items: List[T]
    total: int
    page: int
    pageSize: int
    totalPages: int
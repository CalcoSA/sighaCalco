from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.dtos.LoanLogDto import LoanLogDto
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

class ILoanLogApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, actionDateFrom: Optional[date] = None, actionDateTo: Optional[date] = None,) -> PaginatedResult[LoanLogDto]:
        pass
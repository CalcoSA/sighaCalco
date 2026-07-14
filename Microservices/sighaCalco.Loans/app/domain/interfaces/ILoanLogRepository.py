from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.loanLog import LoanLog
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

class ILoanLogRepository(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, actionDateFrom: Optional[date] = None, actionDateTo: Optional[date] = None,) -> PaginatedResult[LoanLog]:
        pass

    @abstractmethod
    def create(self, loanLogData: LoanLog) -> LoanLog:
        pass
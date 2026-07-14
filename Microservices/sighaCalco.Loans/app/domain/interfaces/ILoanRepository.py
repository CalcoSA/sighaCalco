from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.loan import Loan
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

class ILoanRepository(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, IdLoanStatus: Optional[int] = None, requestDateFrom: Optional[date] = None, requestDateTo: Optional[date] = None) -> PaginatedResult[Loan]:
        pass

    @abstractmethod
    def create(self, loanData: Loan) -> Loan:
        pass
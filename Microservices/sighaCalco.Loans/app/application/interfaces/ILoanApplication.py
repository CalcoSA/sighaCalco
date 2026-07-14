from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.dtos.LoanDto import LoanCreateDto, LoanDto
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

class ILoanApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, IdLoanStatus: Optional[int] = None, requestDateFrom: Optional[date] = None, requestDateTo: Optional[date] = None) -> PaginatedResult[LoanDto]:
        pass

    @abstractmethod
    def create(self, loanData: LoanCreateDto) -> LoanDto:
        pass
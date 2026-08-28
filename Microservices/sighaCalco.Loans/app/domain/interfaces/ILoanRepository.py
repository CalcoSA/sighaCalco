from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.loan import Loan
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

class ILoanRepository(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, IdLoanStatus: Optional[int] = None, requestDateFrom: Optional[date] = None, requestDateTo: Optional[date] = None) -> PaginatedResult[Loan]:
        pass

    @abstractmethod
    def getById(self, IdLoan: int) -> Optional[Loan]:
        pass

    @abstractmethod
    def getByIdForUpdate(self, IdLoan: int) -> Optional[Loan]:
        pass

    @abstractmethod
    def getScheduledLoanIds(self) -> List[int]:
        pass

    @abstractmethod
    def getByIdForScheduled(self, IdLoan: int,) -> Optional[Loan]:
        pass

    @abstractmethod
    def create(self, loanData: Loan) -> Loan:
        pass

    @abstractmethod
    def updateStatus(self, loanData: Loan, IdLoanStatus: int, loanStatusName: str, updatedByUserName: str, updatedAt: datetime) -> Loan:
        pass

    @abstractmethod
    def updateServiceValue(self, loanData: Loan, serviceValue: Decimal, updatedByUserName: str, updatedAt: datetime) -> Loan:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass


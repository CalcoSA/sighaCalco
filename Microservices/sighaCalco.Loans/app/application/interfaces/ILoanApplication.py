from app.domain.dtos.ServiceDiscountHistoryDto import ServiceValueUpdateDto
from app.domain.dtos.LoanDto import LoanCreateDto, LoanDto, LoanUpdateDto
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.dtos.LoanScheduledDto import LoanScheduledDto
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

class ILoanApplication(ABC):

    @abstractmethod
    async def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, IdLoanStatus: Optional[int] = None, requestDateFrom: Optional[date] = None, requestDateTo: Optional[date] = None) -> PaginatedResult[LoanDto]:
        pass

    @abstractmethod
    def create(self, loanData: LoanCreateDto) -> LoanDto:
        pass

    @abstractmethod
    def updateLoanStatus(self, IdLoan: int, loanData: LoanUpdateDto) -> LoanDto:
        pass

    @abstractmethod
    def updateServiceValue(self, IdLoan: int, serviceData: ServiceValueUpdateDto) -> LoanDto:
        pass

    @abstractmethod
    def processScheduledLoans(self, actorUserName: str,) -> LoanScheduledDto:
        pass
from app.domain.entities.loanStatusHistory import LoanStatusHistory
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

class ILoanStatusHistoryRepository(ABC):

    @abstractmethod
    def getById(self, IdLoanStatusHistory: int) -> Optional[LoanStatusHistory]:
        pass

    @abstractmethod
    def getReportDeletions(self, dateFrom: date, dateTo: date,) -> List[LoanStatusHistory]:
        pass

    @abstractmethod
    def getByIdLoan(self, IdLoan: int) -> List[LoanStatusHistory]:
        pass

    @abstractmethod
    def create(self, historyData: LoanStatusHistory) -> LoanStatusHistory:
        pass
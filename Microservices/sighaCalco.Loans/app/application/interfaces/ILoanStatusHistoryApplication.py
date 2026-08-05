from app.domain.dtos.LoanStatusHistoryDto import LoanStatusHistoryDto
from abc import ABC, abstractmethod
from typing import List

class ILoanStatusHistoryApplication(ABC):

    @abstractmethod
    def getById(self, IdLoanStatusHistory: int) -> LoanStatusHistoryDto:
        pass

    @abstractmethod
    def getByIdLoan(self, IdLoan: int) -> List[LoanStatusHistoryDto]:
        pass
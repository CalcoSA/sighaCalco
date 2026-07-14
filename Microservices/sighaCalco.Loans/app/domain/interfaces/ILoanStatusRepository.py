from app.domain.entities.loanStatus import LoanStatus
from abc import ABC, abstractmethod
from typing import List, Optional

class ILoanStatusRepository(ABC):

    @abstractmethod
    def getAll(self) -> List[LoanStatus]:
        pass

    @abstractmethod
    def getById(self, IdLoanStatus: int) -> Optional[LoanStatus]:
        pass

    @abstractmethod
    def create(self, loanStatusData: LoanStatus) -> LoanStatus:
        pass

    @abstractmethod
    def update(self, IdLoanStatus: int, loanStatusData: LoanStatus) -> Optional[LoanStatus]:
        pass

    @abstractmethod
    def delete(self, IdLoanStatus: int) -> bool:
        pass
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.payrollSinergy import PayrollSinergy
from abc import ABC, abstractmethod
from typing import Optional, List

class IPayrollSinergyApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[PayrollSinergy]:
        pass

    @abstractmethod
    def getAllPayroll(self, search: Optional[str] = None) -> List[PayrollSinergy]:
        pass

    @abstractmethod
    def getById(self, IdPayrollSinergy: int) -> PayrollSinergy:
        pass

    @abstractmethod
    def create(self, payrollSinergyData: PayrollSinergy) -> PayrollSinergy:
        pass

    @abstractmethod
    def update(self, IdPayrollSinergy: int, payrollSinergyData: PayrollSinergy) -> PayrollSinergy:
        pass

    @abstractmethod
    def delete(self, IdPayrollSinergy: int) -> bool:
        pass
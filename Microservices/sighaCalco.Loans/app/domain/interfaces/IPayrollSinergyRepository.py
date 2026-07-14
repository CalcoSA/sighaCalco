from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.payrollSinergy import PayrollSinergy
from abc import ABC, abstractmethod
from typing import Optional, List

class IPayrollSinergyRepository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[PayrollSinergy]:
        pass

    @abstractmethod
    def getAllPayroll(self, search: Optional[str] = None) -> List[PayrollSinergy]:
        pass

    @abstractmethod
    def getById(self, IdPayrollSinergy: int) -> Optional[PayrollSinergy]:
        pass

    @abstractmethod
    def getByName(self, namePayrollSinergy: str) -> Optional[PayrollSinergy]:
        pass

    @abstractmethod
    def getByCode(self, codePayrollSinergy: str) -> Optional[PayrollSinergy]:
        pass

    @abstractmethod
    def create(self, payrollSinergyData: PayrollSinergy) -> PayrollSinergy:
        pass

    @abstractmethod
    def update(self, IdPayrollSinergy: int, payrollSinergyData: PayrollSinergy) -> Optional[PayrollSinergy]:
        pass

    @abstractmethod
    def delete(self, IdPayrollSinergy: int) -> bool:
        pass
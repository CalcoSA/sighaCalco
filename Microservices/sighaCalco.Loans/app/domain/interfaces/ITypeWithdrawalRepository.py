from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.typeWithdrawal import TypeWithdrawal
from abc import ABC, abstractmethod
from typing import Optional

class ITypeWithdrawalRepository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[TypeWithdrawal]:
        pass

    @abstractmethod
    def getById(self, IdTypeWithdrawal: int) -> Optional[TypeWithdrawal]:
        pass

    @abstractmethod
    def getByName(self, nameTTypeWithdrawal: str) -> Optional[TypeWithdrawal]:
        pass

    @abstractmethod
    def getByCode(self, codeTypeWithdrawal: str) -> Optional[TypeWithdrawal]:
        pass

    @abstractmethod
    def create(self, typeWithdrawalData: TypeWithdrawal) -> TypeWithdrawal:
        pass

    @abstractmethod
    def update(self, IdTypeWithdrawal: int, typeWithdrawalData: TypeWithdrawal) -> Optional[TypeWithdrawal]:
        pass

    @abstractmethod
    def delete(self, IdTypeWithdrawal: int) -> bool:
        pass
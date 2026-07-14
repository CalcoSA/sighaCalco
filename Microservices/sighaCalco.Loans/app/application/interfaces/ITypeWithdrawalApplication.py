from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.typeWithdrawal import TypeWithdrawal
from abc import ABC, abstractmethod

class ITypeWithdrawalApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[TypeWithdrawal]:
        pass

    @abstractmethod
    def getById(self, IdTypeWithdrawal: int) -> TypeWithdrawal:
        pass

    @abstractmethod
    def create(self, typeWithdrawalData: TypeWithdrawal) -> TypeWithdrawal:
        pass

    @abstractmethod
    def update(self, IdTypeWithdrawal: int, typeWithdrawalData: TypeWithdrawal) -> TypeWithdrawal:
        pass

    @abstractmethod
    def delete(self, IdTypeWithdrawal: int) -> bool:
        pass
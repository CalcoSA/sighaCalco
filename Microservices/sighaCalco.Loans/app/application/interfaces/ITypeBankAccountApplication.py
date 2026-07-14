from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.typeBankAccount import TypeBankAccount
from abc import ABC, abstractmethod

class ITypeBankAccountApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[TypeBankAccount]:
        pass

    @abstractmethod
    def getById(self, IdTypeBankAccount: int) -> TypeBankAccount:
        pass

    @abstractmethod
    def create(self, typeBankAccountData: TypeBankAccount) -> TypeBankAccount:
        pass

    @abstractmethod
    def update(self, IdTypeBankAccount: int, typeBankAccountData: TypeBankAccount) -> TypeBankAccount:
        pass

    @abstractmethod
    def delete(self, IdTypeBankAccount: int) -> bool:
        pass
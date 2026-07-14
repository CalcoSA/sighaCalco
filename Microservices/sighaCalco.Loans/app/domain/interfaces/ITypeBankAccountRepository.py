from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.typeBankAccount import TypeBankAccount
from abc import ABC, abstractmethod
from typing import Optional

class ITypeBankAccountRepository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[TypeBankAccount]:
        pass

    @abstractmethod
    def getById(self, IdTypeBankAccount: int) -> Optional[TypeBankAccount]:
        pass

    @abstractmethod
    def getByName(self, nameTypeBankAccount: str) -> Optional[TypeBankAccount]:
        pass

    @abstractmethod
    def getByCode(self, codeTypeBankAccount: str) -> Optional[TypeBankAccount]:
        pass

    @abstractmethod
    def create(self, typeBankAccountData: TypeBankAccount) -> TypeBankAccount:
        pass

    @abstractmethod
    def update(self, IdTypeBankAccount: int, typeBankAccountData: TypeBankAccount) -> Optional[TypeBankAccount]:
        pass

    @abstractmethod
    def delete(self, IdTypeBankAccount: int) -> bool:
        pass
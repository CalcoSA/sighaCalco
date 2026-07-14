from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.bank import Bank
from abc import ABC, abstractmethod

class IBankApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Bank]:
        pass

    @abstractmethod
    def getById(self, IdBank: int) -> Bank:
        pass

    @abstractmethod
    def create(self, bankData: Bank) -> Bank:
        pass

    @abstractmethod
    def update(self, IdBank: int, bankData: Bank) -> Bank:
        pass

    @abstractmethod
    def delete(self, IdBank: int) -> bool:
        pass
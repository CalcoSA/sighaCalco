from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.incapacity import Incapacity
from abc import ABC, abstractmethod
from typing import Optional

class IIncapacityRepository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Incapacity]:
        pass

    @abstractmethod
    def getById(self, IdIncapacity: int) -> Optional[Incapacity]:
        pass
    
    @abstractmethod
    def getByName(self, nameIncapacity: str) -> Optional[Incapacity]:
        pass

    @abstractmethod
    def getByCode(self, codeIncapacity: str) -> Optional[Incapacity]:
        pass

    @abstractmethod
    def create(self, incapacityData: Incapacity) -> Incapacity:
        pass

    @abstractmethod
    def update(self, IdIncapacity: int, incapacityData: Incapacity) -> Optional[Incapacity]:
        pass

    @abstractmethod
    def delete(self, IdIncapacity: int) -> bool:
        pass
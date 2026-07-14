from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.incapacity import Incapacity
from abc import ABC, abstractmethod

class IIncapacityApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Incapacity]:
        pass

    @abstractmethod
    def getById(self, IdIncapacity: int) -> Incapacity:
        pass

    @abstractmethod
    def create(self, incapacityData: Incapacity) -> Incapacity:
        pass

    @abstractmethod
    def update(self, IdIncapacity: int, incapacityData: Incapacity) -> Incapacity:
        pass

    @abstractmethod
    def delete(self, IdIncapacity: int) -> bool:
        pass
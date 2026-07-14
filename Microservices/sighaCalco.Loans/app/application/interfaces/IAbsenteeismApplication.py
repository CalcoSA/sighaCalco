from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.absenteeism import Absenteeism
from abc import ABC, abstractmethod

class IAbsenteeismApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Absenteeism]:
        pass

    @abstractmethod
    def getById(self, IdAbsenteeism: int) -> Absenteeism:
        pass

    @abstractmethod
    def create(self, absenteeismData: Absenteeism) -> Absenteeism:
        pass

    @abstractmethod
    def update(self, IdAbsenteeism: int, absenteeismData: Absenteeism) -> Absenteeism:
        pass

    @abstractmethod
    def delete(self, IdAbsenteeism: int) -> bool:
        pass
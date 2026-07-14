from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.absenteeism import Absenteeism
from abc import ABC, abstractmethod
from typing import Optional

class IAbsenteeismRepository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Absenteeism]:
        pass

    @abstractmethod
    def getById(self, IdAbsenteeism: int) -> Optional[Absenteeism]:
        pass

    @abstractmethod
    def getByName(self, nameAbsenteeism: str) -> Optional[Absenteeism]:
        pass

    @abstractmethod
    def getByCode(self, codeAbsenteeism: str) -> Optional[Absenteeism]:
        pass

    @abstractmethod
    def create(self, absenteeismData: Absenteeism) -> Absenteeism:
        pass

    @abstractmethod
    def update(self, IdAbsenteeism: int, absenteeismData: Absenteeism) -> Optional[Absenteeism]:
        pass

    @abstractmethod
    def delete(self, IdAbsenteeism: int) -> bool:
        pass
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen2 import DescCen2
from abc import ABC, abstractmethod
from typing import Optional

class IDescCen2Repository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen2]:
        pass

    @abstractmethod
    def getById(self, IdDescCen2: int) -> Optional[DescCen2]:
        pass

    @abstractmethod
    def getByName(self, nameDescCen2: str) -> Optional[DescCen2]:
        pass

    @abstractmethod
    def getByCode(self, codeDescCen2: str) -> Optional[DescCen2]:
        pass

    @abstractmethod
    def create(self, descCen2Data: DescCen2) -> DescCen2:
        pass

    @abstractmethod
    def update(self, IdDescCen2: int, descCen2Data: DescCen2) -> Optional[DescCen2]:
        pass

    @abstractmethod
    def delete(self, IdDescCen2: int) -> bool:
        pass
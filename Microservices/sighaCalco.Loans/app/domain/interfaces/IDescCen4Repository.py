from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen4 import DescCen4
from abc import ABC, abstractmethod
from typing import Optional

class IDescCen4Repository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen4]:
        pass

    @abstractmethod
    def getById(self, IdDescCen4: int) -> Optional[DescCen4]:
        pass

    @abstractmethod
    def getByName(self, nameDescCen4: str) -> Optional[DescCen4]:
        pass

    @abstractmethod
    def getByCode(self, codeDescCen4: str) -> Optional[DescCen4]:
        pass

    @abstractmethod
    def create(self, descCen4Data: DescCen4) -> DescCen4:
        pass

    @abstractmethod
    def update(self, IdDescCen4: int, descCen4Data: DescCen4) -> Optional[DescCen4]:
        pass

    @abstractmethod
    def delete(self, IdDescCen4: int) -> bool:
        pass
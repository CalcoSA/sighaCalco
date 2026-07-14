from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen1 import DescCen1
from abc import ABC, abstractmethod
from typing import Optional

class IDescCen1Repository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen1]:
        pass

    @abstractmethod
    def getById(self, IdDescCen1: int) -> Optional[DescCen1]:
        pass

    @abstractmethod
    def getByName(self, nameDescCen1: str) -> Optional[DescCen1]:
        pass

    @abstractmethod
    def getByCode(self, codeDescCen1: str) -> Optional[DescCen1]:
        pass

    @abstractmethod
    def create(self, descCen1Data: DescCen1) -> DescCen1:
        pass

    @abstractmethod
    def update(self, IdDescCen1: int, descCen1Data: DescCen1) -> Optional[DescCen1]:
        pass

    @abstractmethod
    def delete(self, IdDescCen1: int) -> bool:
        pass
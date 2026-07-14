from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descTsueldo import DescTsueldo
from abc import ABC, abstractmethod
from typing import Optional

class IDescTsueldoRepository(ABC):
    
    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescTsueldo]:
        pass

    @abstractmethod
    def getById(self, IdDescTsueldo: int) -> Optional[DescTsueldo]:
        pass

    @abstractmethod
    def getByName(self, nameDescTsueldo: str) -> Optional[DescTsueldo]:
        pass

    @abstractmethod
    def getByCode(self, codeDescTsueldo: str) -> Optional[DescTsueldo]:
        pass

    @abstractmethod
    def create(self, descTsueldoData: DescTsueldo) -> DescTsueldo:
        pass

    @abstractmethod
    def update(self, IdDescTsueldo: int, descTsueldoData: DescTsueldo) -> Optional[DescTsueldo]:
        pass

    @abstractmethod
    def delete(self, IdDescTsueldo: int) -> bool:
        pass
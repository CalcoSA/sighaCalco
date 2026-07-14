from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen3 import DescCen3
from abc import ABC, abstractmethod

class IDescCen3Application(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen3]:
        pass

    @abstractmethod
    def getById(self, IdDescCen3: int) -> DescCen3:
        pass

    @abstractmethod
    def create(self, descCen3Data: DescCen3) -> DescCen3:
        pass

    @abstractmethod
    def update(self, IdDescCen3: int, descCen3Data: DescCen3) -> DescCen3:
        pass

    @abstractmethod
    def delete(self, IdDescCen3: int) -> bool:
        pass
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen2 import DescCen2
from abc import ABC, abstractmethod

class IDescCen2Application(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen2]:
        pass

    @abstractmethod
    def getById(self, IdDescCen2: int) -> DescCen2:
        pass

    @abstractmethod
    def create(self, descCen2Data: DescCen2) -> DescCen2:
        pass

    @abstractmethod
    def update(self, IdDescCen2: int, descCen2Data: DescCen2) -> DescCen2:
        pass

    @abstractmethod
    def delete(self, IdDescCen2: int) -> bool:
        pass
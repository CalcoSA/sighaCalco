from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen1 import DescCen1
from abc import ABC, abstractmethod

class IDescCen1Application(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen1]:
        pass

    @abstractmethod
    def getById(self, IdDescCen1: int) -> DescCen1:
        pass

    @abstractmethod
    def create(self, descCen1Data: DescCen1) -> DescCen1:
        pass

    @abstractmethod
    def update(self, IdDescCen1: int, descCen1Data: DescCen1) -> DescCen1:
        pass

    @abstractmethod
    def delete(self, IdDescCen1: int) -> bool:
        pass
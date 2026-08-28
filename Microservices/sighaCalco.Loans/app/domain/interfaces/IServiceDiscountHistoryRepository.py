from app.domain.entities.serviceDiscountHistory import ServiceDiscountHistory
from app.common.pagination import PaginationParams, PaginatedResult
from abc import ABC, abstractmethod
from datetime import date

class IServiceDiscountHistoryRepository(ABC):

    @abstractmethod
    def getByIdLoan(self, IdLoan: int, pagination: PaginationParams) -> PaginatedResult[ServiceDiscountHistory]:
        pass

    @abstractmethod
    def exists(self, IdLoan: int, discountDate: date) -> bool:
        pass

    @abstractmethod
    def create(self, historyData: ServiceDiscountHistory) -> ServiceDiscountHistory:
        pass
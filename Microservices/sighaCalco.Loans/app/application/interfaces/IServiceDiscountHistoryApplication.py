from app.domain.dtos.ServiceDiscountHistoryDto import ServiceDiscountHistoryDto
from app.common.pagination import PaginationParams, PaginatedResult
from abc import ABC, abstractmethod

class IServiceDiscountHistoryApplication(ABC):

    @abstractmethod
    def getByIdLoan(self, IdLoan: int, pagination: PaginationParams) -> PaginatedResult[ServiceDiscountHistoryDto]:
        pass
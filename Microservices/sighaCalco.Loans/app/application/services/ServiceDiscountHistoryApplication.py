from app.application.interfaces.IServiceDiscountHistoryApplication import IServiceDiscountHistoryApplication
from app.domain.interfaces.IServiceDiscountHistoryRepository import IServiceDiscountHistoryRepository
from app.domain.dtos.ServiceDiscountHistoryDto import ServiceDiscountHistoryDto
from app.common.pagination import PaginationParams, PaginatedResult

class ServiceDiscountHistoryApplication(IServiceDiscountHistoryApplication):

    def __init__(self, repository: IServiceDiscountHistoryRepository):
        self.repository = repository

    def getByIdLoan(self, IdLoan: int, pagination: PaginationParams) -> PaginatedResult[ServiceDiscountHistoryDto]:
        data = self.repository.getByIdLoan(IdLoan=IdLoan, pagination=pagination)

        return PaginatedResult(
            items=[ServiceDiscountHistoryDto.model_validate(item) for item in data.items],
            total=data.total,
            page=data.page,
            pageSize=data.pageSize,
            totalPages=data.totalPages,
        )
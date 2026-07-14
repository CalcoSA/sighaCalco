from app.application.interfaces.ILoanLogApplication import ILoanLogApplication
from app.domain.interfaces.ILoanLogRepository import ILoanLogRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.dtos.LoanLogDto import LoanLogDto
from app.domain.entities.loanLog import LoanLog
from typing import Optional
from datetime import date

class LoanLogApplication(ILoanLogApplication):

    def __init__(self, loanLogRepository: ILoanLogRepository):
        self.loanLogRepository = loanLogRepository

    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, actionDateFrom: Optional[date] = None, actionDateTo: Optional[date] = None,) -> PaginatedResult[LoanLogDto]:
        data = self.loanLogRepository.getAll(pagination=pagination, employeeDocumentNumber=employeeDocumentNumber, actionDateFrom=actionDateFrom, actionDateTo=actionDateTo,)
        return PaginatedResult(items=[self._toDto(item) for item in data.items], total=data.total, page=data.page, pageSize=data.pageSize, totalPages=data.totalPages,)

    def _toDto(self, loanLog: LoanLog) -> LoanLogDto:
        return LoanLogDto.model_validate(loanLog)
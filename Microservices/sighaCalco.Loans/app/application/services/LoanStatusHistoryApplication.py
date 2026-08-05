from app.application.interfaces.ILoanStatusHistoryApplication import ILoanStatusHistoryApplication
from app.domain.interfaces.ILoanStatusHistoryRepository import ILoanStatusHistoryRepository
from app.domain.dtos.LoanStatusHistoryDto import LoanStatusHistoryDto
from app.domain.entities.loanStatusHistory import LoanStatusHistory
from app.domain.interfaces.ILoanRepository import ILoanRepository
from app.domain.dtos.LoanDto import LoanDto, LoanUpdateDto
from zoneinfo import ZoneInfo
from datetime import datetime
from typing import List

class LoanStatusHistoryApplication(ILoanStatusHistoryApplication):

    def __init__(self, loanRepository: ILoanRepository, historyRepository: ILoanStatusHistoryRepository):
        self.loanRepository = loanRepository
        self.historyRepository = historyRepository

    def _nowColombia(self) -> datetime:
        return datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)

    def getById(self, IdLoanStatusHistory: int) -> LoanStatusHistoryDto:
        historyFound = self.historyRepository.getById(IdLoanStatusHistory)

        if not historyFound:
            raise ValueError("Histórico de estado no encontrado.")

        return LoanStatusHistoryDto.model_validate(historyFound)

    def getByIdLoan(self, IdLoan: int) -> List[LoanStatusHistoryDto]:
        histories = self.historyRepository.getByIdLoan(IdLoan)
        return [
            LoanStatusHistoryDto.model_validate(history)
            for history in histories
        ]
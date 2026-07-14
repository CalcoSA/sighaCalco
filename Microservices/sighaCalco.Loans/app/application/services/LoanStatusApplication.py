from app.application.interfaces.ILoanStatusApplication import ILoanStatusApplication
from app.domain.interfaces.ILoanStatusRepository import ILoanStatusRepository
from app.domain.entities.loanStatus import LoanStatus
from typing import List

class LoanStatusApplication(ILoanStatusApplication):

    def __init__(self, loanStatusRepository: ILoanStatusRepository):
        self.loanStatusRepository = loanStatusRepository

    def getAll(self) -> List[LoanStatus]:
        return self.loanStatusRepository.getAll()

    def getById(self, IdLoanStatus: int) -> LoanStatus:
        loanStatusFound = self.loanStatusRepository.getById(IdLoanStatus)

        if not loanStatusFound:
            raise ValueError("Estado no encontrado.")

        return loanStatusFound

    def create(self, loanStatusData: LoanStatus) -> LoanStatus:

        if not loanStatusData.nameLoanStatus.strip():
            raise ValueError("El nombre del estado es obligatorio.")

        return self.loanStatusRepository.create(loanStatusData)

    def update(self, IdLoanStatus: int, loanStatusData: LoanStatus) -> LoanStatus:
        loanStatusFound = self.loanStatusRepository.getById(IdLoanStatus)

        if not loanStatusFound:
            raise ValueError("Estado no encontrado.")

        if loanStatusData.nameLoanStatus is not None and not loanStatusData.nameLoanStatus.strip():
            raise ValueError("El nombre del estado es obligatorio.")

        updatedLoanStatus = self.loanStatusRepository.update(IdLoanStatus, loanStatusData)

        if not updatedLoanStatus:
            raise ValueError("Estado no encontrado.")

        return updatedLoanStatus

    def delete(self, IdLoanStatus: int) -> bool:
        loanStatusFound = self.loanStatusRepository.getById(IdLoanStatus)

        if not loanStatusFound:
            raise ValueError("Estado no encontrado.")

        return self.loanStatusRepository.delete(IdLoanStatus)
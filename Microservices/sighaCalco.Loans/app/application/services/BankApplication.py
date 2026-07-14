from app.application.interfaces.IBankApplication import IBankApplication
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.interfaces.IBankRepository import IBankRepository
from app.domain.entities.bank import Bank
from typing import Optional

class BankApplication(IBankApplication):

    def __init__(self, bankRepository: IBankRepository):
        self.bankRepository = bankRepository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Bank]:
        return self.bankRepository.getAll(pagination)

    def getById(self, IdBank: int) -> Bank:
        BankFound = self.bankRepository.getById(IdBank)

        if not BankFound:
            raise ValueError("Banco no encontrado.")

        return BankFound

    def create(self, bankData: Bank) -> Bank:
        bankData.nameBank = self._normalizeText(bankData.nameBank)
        bankData.codeBank = self._normalizeText(bankData.codeBank)

        if bankData.nameBank:
            nameExists = self.bankRepository.getByName(bankData.nameBank)

            if nameExists:
                raise ValueError("Ya existe un banco con ese nombre.")

        if bankData.codeBank:
            codeExists = self.bankRepository.getByCode(bankData.codeBank)

            if codeExists:
                raise ValueError("Ya existe un banco con ese código.")

        return self.bankRepository.create(bankData)

    def update(self, IdBank: int, bankData: Bank) -> Bank:
        BankFound = self.bankRepository.getById(IdBank)

        if not BankFound:
            raise ValueError("Banco no encontrado.")

        bankData.nameBank = self._normalizeText(bankData.nameBank)
        bankData.codeBank = self._normalizeText(bankData.codeBank)

        if bankData.nameBank:
            nameExists = self.bankRepository.getByName(bankData.nameBank)

            if nameExists and nameExists.IdBank != IdBank:
                raise ValueError("Ya existe otro banco con ese nombre.")

        if bankData.codeBank:
            codeExists = self.bankRepository.getByCode(bankData.codeBank)

            if codeExists and codeExists.IdBank != IdBank:
                raise ValueError("Ya existe otro banco con ese código.")

        BankUpdated = self.bankRepository.update(IdBank, bankData)

        if not BankUpdated:
            raise ValueError("Banco no encontrado.")

        return BankUpdated

    def delete(self, IdBank: int) -> bool:
        BankFound = self.bankRepository.getById(IdBank)

        if not BankFound:
            raise ValueError("Banco no encontrado.")

        return self.bankRepository.delete(IdBank)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
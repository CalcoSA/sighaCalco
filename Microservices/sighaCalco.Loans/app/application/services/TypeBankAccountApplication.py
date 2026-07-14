from app.application.interfaces.ITypeBankAccountApplication import ITypeBankAccountApplication
from app.domain.interfaces.ITypeBankAccountRepository import ITypeBankAccountRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.typeBankAccount import TypeBankAccount
from typing import Optional

class TypeBankAccountApplication(ITypeBankAccountApplication):

    def __init__(self, typeBankAccountRepository: ITypeBankAccountRepository):
        self.typeBankAccountRepository = typeBankAccountRepository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[TypeBankAccount]:
        return self.typeBankAccountRepository.getAll(pagination)

    def getById(self, IdTypeBankAccount: int) -> TypeBankAccount:
        TypeBankAccountFound = self.typeBankAccountRepository.getById(IdTypeBankAccount)

        if not TypeBankAccountFound:
            raise ValueError("Tipo de cuenta no encontrado.")

        return TypeBankAccountFound

    def create(self, typeBankAccountData: TypeBankAccount) -> TypeBankAccount:
        typeBankAccountData.nameTypeBankAccount = self._normalizeText(typeBankAccountData.nameTypeBankAccount)
        typeBankAccountData.codeTypeBankAccount = self._normalizeText(typeBankAccountData.codeTypeBankAccount)

        if typeBankAccountData.nameTypeBankAccount:
            nameExists = self.typeBankAccountRepository.getByName(typeBankAccountData.nameTypeBankAccount)

            if nameExists:
                raise ValueError("Ya existe un Tipo de cuenta con ese nombre.")

        if typeBankAccountData.codeTypeBankAccount:
            codeExists = self.typeBankAccountRepository.getByCode(typeBankAccountData.codeTypeBankAccount)

            if codeExists:
                raise ValueError("Ya existe un Tipo de cuenta con ese código.")

        return self.typeBankAccountRepository.create(typeBankAccountData)

    def update(self, IdTypeBankAccount: int, typeBankAccountData: TypeBankAccount) -> TypeBankAccount:
        TypeBankAccountFound = self.typeBankAccountRepository.getById(IdTypeBankAccount)

        if not TypeBankAccountFound:
            raise ValueError("Tipo de cuenta no encontrado.")

        typeBankAccountData.nameTypeBankAccount = self._normalizeText(typeBankAccountData.nameTypeBankAccount)
        typeBankAccountData.codeTypeBankAccount = self._normalizeText(typeBankAccountData.codeTypeBankAccount)

        if typeBankAccountData.nameTypeBankAccount:
            nameExists = self.typeBankAccountRepository.getByName(typeBankAccountData.nameTypeBankAccount)

            if nameExists and nameExists.IdTypeBankAccount != IdTypeBankAccount:
                raise ValueError("Ya existe otro Tipo de cuenta con ese nombre.")

        if typeBankAccountData.codeTypeBankAccount:
            codeExists = self.typeBankAccountRepository.getByCode(typeBankAccountData.codeTypeBankAccount)

            if codeExists and codeExists.IdTypeBankAccount != IdTypeBankAccount:
                raise ValueError("Ya existe otro Tipo de cuenta con ese código.")

        TypeBankAccountUpdated = self.typeBankAccountRepository.update(IdTypeBankAccount, typeBankAccountData)

        if not TypeBankAccountUpdated:
            raise ValueError("Tipo de cuenta no encontrado.")

        return TypeBankAccountUpdated

    def delete(self, IdTypeBankAccount: int) -> bool:
        TypeBankAccountFound = self.typeBankAccountRepository.getById(IdTypeBankAccount)

        if not TypeBankAccountFound:
            raise ValueError("Tipo de cuenta no encontrado.")

        return self.typeBankAccountRepository.delete(IdTypeBankAccount)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
from app.application.interfaces.ITypeWithdrawalApplication import ITypeWithdrawalApplication
from app.domain.interfaces.ITypeWithdrawalRepository import ITypeWithdrawalRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.typeWithdrawal import TypeWithdrawal
from typing import Optional

class TypeWithdrawalApplication(ITypeWithdrawalApplication):

    def __init__(self, typeWithdrawalRepository: ITypeWithdrawalRepository):
        self.typeWithdrawalRepository = typeWithdrawalRepository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[TypeWithdrawal]:
        return self.typeWithdrawalRepository.getAll(pagination)

    def getById(self, IdTypeWithdrawal: int) -> TypeWithdrawal:
        TypeWithdrawalFound = self.typeWithdrawalRepository.getById(IdTypeWithdrawal)

        if not TypeWithdrawalFound:
            raise ValueError("Tipo de retiro no encontrado.")

        return TypeWithdrawalFound

    def create(self, typeWithdrawalData: TypeWithdrawal) -> TypeWithdrawal:
        typeWithdrawalData.nameTypeWithdrawal = self._normalizeText(typeWithdrawalData.nameTypeWithdrawal)
        typeWithdrawalData.codeTypeWithdrawal = self._normalizeText(typeWithdrawalData.codeTypeWithdrawal)

        if typeWithdrawalData.nameTypeWithdrawal:
            nameExists = self.typeWithdrawalRepository.getByName(typeWithdrawalData.nameTypeWithdrawal)

            if nameExists:
                raise ValueError("Ya existe un Tipo de retiro con ese nombre.")

        if typeWithdrawalData.codeTypeWithdrawal:
            codeExists = self.typeWithdrawalRepository.getByCode(typeWithdrawalData.codeTypeWithdrawal)

            if codeExists:
                raise ValueError("Ya existe un Tipo de retiro con ese código.")

        return self.typeWithdrawalRepository.create(typeWithdrawalData)

    def update(self, IdTypeWithdrawal: int, typeWithdrawalData: TypeWithdrawal) -> TypeWithdrawal:
        TypeWithdrawalFound = self.typeWithdrawalRepository.getById(IdTypeWithdrawal)

        if not TypeWithdrawalFound:
            raise ValueError("Tipo de retiro no encontrado.")

        typeWithdrawalData.nameTypeWithdrawal = self._normalizeText(typeWithdrawalData.nameTypeWithdrawal)
        typeWithdrawalData.codeTypeWithdrawal = self._normalizeText(typeWithdrawalData.codeTypeWithdrawal)

        if typeWithdrawalData.nameTypeWithdrawal:
            nameExists = self.typeWithdrawalRepository.getByName(typeWithdrawalData.nameTypeWithdrawal)

            if nameExists and nameExists.IdTypeWithdrawal != IdTypeWithdrawal:
                raise ValueError("Ya existe otro Tipo de retiro con ese nombre.")

        if typeWithdrawalData.codeTypeWithdrawal:
            codeExists = self.typeWithdrawalRepository.getByCode(typeWithdrawalData.codeTypeWithdrawal)

            if codeExists and codeExists.IdTypeWithdrawal != IdTypeWithdrawal:
                raise ValueError("Ya existe otro Tipo de retiro con ese código.")

        TypeWithdrawalUpdated = self.typeWithdrawalRepository.update(IdTypeWithdrawal, typeWithdrawalData)

        if not TypeWithdrawalUpdated:
            raise ValueError("Tipo de retiro no encontrado.")

        return TypeWithdrawalUpdated

    def delete(self, IdTypeWithdrawal: int) -> bool:
        TypeWithdrawalFound = self.typeWithdrawalRepository.getById(IdTypeWithdrawal)

        if not TypeWithdrawalFound:
            raise ValueError("Tipo de retiro no encontrado.")

        return self.typeWithdrawalRepository.delete(IdTypeWithdrawal)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
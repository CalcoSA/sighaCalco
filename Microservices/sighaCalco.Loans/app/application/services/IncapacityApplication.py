from app.application.interfaces.IIncapacityApplication import IIncapacityApplication
from app.domain.interfaces.IIncapacityRepository import IIncapacityRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.incapacity import Incapacity
from typing import Optional

class IncapacityApplication(IIncapacityApplication):

    def __init__(self, incapacityRepository: IIncapacityRepository):
        self.incapacityRepository = incapacityRepository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Incapacity]:
        return self.incapacityRepository.getAll(pagination)

    def getById(self, IdIncapacity: int) -> Incapacity:
        IncapacityFound = self.incapacityRepository.getById(IdIncapacity)

        if not IncapacityFound:
            raise ValueError("Incapacidad no encontrada.")

        return IncapacityFound

    def create(self, incapacityData: Incapacity) -> Incapacity:
        incapacityData.nameIncapacity = self._normalizeText(incapacityData.nameIncapacity)
        incapacityData.codeIncapacity = self._normalizeText(incapacityData.codeIncapacity)

        if incapacityData.nameIncapacity:
            nameExists = self.incapacityRepository.getByName(incapacityData.nameIncapacity)

            if nameExists:
                raise ValueError("Ya existe una Incapacidad con ese nombre.")

        if incapacityData.codeIncapacity:
            codeExists = self.incapacityRepository.getByCode(incapacityData.codeIncapacity)

            if codeExists:
                raise ValueError("Ya existe una Incapacidad con ese código.")

        return self.incapacityRepository.create(incapacityData)

    def update(self, IdIncapacity: int, incapacityData: Incapacity) -> Incapacity:
        IncapacityFound = self.incapacityRepository.getById(IdIncapacity)

        if not IncapacityFound:
            raise ValueError("Incapacidad no encontrada.")

        incapacityData.nameIncapacity = self._normalizeText(incapacityData.nameIncapacity)
        incapacityData.codeIncapacity = self._normalizeText(incapacityData.codeIncapacity)

        if incapacityData.nameIncapacity:
            nameExists = self.incapacityRepository.getByName(incapacityData.nameIncapacity)

            if nameExists and nameExists.IdIncapacity != IdIncapacity:
                raise ValueError("Ya existe otra Incapacidad con ese nombre.")

        if incapacityData.codeIncapacity:
            codeExists = self.incapacityRepository.getByCode(incapacityData.codeIncapacity)

            if codeExists and codeExists.IdIncapacity != IdIncapacity:
                raise ValueError("Ya existe otra Incapacidad con ese código.")

        IncapacityUpdated = self.incapacityRepository.update(IdIncapacity, incapacityData)

        if not IncapacityUpdated:
            raise ValueError("Incapacidad no encontrada.")

        return IncapacityUpdated

    def delete(self, IdIncapacity: int) -> bool:
        IncapacityFound = self.incapacityRepository.getById(IdIncapacity)

        if not IncapacityFound:
            raise ValueError("Incapacidad no encontrada.")

        return self.incapacityRepository.delete(IdIncapacity)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
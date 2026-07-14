from app.application.interfaces.IAbsenteeismApplication import IAbsenteeismApplication
from app.domain.interfaces.IAbsenteeismRepository import IAbsenteeismRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.absenteeism import Absenteeism
from typing import Optional

class AbsenteeismApplication(IAbsenteeismApplication):

    def __init__(self, absenteeismRepository: IAbsenteeismRepository):
        self.absenteeismRepository = absenteeismRepository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Absenteeism]:
        return self.absenteeismRepository.getAll(pagination)

    def getById(self, IdAbsenteeism: int) -> Absenteeism:
        absenteeismFound = self.absenteeismRepository.getById(IdAbsenteeism)

        if not absenteeismFound:
            raise ValueError("Ausentismo no encontrado.")

        return absenteeismFound

    def create(self, absenteeismData: Absenteeism) -> Absenteeism:
        absenteeismData.nameAbsenteeism = self._normalizeText(absenteeismData.nameAbsenteeism)
        absenteeismData.codeAbsenteeism = self._normalizeText(absenteeismData.codeAbsenteeism)

        if absenteeismData.nameAbsenteeism:
            nameExists = self.absenteeismRepository.getByName(absenteeismData.nameAbsenteeism)

            if nameExists:
                raise ValueError("Ya existe un ausentismo con ese nombre.")

        if absenteeismData.codeAbsenteeism:
            codeExists = self.absenteeismRepository.getByCode(absenteeismData.codeAbsenteeism)

            if codeExists:
                raise ValueError("Ya existe un ausentismo con ese código.")

        return self.absenteeismRepository.create(absenteeismData)

    def update(self, IdAbsenteeism: int, absenteeismData: Absenteeism) -> Absenteeism:
        absenteeismFound = self.absenteeismRepository.getById(IdAbsenteeism)

        if not absenteeismFound:
            raise ValueError("Ausentismo no encontrado.")

        absenteeismData.nameAbsenteeism = self._normalizeText(absenteeismData.nameAbsenteeism)
        absenteeismData.codeAbsenteeism = self._normalizeText(absenteeismData.codeAbsenteeism)

        if absenteeismData.nameAbsenteeism:
            nameExists = self.absenteeismRepository.getByName(absenteeismData.nameAbsenteeism)

            if nameExists and nameExists.IdAbsenteeism != IdAbsenteeism:
                raise ValueError("Ya existe otro ausentismo con ese nombre.")

        if absenteeismData.codeAbsenteeism:
            codeExists = self.absenteeismRepository.getByCode(absenteeismData.codeAbsenteeism)

            if codeExists and codeExists.IdAbsenteeism != IdAbsenteeism:
                raise ValueError("Ya existe otro ausentismo con ese código.")

        absenteeismUpdated = self.absenteeismRepository.update(IdAbsenteeism, absenteeismData)

        if not absenteeismUpdated:
            raise ValueError("Ausentismo no encontrado.")

        return absenteeismUpdated

    def delete(self, IdAbsenteeism: int) -> bool:
        absenteeismFound = self.absenteeismRepository.getById(IdAbsenteeism)

        if not absenteeismFound:
            raise ValueError("Ausentismo no encontrado.")

        return self.absenteeismRepository.delete(IdAbsenteeism)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
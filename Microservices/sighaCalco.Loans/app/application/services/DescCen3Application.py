from app.application.interfaces.IDescCen3Application import IDescCen3Application
from app.domain.interfaces.IDescCen3Repository import IDescCen3Repository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen3 import DescCen3
from typing import Optional

class DescCen3Application(IDescCen3Application):

    def __init__(self, descCen3Repository: IDescCen3Repository):
        self.descCen3Repository = descCen3Repository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen3]:
        return self.descCen3Repository.getAll(pagination)

    def getById(self, IdDescCen3: int) -> DescCen3:
        DescCen3Found = self.descCen3Repository.getById(IdDescCen3)

        if not DescCen3Found:
            raise ValueError("DescCen3 no encontrado.")

        return DescCen3Found

    def create(self, descCen3Data: DescCen3) -> DescCen3:
        descCen3Data.nameDescCen3 = self._normalizeText(descCen3Data.nameDescCen3)
        descCen3Data.codeDescCen3 = self._normalizeText(descCen3Data.codeDescCen3)

        if descCen3Data.nameDescCen3:
            nameExists = self.descCen3Repository.getByName(descCen3Data.nameDescCen3)

            if nameExists:
                raise ValueError("Ya existe un DescCen3 con ese nombre.")

        if descCen3Data.codeDescCen3:
            codeExists = self.descCen3Repository.getByCode(descCen3Data.codeDescCen3)

            if codeExists:
                raise ValueError("Ya existe un DescCen3 con ese código.")

        return self.descCen3Repository.create(descCen3Data)

    def update(self, IdDescCen3: int, descCen3Data: DescCen3) -> DescCen3:
        DescCen3Found = self.descCen3Repository.getById(IdDescCen3)

        if not DescCen3Found:
            raise ValueError("DescCen3 no encontrado.")

        descCen3Data.nameDescCen3 = self._normalizeText(descCen3Data.nameDescCen3)
        descCen3Data.codeDescCen3 = self._normalizeText(descCen3Data.codeDescCen3)

        if descCen3Data.nameDescCen3:
            nameExists = self.descCen3Repository.getByName(descCen3Data.nameDescCen3)

            if nameExists and nameExists.IdDescCen3 != IdDescCen3:
                raise ValueError("Ya existe otro DescCen3 con ese nombre.")

        if descCen3Data.codeDescCen3:
            codeExists = self.descCen3Repository.getByCode(descCen3Data.codeDescCen3)

            if codeExists and codeExists.IdDescCen3 != IdDescCen3:
                raise ValueError("Ya existe otro DescCen3 con ese código.")

        DescCen3Updated = self.descCen3Repository.update(IdDescCen3, descCen3Data)

        if not DescCen3Updated:
            raise ValueError("DescCen3 no encontrado.")

        return DescCen3Updated

    def delete(self, IdDescCen3: int) -> bool:
        DescCen3Found = self.descCen3Repository.getById(IdDescCen3)

        if not DescCen3Found:
            raise ValueError("DescCen3 no encontrado.")

        return self.descCen3Repository.delete(IdDescCen3)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
from app.application.interfaces.IDescCen2Application import IDescCen2Application
from app.domain.interfaces.IDescCen2Repository import IDescCen2Repository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen2 import DescCen2
from typing import Optional

class DescCen2Application(IDescCen2Application):

    def __init__(self, descCen2Repository: IDescCen2Repository):
        self.descCen2Repository = descCen2Repository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen2]:
        return self.descCen2Repository.getAll(pagination)

    def getById(self, IdDescCen2: int) -> DescCen2:
        DescCen2Found = self.descCen2Repository.getById(IdDescCen2)

        if not DescCen2Found:
            raise ValueError("DescCen2 no encontrado.")

        return DescCen2Found

    def create(self, descCen2Data: DescCen2) -> DescCen2:
        descCen2Data.nameDescCen2 = self._normalizeText(descCen2Data.nameDescCen2)
        descCen2Data.codeDescCen2 = self._normalizeText(descCen2Data.codeDescCen2)

        if descCen2Data.nameDescCen2:
            nameExists = self.descCen2Repository.getByName(descCen2Data.nameDescCen2)

            if nameExists:
                raise ValueError("Ya existe un DescCen2 con ese nombre.")

        if descCen2Data.codeDescCen2:
            codeExists = self.descCen2Repository.getByCode(descCen2Data.codeDescCen2)

            if codeExists:
                raise ValueError("Ya existe un DescCen2 con ese código.")

        return self.descCen2Repository.create(descCen2Data)

    def update(self, IdDescCen2: int, descCen2Data: DescCen2) -> DescCen2:
        DescCen2Found = self.descCen2Repository.getById(IdDescCen2)

        if not DescCen2Found:
            raise ValueError("DescCen2 no encontrado.")

        descCen2Data.nameDescCen2 = self._normalizeText(descCen2Data.nameDescCen2)
        descCen2Data.codeDescCen2 = self._normalizeText(descCen2Data.codeDescCen2)

        if descCen2Data.nameDescCen2:
            nameExists = self.descCen2Repository.getByName(descCen2Data.nameDescCen2)

            if nameExists and nameExists.IdDescCen2 != IdDescCen2:
                raise ValueError("Ya existe otro DescCen2 con ese nombre.")

        if descCen2Data.codeDescCen2:
            codeExists = self.descCen2Repository.getByCode(descCen2Data.codeDescCen2)

            if codeExists and codeExists.IdDescCen2 != IdDescCen2:
                raise ValueError("Ya existe otro DescCen2 con ese código.")

        DescCen2Updated = self.descCen2Repository.update(IdDescCen2, descCen2Data)

        if not DescCen2Updated:
            raise ValueError("DescCen2 no encontrado.")

        return DescCen2Updated

    def delete(self, IdDescCen2: int) -> bool:
        DescCen2Found = self.descCen2Repository.getById(IdDescCen2)

        if not DescCen2Found:
            raise ValueError("DescCen2 no encontrado.")

        return self.descCen2Repository.delete(IdDescCen2)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
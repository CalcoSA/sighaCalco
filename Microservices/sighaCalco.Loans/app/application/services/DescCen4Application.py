from app.application.interfaces.IDescCen4Application import IDescCen4Application
from app.domain.interfaces.IDescCen4Repository import IDescCen4Repository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen4 import DescCen4
from typing import Optional

class DescCen4Application(IDescCen4Application):

    def __init__(self, descCen4Repository: IDescCen4Repository):
        self.descCen4Repository = descCen4Repository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen4]:
        return self.descCen4Repository.getAll(pagination)

    def getById(self, IdDescCen4: int) -> DescCen4:
        DescCen4Found = self.descCen4Repository.getById(IdDescCen4)

        if not DescCen4Found:
            raise ValueError("DescCen4 no encontrado.")

        return DescCen4Found

    def create(self, descCen4Data: DescCen4) -> DescCen4:
        descCen4Data.nameDescCen4 = self._normalizeText(descCen4Data.nameDescCen4)
        descCen4Data.codeDescCen4 = self._normalizeText(descCen4Data.codeDescCen4)

        if descCen4Data.nameDescCen4:
            nameExists = self.descCen4Repository.getByName(descCen4Data.nameDescCen4)

            if nameExists:
                raise ValueError("Ya existe un DescCen4 con ese nombre.")

        if descCen4Data.codeDescCen4:
            codeExists = self.descCen4Repository.getByCode(descCen4Data.codeDescCen4)

            if codeExists:
                raise ValueError("Ya existe un DescCen4 con ese código.")

        return self.descCen4Repository.create(descCen4Data)

    def update(self, IdDescCen4: int, descCen4Data: DescCen4) -> DescCen4:
        DescCen4Found = self.descCen4Repository.getById(IdDescCen4)

        if not DescCen4Found:
            raise ValueError("DescCen4 no encontrado.")

        descCen4Data.nameDescCen4 = self._normalizeText(descCen4Data.nameDescCen4)
        descCen4Data.codeDescCen4 = self._normalizeText(descCen4Data.codeDescCen4)

        if descCen4Data.nameDescCen4:
            nameExists = self.descCen4Repository.getByName(descCen4Data.nameDescCen4)

            if nameExists and nameExists.IdDescCen4 != IdDescCen4:
                raise ValueError("Ya existe otro DescCen4 con ese nombre.")

        if descCen4Data.codeDescCen4:
            codeExists = self.descCen4Repository.getByCode(descCen4Data.codeDescCen4)

            if codeExists and codeExists.IdDescCen4 != IdDescCen4:
                raise ValueError("Ya existe otro DescCen4 con ese código.")

        DescCen4Updated = self.descCen4Repository.update(IdDescCen4, descCen4Data)

        if not DescCen4Updated:
            raise ValueError("DescCen4 no encontrado.")

        return DescCen4Updated

    def delete(self, IdDescCen4: int) -> bool:
        DescCen4Found = self.descCen4Repository.getById(IdDescCen4)

        if not DescCen4Found:
            raise ValueError("DescCen4 no encontrado.")

        return self.descCen4Repository.delete(IdDescCen4)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
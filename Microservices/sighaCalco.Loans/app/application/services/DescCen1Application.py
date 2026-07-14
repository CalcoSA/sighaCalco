from app.application.interfaces.IDescCen1Application import IDescCen1Application
from app.domain.interfaces.IDescCen1Repository import IDescCen1Repository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descCen1 import DescCen1
from typing import Optional

class DescCen1Application(IDescCen1Application):

    def __init__(self, descCen1Repository: IDescCen1Repository):
        self.descCen1Repository = descCen1Repository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen1]:
        return self.descCen1Repository.getAll(pagination)

    def getById(self, IdDescCen1: int) -> DescCen1:
        DescCen1Found = self.descCen1Repository.getById(IdDescCen1)

        if not DescCen1Found:
            raise ValueError("DescCen1 no encontrado.")

        return DescCen1Found

    def create(self, descCen1Data: DescCen1) -> DescCen1:
        descCen1Data.nameDescCen1 = self._normalizeText(descCen1Data.nameDescCen1)
        descCen1Data.codeDescCen1 = self._normalizeText(descCen1Data.codeDescCen1)

        if descCen1Data.nameDescCen1:
            nameExists = self.descCen1Repository.getByName(descCen1Data.nameDescCen1)

            if nameExists:
                raise ValueError("Ya existe un DescCen1 con ese nombre.")

        if descCen1Data.codeDescCen1:
            codeExists = self.descCen1Repository.getByCode(descCen1Data.codeDescCen1)

            if codeExists:
                raise ValueError("Ya existe un DescCen1 con ese código.")

        return self.descCen1Repository.create(descCen1Data)

    def update(self, IdDescCen1: int, descCen1Data: DescCen1) -> DescCen1:
        DescCen1Found = self.descCen1Repository.getById(IdDescCen1)

        if not DescCen1Found:
            raise ValueError("DescCen1 no encontrado.")

        descCen1Data.nameDescCen1 = self._normalizeText(descCen1Data.nameDescCen1)
        descCen1Data.codeDescCen1 = self._normalizeText(descCen1Data.codeDescCen1)

        if descCen1Data.nameDescCen1:
            nameExists = self.descCen1Repository.getByName(descCen1Data.nameDescCen1)

            if nameExists and nameExists.IdDescCen1 != IdDescCen1:
                raise ValueError("Ya existe otro DescCen1 con ese nombre.")

        if descCen1Data.codeDescCen1:
            codeExists = self.descCen1Repository.getByCode(descCen1Data.codeDescCen1)

            if codeExists and codeExists.IdDescCen1 != IdDescCen1:
                raise ValueError("Ya existe otro DescCen1 con ese código.")

        DescCen1Updated = self.descCen1Repository.update(IdDescCen1, descCen1Data)

        if not DescCen1Updated:
            raise ValueError("DescCen1 no encontrado.")

        return DescCen1Updated

    def delete(self, IdDescCen1: int) -> bool:
        DescCen1Found = self.descCen1Repository.getById(IdDescCen1)

        if not DescCen1Found:
            raise ValueError("DescCen1 no encontrado.")

        return self.descCen1Repository.delete(IdDescCen1)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
from app.application.interfaces.IDescTsueldoApplication import IDescTsueldoApplication
from app.domain.interfaces.IDescTsueldoRepository import IDescTsueldoRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.descTsueldo import DescTsueldo
from typing import Optional

class DescTsueldoApplication(IDescTsueldoApplication):

    def __init__(self, descTsueldoRepository: IDescTsueldoRepository):
        self.descTsueldoRepository = descTsueldoRepository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescTsueldo]:
        return self.descTsueldoRepository.getAll(pagination)

    def getById(self, IdDescTsueldo: int) -> DescTsueldo:
        DescTsueldoFound = self.descTsueldoRepository.getById(IdDescTsueldo)

        if not DescTsueldoFound:
            raise ValueError("DescTsueldo no encontrado.")

        return DescTsueldoFound

    def create(self, descTsueldoData: DescTsueldo) -> DescTsueldo:
        descTsueldoData.nameDescTsueldo = self._normalizeText(descTsueldoData.nameDescTsueldo)
        descTsueldoData.codeDescTsueldo = self._normalizeText(descTsueldoData.codeDescTsueldo)

        if descTsueldoData.nameDescTsueldo:
            nameExists = self.descTsueldoRepository.getByName(descTsueldoData.nameDescTsueldo)

            if nameExists:
                raise ValueError("Ya existe un DescTsueldo con ese nombre.")

        if descTsueldoData.codeDescTsueldo:
            codeExists = self.descTsueldoRepository.getByCode(descTsueldoData.codeDescTsueldo)

            if codeExists:
                raise ValueError("Ya existe un DescTsueldo con ese código.")

        return self.descTsueldoRepository.create(descTsueldoData)

    def update(self, IdDescTsueldo: int, descTsueldoData: DescTsueldo) -> DescTsueldo:
        DescTsueldoFound = self.descTsueldoRepository.getById(IdDescTsueldo)

        if not DescTsueldoFound:
            raise ValueError("DescTsueldo no encontrado.")

        descTsueldoData.nameDescTsueldo = self._normalizeText(descTsueldoData.nameDescTsueldo)
        descTsueldoData.codeDescTsueldo = self._normalizeText(descTsueldoData.codeDescTsueldo)

        if descTsueldoData.nameDescTsueldo:
            nameExists = self.descTsueldoRepository.getByName(descTsueldoData.nameDescTsueldo)

            if nameExists and nameExists.IdDescTsueldo != IdDescTsueldo:
                raise ValueError("Ya existe otro DescTsueldo con ese nombre.")

        if descTsueldoData.codeDescTsueldo:
            codeExists = self.descTsueldoRepository.getByCode(descTsueldoData.codeDescTsueldo)

            if codeExists and codeExists.IdDescTsueldo != IdDescTsueldo:
                raise ValueError("Ya existe otro DescTsueldo con ese código.")

        DescTsueldoUpdated = self.descTsueldoRepository.update(IdDescTsueldo, descTsueldoData)

        if not DescTsueldoUpdated:
            raise ValueError("DescTsueldo no encontrado.")

        return DescTsueldoUpdated

    def delete(self, IdDescTsueldo: int) -> bool:
        DescTsueldoFound = self.descTsueldoRepository.getById(IdDescTsueldo)

        if not DescTsueldoFound:
            raise ValueError("DescTsueldo no encontrado.")

        return self.descTsueldoRepository.delete(IdDescTsueldo)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
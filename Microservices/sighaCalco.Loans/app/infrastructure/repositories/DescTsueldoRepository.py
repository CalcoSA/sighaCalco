from app.domain.interfaces.IDescTsueldoRepository import IDescTsueldoRepository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.descTsueldo import DescTsueldo
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class DescTsueldoRepository(IDescTsueldoRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescTsueldo]:
        query = self.db.query(DescTsueldo)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    DescTsueldo.codeDescTsueldo.like(searchValue),
                    DescTsueldo.nameDescTsueldo.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(DescTsueldo.IdDescTsueldo.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdDescTsueldo: int) -> Optional[DescTsueldo]:
        return (self.db.query(DescTsueldo).filter(DescTsueldo.IdDescTsueldo == IdDescTsueldo).first())
    
    def getByName(self, nameDescTsueldo: str) -> Optional[DescTsueldo]:
        return (self.db.query(DescTsueldo).filter(DescTsueldo.nameDescTsueldo == nameDescTsueldo.strip()).first())

    def getByCode(self, codeDescTsueldo: str) -> Optional[DescTsueldo]:
        return (self.db.query(DescTsueldo).filter(DescTsueldo.codeDescTsueldo == codeDescTsueldo.strip()).first())

    def create(self, descTsueldoData: DescTsueldo) -> DescTsueldo:
        try:
            self.db.add(descTsueldoData)
            self.db.commit()
            self.db.refresh(descTsueldoData)
            return descTsueldoData
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdDescTsueldo: int, descTsueldoData: DescTsueldo) -> Optional[DescTsueldo]:
        try:
            descTsueldoFound = self.getById(IdDescTsueldo)

            if not descTsueldoFound:
                return None

            descTsueldoFound.nameDescTsueldo = descTsueldoData.nameDescTsueldo
            descTsueldoFound.codeDescTsueldo = descTsueldoData.codeDescTsueldo

            self.db.commit()
            self.db.refresh(descTsueldoFound)

            return descTsueldoFound
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdDescTsueldo: int) -> bool:
        try:
            descTsueldoFound = self.getById(IdDescTsueldo)

            if not descTsueldoFound:
                return False

            self.db.delete(descTsueldoFound)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
from app.domain.interfaces.IDescCen3Repository import IDescCen3Repository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.descCen3 import DescCen3
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class DescCen3Repository(IDescCen3Repository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen3]:
        query = self.db.query(DescCen3)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    DescCen3.codeDescCen3.like(searchValue),
                    DescCen3.nameDescCen3.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(DescCen3.IdDescCen3.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdDescCen3: int) -> Optional[DescCen3]:
        return (self.db.query(DescCen3).filter(DescCen3.IdDescCen3 == IdDescCen3).first())
    
    def getByName(self, nameDescCen3: str) -> Optional[DescCen3]:
        return (self.db.query(DescCen3).filter(DescCen3.nameDescCen3 == nameDescCen3.strip()).first())

    def getByCode(self, codeDescCen3: str) -> Optional[DescCen3]:
        return (self.db.query(DescCen3).filter(DescCen3.codeDescCen3 == codeDescCen3.strip()).first())

    def create(self, descCen3Data: DescCen3) -> DescCen3:
        try:
            self.db.add(descCen3Data)
            self.db.commit()
            self.db.refresh(descCen3Data)
            return descCen3Data
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdDescCen3: int, descCen3Data: DescCen3) -> Optional[DescCen3]:
        try:
            descCen3Found = self.getById(IdDescCen3)

            if not descCen3Found:
                return None

            descCen3Found.nameDescCen3 = descCen3Data.nameDescCen3
            descCen3Found.codeDescCen3 = descCen3Data.codeDescCen3

            self.db.commit()
            self.db.refresh(descCen3Found)

            return descCen3Found
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdDescCen3: int) -> bool:
        try:
            descCen3Found = self.getById(IdDescCen3)

            if not descCen3Found:
                return False

            self.db.delete(descCen3Found)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
from app.domain.interfaces.IDescCen2Repository import IDescCen2Repository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.descCen2 import DescCen2
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class DescCen2Repository(IDescCen2Repository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen2]:
        query = self.db.query(DescCen2)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    DescCen2.codeDescCen2.like(searchValue),
                    DescCen2.nameDescCen2.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(DescCen2.IdDescCen2.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdDescCen2: int) -> Optional[DescCen2]:
        return (self.db.query(DescCen2).filter(DescCen2.IdDescCen2 == IdDescCen2).first())
    
    def getByName(self, nameDescCen2: str) -> Optional[DescCen2]:
        return (self.db.query(DescCen2).filter(DescCen2.nameDescCen2 == nameDescCen2.strip()).first())

    def getByCode(self, codeDescCen2: str) -> Optional[DescCen2]:
        return (self.db.query(DescCen2).filter(DescCen2.codeDescCen2 == codeDescCen2.strip()).first())

    def create(self, descCen2Data: DescCen2) -> DescCen2:
        try:
            self.db.add(descCen2Data)
            self.db.commit()
            self.db.refresh(descCen2Data)
            return descCen2Data
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdDescCen2: int, descCen2Data: DescCen2) -> Optional[DescCen2]:
        try:
            descCen2Found = self.getById(IdDescCen2)

            if not descCen2Found:
                return None

            descCen2Found.nameDescCen2 = descCen2Data.nameDescCen2
            descCen2Found.codeDescCen2 = descCen2Data.codeDescCen2

            self.db.commit()
            self.db.refresh(descCen2Found)

            return descCen2Found
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdDescCen2: int) -> bool:
        try:
            descCen2Found = self.getById(IdDescCen2)

            if not descCen2Found:
                return False

            self.db.delete(descCen2Found)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
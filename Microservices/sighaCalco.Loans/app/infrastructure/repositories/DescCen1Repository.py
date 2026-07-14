from app.domain.interfaces.IDescCen1Repository import IDescCen1Repository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.descCen1 import DescCen1
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class DescCen1Repository(IDescCen1Repository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen1]:
        query = self.db.query(DescCen1)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    DescCen1.codeDescCen1.like(searchValue),
                    DescCen1.nameDescCen1.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(DescCen1.IdDescCen1.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdDescCen1: int) -> Optional[DescCen1]:
        return (self.db.query(DescCen1).filter(DescCen1.IdDescCen1 == IdDescCen1).first())
    
    def getByName(self, nameDescCen1: str) -> Optional[DescCen1]:
        return (self.db.query(DescCen1).filter(DescCen1.nameDescCen1 == nameDescCen1.strip()).first())

    def getByCode(self, codeDescCen1: str) -> Optional[DescCen1]:
        return (self.db.query(DescCen1).filter(DescCen1.codeDescCen1 == codeDescCen1.strip()).first())

    def create(self, descCen1Data: DescCen1) -> DescCen1:
        try:
            self.db.add(descCen1Data)
            self.db.commit()
            self.db.refresh(descCen1Data)
            return descCen1Data
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdDescCen1: int, descCen1Data: DescCen1) -> Optional[DescCen1]:
        try:
            descCen1Found = self.getById(IdDescCen1)

            if not descCen1Found:
                return None

            descCen1Found.nameDescCen1 = descCen1Data.nameDescCen1
            descCen1Found.codeDescCen1 = descCen1Data.codeDescCen1

            self.db.commit()
            self.db.refresh(descCen1Found)

            return descCen1Found
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdDescCen1: int) -> bool:
        try:
            descCen1Found = self.getById(IdDescCen1)

            if not descCen1Found:
                return False

            self.db.delete(descCen1Found)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
from app.domain.interfaces.IDescCen4Repository import IDescCen4Repository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.descCen4 import DescCen4
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class DescCen4Repository(IDescCen4Repository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[DescCen4]:
        query = self.db.query(DescCen4)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    DescCen4.codeDescCen4.like(searchValue),
                    DescCen4.nameDescCen4.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(DescCen4.IdDescCen4.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdDescCen4: int) -> Optional[DescCen4]:
        return (self.db.query(DescCen4).filter(DescCen4.IdDescCen4 == IdDescCen4).first())
    
    def getByName(self, nameDescCen4: str) -> Optional[DescCen4]:
        return (self.db.query(DescCen4).filter(DescCen4.nameDescCen4 == nameDescCen4.strip()).first())

    def getByCode(self, codeDescCen4: str) -> Optional[DescCen4]:
        return (self.db.query(DescCen4).filter(DescCen4.codeDescCen4 == codeDescCen4.strip()).first())

    def create(self, descCen4Data: DescCen4) -> DescCen4:
        try:
            self.db.add(descCen4Data)
            self.db.commit()
            self.db.refresh(descCen4Data)
            return descCen4Data
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdDescCen4: int, descCen4Data: DescCen4) -> Optional[DescCen4]:
        try:
            descCen4Found = self.getById(IdDescCen4)

            if not descCen4Found:
                return None

            descCen4Found.nameDescCen4 = descCen4Data.nameDescCen4
            descCen4Found.codeDescCen4 = descCen4Data.codeDescCen4

            self.db.commit()
            self.db.refresh(descCen4Found)

            return descCen4Found
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdDescCen4: int) -> bool:
        try:
            descCen4Found = self.getById(IdDescCen4)

            if not descCen4Found:
                return False

            self.db.delete(descCen4Found)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
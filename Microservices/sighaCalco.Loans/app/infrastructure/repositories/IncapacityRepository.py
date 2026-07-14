from app.domain.interfaces.IIncapacityRepository import IIncapacityRepository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.incapacity import Incapacity
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class IncapacityRepository(IIncapacityRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Incapacity]:
        query = self.db.query(Incapacity)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    Incapacity.codeIncapacity.like(searchValue),
                    Incapacity.nameIncapacity.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(Incapacity.IdIncapacity.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdIncapacity: int) -> Optional[Incapacity]:
        return (self.db.query(Incapacity).filter(Incapacity.IdIncapacity == IdIncapacity).first())
    
    def getByName(self, nameIncapacity: str) -> Optional[Incapacity]:
        return (self.db.query(Incapacity).filter(Incapacity.nameIncapacity == nameIncapacity.strip()).first())

    def getByCode(self, codeIncapacity: str) -> Optional[Incapacity]:
        return (self.db.query(Incapacity).filter(Incapacity.codeIncapacity == codeIncapacity.strip()).first())

    def create(self, incapacityData: Incapacity) -> Incapacity:
        try:
            self.db.add(incapacityData)
            self.db.commit()
            self.db.refresh(incapacityData)
            return incapacityData
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdIncapacity: int, incapacityData: Incapacity) -> Optional[Incapacity]:
        try:
            incapacityFound = self.getById(IdIncapacity)

            if not incapacityFound:
                return None

            incapacityFound.nameIncapacity = incapacityData.nameIncapacity
            incapacityFound.codeIncapacity = incapacityData.codeIncapacity

            self.db.commit()
            self.db.refresh(incapacityFound)

            return incapacityFound
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdIncapacity: int) -> bool:
        try:
            incapacityFound = self.getById(IdIncapacity)

            if not incapacityFound:
                return False

            self.db.delete(incapacityFound)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
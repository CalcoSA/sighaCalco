from app.domain.interfaces.IAbsenteeismRepository import IAbsenteeismRepository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.absenteeism import Absenteeism
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class AbsenteeismRepository(IAbsenteeismRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Absenteeism]:
        query = self.db.query(Absenteeism)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    Absenteeism.codeAbsenteeism.like(searchValue),
                    Absenteeism.nameAbsenteeism.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(Absenteeism.IdAbsenteeism.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdAbsenteeism: int) -> Optional[Absenteeism]:
        return (self.db.query(Absenteeism).filter(Absenteeism.IdAbsenteeism == IdAbsenteeism).first())
    
    def getByName(self, nameAbsenteeism: str) -> Optional[Absenteeism]:
        return (self.db.query(Absenteeism).filter(Absenteeism.nameAbsenteeism == nameAbsenteeism.strip()).first())

    def getByCode(self, codeAbsenteeism: str) -> Optional[Absenteeism]:
        return (self.db.query(Absenteeism).filter(Absenteeism.codeAbsenteeism == codeAbsenteeism.strip()).first())

    def create(self, absenteeismData: Absenteeism) -> Absenteeism:
        try:
            self.db.add(absenteeismData)
            self.db.commit()
            self.db.refresh(absenteeismData)
            return absenteeismData
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdAbsenteeism: int, absenteeismData: Absenteeism) -> Optional[Absenteeism]:
        try:
            absenteeismFound = self.getById(IdAbsenteeism)

            if not absenteeismFound:
                return None

            absenteeismFound.nameAbsenteeism = absenteeismData.nameAbsenteeism
            absenteeismFound.codeAbsenteeism = absenteeismData.codeAbsenteeism

            self.db.commit()
            self.db.refresh(absenteeismFound)

            return absenteeismFound
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdAbsenteeism: int) -> bool:
        try:
            absenteeismFound = self.getById(IdAbsenteeism)

            if not absenteeismFound:
                return False

            self.db.delete(absenteeismFound)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
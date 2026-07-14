from app.domain.interfaces.ITypeWithdrawalRepository import ITypeWithdrawalRepository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.typeWithdrawal import TypeWithdrawal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class TypeWithdrawalRepository(ITypeWithdrawalRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[TypeWithdrawal]:
        query = self.db.query(TypeWithdrawal)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    TypeWithdrawal.codeTypeWithdrawal.like(searchValue),
                    TypeWithdrawal.nameTypeWithdrawal.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(TypeWithdrawal.IdTypeWithdrawal.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdTypeWithdrawal: int) -> Optional[TypeWithdrawal]:
        return (self.db.query(TypeWithdrawal).filter(TypeWithdrawal.IdTypeWithdrawal == IdTypeWithdrawal).first())
    
    def getByName(self, nameTypeWithdrawal: str) -> Optional[TypeWithdrawal]:
        return (self.db.query(TypeWithdrawal).filter(TypeWithdrawal.nameTypeWithdrawal == nameTypeWithdrawal.strip()).first())

    def getByCode(self, codeTypeWithdrawal: str) -> Optional[TypeWithdrawal]:
        return (self.db.query(TypeWithdrawal).filter(TypeWithdrawal.codeTypeWithdrawal == codeTypeWithdrawal.strip()).first())

    def create(self, typeWithdrawalData: TypeWithdrawal) -> TypeWithdrawal:
        try:
            self.db.add(typeWithdrawalData)
            self.db.commit()
            self.db.refresh(typeWithdrawalData)
            return typeWithdrawalData
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdTypeWithdrawal: int, typeWithdrawalData: TypeWithdrawal) -> Optional[TypeWithdrawal]:
        try:
            typeWithdrawalFound = self.getById(IdTypeWithdrawal)

            if not typeWithdrawalFound:
                return None

            typeWithdrawalFound.nameTypeWithdrawal = typeWithdrawalData.nameTypeWithdrawal
            typeWithdrawalFound.codeTypeWithdrawal = typeWithdrawalData.codeTypeWithdrawal

            self.db.commit()
            self.db.refresh(typeWithdrawalFound)

            return typeWithdrawalFound
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdTypeWithdrawal: int) -> bool:
        try:
            typeWithdrawalFound = self.getById(IdTypeWithdrawal)

            if not typeWithdrawalFound:
                return False

            self.db.delete(typeWithdrawalFound)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
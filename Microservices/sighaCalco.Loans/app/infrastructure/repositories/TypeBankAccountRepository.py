from app.domain.interfaces.ITypeBankAccountRepository import ITypeBankAccountRepository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.typeBankAccount import TypeBankAccount
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class TypeBankAccountRepository(ITypeBankAccountRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[TypeBankAccount]:
        query = self.db.query(TypeBankAccount)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    TypeBankAccount.codeTypeBankAccount.like(searchValue),
                    TypeBankAccount.nameTypeBankAccount.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(TypeBankAccount.IdTypeBankAccount.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdTypeBankAccount: int) -> Optional[TypeBankAccount]:
        return (self.db.query(TypeBankAccount).filter(TypeBankAccount.IdTypeBankAccount == IdTypeBankAccount).first())
    
    def getByName(self, nameTypeBankAccount: str) -> Optional[TypeBankAccount]:
        return (self.db.query(TypeBankAccount).filter(TypeBankAccount.nameTypeBankAccount == nameTypeBankAccount.strip()).first())

    def getByCode(self, codeTypeBankAccount: str) -> Optional[TypeBankAccount]:
        return (self.db.query(TypeBankAccount).filter(TypeBankAccount.codeTypeBankAccount == codeTypeBankAccount.strip()).first())

    def create(self, typeBankAccountData: TypeBankAccount) -> TypeBankAccount:
        try:
            self.db.add(typeBankAccountData)
            self.db.commit()
            self.db.refresh(typeBankAccountData)
            return typeBankAccountData
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdTypeBankAccount: int, typeBankAccountData: TypeBankAccount) -> Optional[TypeBankAccount]:
        try:
            typeBankAccountFound = self.getById(IdTypeBankAccount)

            if not typeBankAccountFound:
                return None

            typeBankAccountFound.nameTypeBankAccount = typeBankAccountData.nameTypeBankAccount
            typeBankAccountFound.codeTypeBankAccount = typeBankAccountData.codeTypeBankAccount

            self.db.commit()
            self.db.refresh(typeBankAccountFound)

            return typeBankAccountFound
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdTypeBankAccount: int) -> bool:
        try:
            typeBankAccountFound = self.getById(IdTypeBankAccount)

            if not typeBankAccountFound:
                return False

            self.db.delete(typeBankAccountFound)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
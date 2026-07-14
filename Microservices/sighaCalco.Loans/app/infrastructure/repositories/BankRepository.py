from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.interfaces.IBankRepository import IBankRepository
from sqlalchemy.exc import SQLAlchemyError
from app.domain.entities.bank import Bank
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_
from math import ceil

class BankRepository(IBankRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Bank]:
        query = self.db.query(Bank)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    Bank.codeBank.like(searchValue),
                    Bank.nameBank.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(Bank.IdBank.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdBank: int) -> Optional[Bank]:
        return (self.db.query(Bank).filter(Bank.IdBank == IdBank).first())
    
    def getByName(self, nameBank: str) -> Optional[Bank]:
        return (self.db.query(Bank).filter(Bank.nameBank == nameBank.strip()).first())

    def getByCode(self, codeBank: str) -> Optional[Bank]:
        return (self.db.query(Bank).filter(Bank.codeBank == codeBank.strip()).first())

    def create(self, bankData: Bank) -> Bank:
        try:
            self.db.add(bankData)
            self.db.commit()
            self.db.refresh(bankData)
            return bankData
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdBank: int, bankData: Bank) -> Optional[Bank]:
        try:
            bankFound = self.getById(IdBank)

            if not bankFound:
                return None

            bankFound.nameBank = bankData.nameBank
            bankFound.codeBank = bankData.codeBank

            self.db.commit()
            self.db.refresh(bankFound)

            return bankFound
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdBank: int) -> bool:
        try:
            bankFound = self.getById(IdBank)

            if not bankFound:
                return False

            self.db.delete(bankFound)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
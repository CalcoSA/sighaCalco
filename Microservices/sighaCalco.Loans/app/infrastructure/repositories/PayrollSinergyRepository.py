from app.domain.interfaces.IPayrollSinergyRepository import IPayrollSinergyRepository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.payrollSinergy import PayrollSinergy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import or_
from math import ceil

class PayrollSinergyRepository(IPayrollSinergyRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[PayrollSinergy]:
        query = self.db.query(PayrollSinergy)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(                    
                    PayrollSinergy.codePayrollSinergy.like(searchValue),
                    PayrollSinergy.namePayrollSinergy.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(PayrollSinergy.IdPayrollSinergy.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)
    
    def getAllPayroll(self, search: Optional[str] = None) -> List[PayrollSinergy]:
        query = self.db.query(PayrollSinergy)

        if search and search.strip():
            searchValue = f"%{search.strip()}%"

            query = query.filter(
                or_(
                    PayrollSinergy.codePayrollSinergy.like(searchValue),
                    PayrollSinergy.namePayrollSinergy.like(searchValue),
                )
            )

        return (query.order_by(PayrollSinergy.namePayrollSinergy.asc()).all())

    def getById(self, IdPayrollSinergy: int) -> Optional[PayrollSinergy]:
        return (self.db.query(PayrollSinergy).filter(PayrollSinergy.IdPayrollSinergy == IdPayrollSinergy).first())
    
    def getByName(self, namePayrollSinergy: str) -> Optional[PayrollSinergy]:
        return (self.db.query(PayrollSinergy).filter(PayrollSinergy.namePayrollSinergy == namePayrollSinergy.strip()).first())

    def getByCode(self, codePayrollSinergy: str) -> Optional[PayrollSinergy]:
        return (self.db.query(PayrollSinergy).filter(PayrollSinergy.codePayrollSinergy == codePayrollSinergy.strip()).first())

    def create(self, payrollSinergyData: PayrollSinergy) -> PayrollSinergy:
        try:
            self.db.add(payrollSinergyData)
            self.db.commit()
            self.db.refresh(payrollSinergyData)
            return payrollSinergyData
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdPayrollSinergy: int, payrollSinergyData: PayrollSinergy) -> Optional[PayrollSinergy]:
        try:
            payrollSinergyFound = self.getById(IdPayrollSinergy)

            if not payrollSinergyFound:
                return None

            payrollSinergyFound.namePayrollSinergy = payrollSinergyData.namePayrollSinergy
            payrollSinergyFound.codePayrollSinergy = payrollSinergyData.codePayrollSinergy

            self.db.commit()
            self.db.refresh(payrollSinergyFound)

            return payrollSinergyFound
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdPayrollSinergy: int) -> bool:
        try:
            payrollSinergyFound = self.getById(IdPayrollSinergy)

            if not payrollSinergyFound:
                return False

            self.db.delete(payrollSinergyFound)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
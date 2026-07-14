from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.interfaces.ILoanRepository import ILoanRepository
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError
from app.domain.entities.loan import Loan
from datetime import datetime, date
from zoneinfo import ZoneInfo
from typing import Optional
from math import ceil

class LoanRepository(ILoanRepository):

    def __init__(self, db: Session):
        self.db = db

    def _nowColombia(self) -> datetime:
        return datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)
    
    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, IdLoanStatus: Optional[int] = None, requestDateFrom: Optional[date] = None, requestDateTo: Optional[date] = None) -> PaginatedResult[Loan]:

        query = self.db.query(Loan).options(selectinload(Loan.loanInstallments))

        if employeeDocumentNumber and employeeDocumentNumber.strip():
            documentValue = f"%{employeeDocumentNumber.strip()}%"
            query = query.filter(Loan.employeeDocumentNumber.like(documentValue))

        if IdLoanStatus and IdLoanStatus > 0:
            query = query.filter(Loan.IdLoanStatus == IdLoanStatus)

        if requestDateFrom:
            query = query.filter(Loan.requestDate >= requestDateFrom)

        if requestDateTo:
            query = query.filter(Loan.requestDate <= requestDateTo)

        total = query.count()
        items = (query.order_by(Loan.createdAt.desc(), Loan.IdLoan.desc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def create(self, loanData: Loan) -> Loan:
        try:
            nowColombia = self._nowColombia()

            loanData.createdAt = nowColombia
            loanData.updatedAt = None

            self.db.add(loanData)
            self.db.commit()
            self.db.refresh(loanData)

            return (self.db.query(Loan).options(selectinload(Loan.loanInstallments)).filter(Loan.IdLoan == loanData.IdLoan).first())

        except ValueError:
            self.db.rollback()
            raise

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el préstamo: {str(e)}")
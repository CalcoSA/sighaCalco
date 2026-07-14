from app.domain.interfaces.ILoanLogRepository import ILoanLogRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.loanLog import LoanLog
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from math import ceil

class LoanLogRepository(ILoanLogRepository):

    def __init__(self, db: Session):
        self.db = db

    def _nowColombia(self) -> datetime:
        return datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)

    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, actionDateFrom: Optional[date] = None, actionDateTo: Optional[date] = None,) -> PaginatedResult[LoanLog]:
        query = self.db.query(LoanLog)

        if employeeDocumentNumber and employeeDocumentNumber.strip():
            documentValue = f"%{employeeDocumentNumber.strip()}%"
            query = query.filter(LoanLog.employeeDocumentNumber.like(documentValue))

        if actionDateFrom:
            startDate = datetime.combine(actionDateFrom, time.min)
            query = query.filter(LoanLog.actionDate >= startDate)

        if actionDateTo:
            endDate = datetime.combine(actionDateTo, time.max)
            query = query.filter(LoanLog.actionDate <= endDate)

        total = query.count()
        items = (query.order_by(LoanLog.actionDate.desc(), LoanLog.IdLoanLog.desc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def create(self, loanLogData: LoanLog) -> LoanLog:
        try:
            newLoanLog = LoanLog(
                actionType=loanLogData.actionType.strip(),
                IdLoan=loanLogData.IdLoan,
                IdLoanInstallment=loanLogData.IdLoanInstallment,
                installmentNumber=loanLogData.installmentNumber,
                employeeDocumentNumber=loanLogData.employeeDocumentNumber.strip() if loanLogData.employeeDocumentNumber else None,
                conceptName=loanLogData.conceptName.strip() if loanLogData.conceptName else None,
                loanStatusName=loanLogData.loanStatusName.strip() if loanLogData.loanStatusName else None,
                installmentStatusName=loanLogData.installmentStatusName.strip() if loanLogData.installmentStatusName else None,
                observation=loanLogData.observation.strip() if loanLogData.observation else None,
                actorUserName=loanLogData.actorUserName.strip() if loanLogData.actorUserName else None,
                actionDate=self._nowColombia(),
            )

            self.db.add(newLoanLog)
            self.db.commit()
            self.db.refresh(newLoanLog)

            return newLoanLog

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el log del préstamo: {str(e)}")
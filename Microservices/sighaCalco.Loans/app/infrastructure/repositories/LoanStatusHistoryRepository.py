from app.domain.interfaces.ILoanStatusHistoryRepository import ILoanStatusHistoryRepository
from app.domain.entities.loanStatusHistory import LoanStatusHistory
from sqlalchemy.orm import Session, joinedload
from app.domain.entities.loan import Loan
from datetime import datetime, date, time
from typing import List, Optional

class LoanStatusHistoryRepository(ILoanStatusHistoryRepository):

    def __init__(self, db: Session):
        self.db = db

    def getById(self, IdLoanStatusHistory: int) -> Optional[LoanStatusHistory]:
        return self.db.query(LoanStatusHistory).options(joinedload(LoanStatusHistory.loanStatus)).filter(LoanStatusHistory.IdLoanStatusHistory == IdLoanStatusHistory).first()

    def getByIdLoan(self, IdLoan: int) -> List[LoanStatusHistory]:
        return self.db.query(LoanStatusHistory).options(joinedload(LoanStatusHistory.loanStatus)).filter(LoanStatusHistory.IdLoan == IdLoan).order_by(LoanStatusHistory.createdAt.desc(), LoanStatusHistory.IdLoanStatusHistory.desc()).all()

    def getReportDeletions(self, dateFrom: date, dateTo: date,) -> List[LoanStatusHistory]:
        startDate = datetime.combine(dateFrom, time.min,)
        endDate = datetime.combine(dateTo, time.max,)

        return (
            self.db.query(LoanStatusHistory)
            .options(
                joinedload(LoanStatusHistory.loanStatus),
                joinedload(LoanStatusHistory.loan).selectinload(Loan.loanInstallments),
            )
            .filter(
                LoanStatusHistory.IdLoanStatus.in_([3, 4, 5]),
                LoanStatusHistory.createdAt >= startDate,
                LoanStatusHistory.createdAt <= endDate,
            )
            .order_by(
                LoanStatusHistory.createdAt.asc(),
                LoanStatusHistory.IdLoanStatusHistory.asc(),
            )
            .all()
        )

    def create(self, historyData: LoanStatusHistory) -> LoanStatusHistory:
        self.db.add(historyData)
        self.db.flush()
        self.db.refresh(historyData)
        return historyData
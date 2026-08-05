from app.domain.interfaces.ILoanStatusHistoryRepository import ILoanStatusHistoryRepository
from app.domain.entities.loanStatusHistory import LoanStatusHistory
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

class LoanStatusHistoryRepository(ILoanStatusHistoryRepository):

    def __init__(self, db: Session):
        self.db = db

    def getById(self, IdLoanStatusHistory: int) -> Optional[LoanStatusHistory]:
        return self.db.query(LoanStatusHistory).options(joinedload(LoanStatusHistory.loanStatus)).filter(LoanStatusHistory.IdLoanStatusHistory == IdLoanStatusHistory).first()

    def getByIdLoan(self, IdLoan: int) -> List[LoanStatusHistory]:
        return self.db.query(LoanStatusHistory).options(joinedload(LoanStatusHistory.loanStatus)).filter(LoanStatusHistory.IdLoan == IdLoan).order_by(LoanStatusHistory.createdAt.desc(), LoanStatusHistory.IdLoanStatusHistory.desc()).all()
        
    def create(self, historyData: LoanStatusHistory) -> LoanStatusHistory:
        self.db.add(historyData)
        self.db.flush()
        self.db.refresh(historyData)
        return historyData
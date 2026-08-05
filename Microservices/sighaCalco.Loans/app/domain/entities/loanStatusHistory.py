from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.connection import Base
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.domain.entities.loanStatus import LoanStatus

class LoanStatusHistory(Base):
    __tablename__ = "loan_loanStatusHistory"

    IdLoanStatusHistory: Mapped[int] = mapped_column("IdLoanStatusHistory", Integer, primary_key=True, autoincrement=True)
    IdLoan: Mapped[int] = mapped_column("IdLoan", Integer, ForeignKey("loan_loan.IdLoan", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    IdLoanStatus: Mapped[int] = mapped_column("IdLoanStatus", Integer, ForeignKey("loan_loanStatus.IdLoanStatus", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    observation: Mapped[str] = mapped_column("observation", Text, nullable=False)
    createdAt: Mapped[datetime] = mapped_column("createdAt", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    createdByUserName: Mapped[str] = mapped_column("createdByUserName", String(250), nullable=False)

    loanStatus: Mapped["LoanStatus"] = relationship("LoanStatus")
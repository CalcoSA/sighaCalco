from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class LoanStatus(Base):
    __tablename__ = "loan_loanStatus"

    IdLoanStatus: Mapped[int] = mapped_column("IdLoanStatus", Integer, primary_key=True, autoincrement=True)
    nameLoanStatus: Mapped[str] = mapped_column("nameLoanStatus", String(100), nullable=False)

    __table_args__ = (UniqueConstraint("nameLoanStatus", name="uq_loanStatus_name"),)
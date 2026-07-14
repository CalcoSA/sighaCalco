from __future__ import annotations

from sqlalchemy import DateTime, Integer, String, Text, text
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class LoanLog(Base):
    __tablename__ = "loan_LoanLog"

    IdLoanLog: Mapped[int] = mapped_column("IdLoanLog", Integer, primary_key=True, autoincrement=True)
    actionType: Mapped[str] = mapped_column("actionType", String(100), nullable=False)
    IdLoan: Mapped[int | None] = mapped_column("IdLoan", Integer, nullable=True)
    IdLoanInstallment: Mapped[int | None] = mapped_column("IdLoanInstallment", Integer, nullable=True)
    installmentNumber: Mapped[int | None] = mapped_column("installmentNumber", Integer, nullable=True)
    employeeDocumentNumber: Mapped[str | None] = mapped_column("employeeDocumentNumber", String(50), nullable=True)
    conceptName: Mapped[str | None] = mapped_column("conceptName", String(250), nullable=True)
    loanStatusName: Mapped[str | None] = mapped_column("loanStatusName", String(100), nullable=True)
    installmentStatusName: Mapped[str | None] = mapped_column("installmentStatusName", String(100), nullable=True)
    observation: Mapped[str | None] = mapped_column("observation", Text, nullable=True)
    actorUserName: Mapped[str | None] = mapped_column("actorUserName", String(250), nullable=True)
    actionDate: Mapped[datetime] = mapped_column("actionDate", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
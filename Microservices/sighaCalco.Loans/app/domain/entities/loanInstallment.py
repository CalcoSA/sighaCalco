from __future__ import annotations

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.connection import Base
from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import date

if TYPE_CHECKING:
    from app.domain.entities.loan import Loan

class LoanInstallment(Base):
    __tablename__ = "loan_loanInstallment"

    IdLoanInstallment: Mapped[int] = mapped_column("IdLoanInstallment", Integer, primary_key=True, autoincrement=True)
    IdLoan: Mapped[int] = mapped_column("IdLoan", Integer, ForeignKey("loan_loan.IdLoan", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    installmentNumber: Mapped[int] = mapped_column("installmentNumber", Integer, nullable=False)
    installmentValue: Mapped[Decimal] = mapped_column("installmentValue", Numeric(18, 2), nullable=False)
    isPaid: Mapped[bool] = mapped_column("isPaid", Boolean, nullable=False, default=False)
    commitmentDate: Mapped[date] = mapped_column("commitmentDate", Date, nullable=False)
    paymentDate: Mapped[date | None] = mapped_column("paymentDate", Date, nullable=True)

    loan: Mapped["Loan"] = relationship("Loan", back_populates="loanInstallments")

    __table_args__ = (UniqueConstraint("IdLoan", "installmentNumber", name="uq_loan_installment_number"),)
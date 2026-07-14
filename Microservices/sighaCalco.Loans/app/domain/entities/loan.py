from __future__ import annotations

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.connection import Base
from typing import TYPE_CHECKING, List
from datetime import date, datetime
from decimal import Decimal

if TYPE_CHECKING:
    from app.domain.entities.loanInstallment import LoanInstallment

class Loan(Base):
    __tablename__ = "loan_loan"

    IdLoan: Mapped[int] = mapped_column("IdLoan", Integer, primary_key=True, autoincrement=True)
    employeeDocumentNumber: Mapped[str] = mapped_column("employeeDocumentNumber", String(50), nullable=False)
    employeeFullName: Mapped[str] = mapped_column("employeeFullName", String(250), nullable=False)
    employeeRoleName: Mapped[str | None] = mapped_column("employeeRoleName", String(250), nullable=True)
    employeeCostCenterName: Mapped[str | None] = mapped_column("employeeCostCenterName", String(250), nullable=True)
    IdConcept: Mapped[int] = mapped_column("IdConcept", Integer, nullable=False)
    conceptName: Mapped[str] = mapped_column("conceptName", String(250), nullable=False)
    IdDeductionPlan: Mapped[int] = mapped_column("IdDeductionPlan", Integer, nullable=False)
    deductionPlanName: Mapped[str] = mapped_column("deductionPlanName", String(150), nullable=False)
    IdLoanStatus: Mapped[int] = mapped_column("IdLoanStatus", Integer, nullable=False)
    loanStatusName: Mapped[str] = mapped_column("loanStatusName", String(100), nullable=False)
    crossDocument: Mapped[str | None] = mapped_column("crossDocument", String(100), nullable=True)
    loanAmount: Mapped[Decimal] = mapped_column("loanAmount", Numeric(18, 2), nullable=False)
    numberInstallments: Mapped[int] = mapped_column("numberInstallments", Integer, nullable=False)
    paidInstallments: Mapped[int] = mapped_column("paidInstallments", Integer, nullable=False, default=0)
    remainingAmount: Mapped[Decimal] = mapped_column("remainingAmount", Numeric(18, 2), nullable=False)
    requestDate: Mapped[date] = mapped_column("requestDate", Date, nullable=False)
    startDiscountDate: Mapped[date] = mapped_column("startDiscountDate", Date, nullable=False)
    endDiscountDate: Mapped[date | None] = mapped_column("endDiscountDate", Date, nullable=True)
    observation: Mapped[str | None] = mapped_column("observation", Text, nullable=True)
    createdByUserName: Mapped[str] = mapped_column("createdByUserName", String(250), nullable=False)
    updatedByUserName: Mapped[str | None] = mapped_column("updatedByUserName", String(250), nullable=True)
    createdAt: Mapped[datetime] = mapped_column("createdAt", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updatedAt: Mapped[datetime | None] = mapped_column("updatedAt", DateTime, nullable=True, server_onupdate=text("CURRENT_TIMESTAMP"))

    loanInstallments: Mapped[List["LoanInstallment"]] = relationship("LoanInstallment", back_populates="loan", cascade="all, delete-orphan", order_by="LoanInstallment.installmentNumber",)
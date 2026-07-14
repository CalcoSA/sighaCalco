from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class PayrollSinergy(Base):
    __tablename__ = "loan_payrollSinergy"

    IdPayrollSinergy: Mapped[int] = mapped_column("IdPayrollSinergy", Integer, primary_key=True, autoincrement=True)
    namePayrollSinergy: Mapped[str] = mapped_column("namePayrollSinergy", String(250), nullable=True)
    codePayrollSinergy: Mapped[str] = mapped_column("codePayrollSinergy", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("namePayrollSinergy", name="uq_payrollSinergy_name"), UniqueConstraint("codePayrollSinergy", name="uq_payrollSinergy_code"),)
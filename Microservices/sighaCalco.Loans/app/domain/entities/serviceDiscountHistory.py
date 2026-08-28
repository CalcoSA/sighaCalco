from __future__ import annotations

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, text
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from decimal import Decimal

class ServiceDiscountHistory(Base):
    __tablename__ = "loan_serviceDiscountHistory"

    IdServiceDiscountHistory: Mapped[int] = mapped_column("IdServiceDiscountHistory", Integer, primary_key=True, autoincrement=True)
    IdLoan: Mapped[int] = mapped_column("IdLoan", Integer, ForeignKey("loan_loan.IdLoan", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    discountValue: Mapped[Decimal] = mapped_column("discountValue", Numeric(18, 2), nullable=False)
    discountDate: Mapped[date] = mapped_column("discountDate", Date, nullable=False)
    createdAt: Mapped[datetime] = mapped_column("createdAt", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    createdByUserName: Mapped[str] = mapped_column("createdByUserName", String(250), nullable=False)

    __table_args__ = (UniqueConstraint("IdLoan", "discountDate", name="uq_serviceDiscountHistory_loan_date"),)
from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class DeductionPlan(Base):
    __tablename__ = "loan_deductionPlan"

    IdDeductionPlan: Mapped[int] = mapped_column("IdDeductionPlan", Integer, primary_key=True, autoincrement=True)
    nameDeductionPlan: Mapped[str] = mapped_column("nameDeductionPlan", String(150), nullable=False)
    firstFortnight: Mapped[bool] = mapped_column("firstFortnight", Boolean, nullable=False, default=False)
    secondFortnight: Mapped[bool] = mapped_column("secondFortnight", Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint("nameDeductionPlan", name="uq_deductionPlan_name"),)
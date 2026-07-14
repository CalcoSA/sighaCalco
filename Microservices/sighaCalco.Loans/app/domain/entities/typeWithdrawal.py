from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class TypeWithdrawal(Base):
    __tablename__ = "loan_typeWithdrawal"

    IdTypeWithdrawal: Mapped[int] = mapped_column("IdTypeWithdrawal", Integer, primary_key=True, autoincrement=True)
    nameTypeWithdrawal: Mapped[str] = mapped_column("nameTypeWithdrawal", String(250), nullable=True)
    codeTypeWithdrawal: Mapped[str] = mapped_column("codeTypeWithdrawal", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameTypeWithdrawal", name="uq_typeWithdrawal_name"), UniqueConstraint("codeTypeWithdrawal", name="uq_typeWithdrawal_code"),)
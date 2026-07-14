from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class TypeBankAccount(Base):
    __tablename__ = "loan_typeBankAccount"

    IdTypeBankAccount: Mapped[int] = mapped_column("IdTypeBankAccount", Integer, primary_key=True, autoincrement=True)
    nameTypeBankAccount: Mapped[str] = mapped_column("nameTypeBankAccount", String(250), nullable=True)
    codeTypeBankAccount: Mapped[str] = mapped_column("codeTypeBankAccount", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameTypeBankAccount", name="uq_typeBankAccount_name"), UniqueConstraint("codeTypeBankAccount", name="uq_typeBankAccount_code"),)
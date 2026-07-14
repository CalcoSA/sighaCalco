from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class Bank(Base):
    __tablename__ = "loan_bank"

    IdBank: Mapped[int] = mapped_column("IdBank", Integer, primary_key=True, autoincrement=True)
    nameBank: Mapped[str] = mapped_column("nameBank", String(250), nullable=True)
    codeBank: Mapped[str] = mapped_column("codeBank", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameBank", name="uq_bank_name"), UniqueConstraint("codeBank", name="uq_bank_code"),)
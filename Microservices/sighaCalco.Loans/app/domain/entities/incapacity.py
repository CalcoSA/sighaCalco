from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class Incapacity(Base):
    __tablename__ = "loan_incapacity"

    IdIncapacity: Mapped[int] = mapped_column("IdIncapacity", Integer, primary_key=True, autoincrement=True)
    nameIncapacity: Mapped[str] = mapped_column("nameIncapacity", String(250), nullable=True)
    codeIncapacity: Mapped[str] = mapped_column("codeIncapacity", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameIncapacity", name="uq_incapacity_name"), UniqueConstraint("codeIncapacity", name="uq_incapacity_code"),)
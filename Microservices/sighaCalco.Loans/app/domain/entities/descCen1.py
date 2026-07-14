from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class DescCen1(Base):
    __tablename__ = "loan_descCen1"

    IdDescCen1: Mapped[int] = mapped_column("IdDescCen1", Integer, primary_key=True, autoincrement=True)
    nameDescCen1: Mapped[str] = mapped_column("nameDescCen1", String(250), nullable=True)
    codeDescCen1: Mapped[str] = mapped_column("codeDescCen1", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameDescCen1", name="uq_descCen1_name"), UniqueConstraint("codeDescCen1", name="uq_descCen1_code"),)
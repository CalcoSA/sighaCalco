from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class DescCen4(Base):
    __tablename__ = "loan_descCen4"

    IdDescCen4: Mapped[int] = mapped_column("IdDescCen4", Integer, primary_key=True, autoincrement=True)
    nameDescCen4: Mapped[str] = mapped_column("nameDescCen4", String(250), nullable=True)
    codeDescCen4: Mapped[str] = mapped_column("codeDescCen4", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameDescCen4", name="uq_descCen4_name"), UniqueConstraint("codeDescCen4", name="uq_descCen4_code"),)
from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class DescCen2(Base):
    __tablename__ = "loan_descCen2"

    IdDescCen2: Mapped[int] = mapped_column("IdDescCen2", Integer, primary_key=True, autoincrement=True)
    nameDescCen2: Mapped[str] = mapped_column("nameDescCen2", String(250), nullable=True)
    codeDescCen2: Mapped[str] = mapped_column("codeDescCen2", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameDescCen2", name="uq_descCen2_name"), UniqueConstraint("codeDescCen2", name="uq_descCen2_code"),)
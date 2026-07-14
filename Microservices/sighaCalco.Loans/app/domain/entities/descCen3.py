from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class DescCen3(Base):
    __tablename__ = "loan_descCen3"

    IdDescCen3: Mapped[int] = mapped_column("IdDescCen3", Integer, primary_key=True, autoincrement=True)
    nameDescCen3: Mapped[str] = mapped_column("nameDescCen3", String(250), nullable=True)
    codeDescCen3: Mapped[str] = mapped_column("codeDescCen3", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameDescCen3", name="uq_descCen3_name"), UniqueConstraint("codeDescCen3", name="uq_descCen3_code"),)
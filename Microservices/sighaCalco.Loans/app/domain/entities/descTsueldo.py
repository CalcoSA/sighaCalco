from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class DescTsueldo(Base):
    __tablename__ = "loan_descTsueldo"

    IdDescTsueldo: Mapped[int] = mapped_column("IdDescTsueldo", Integer, primary_key=True, autoincrement=True)
    nameDescTsueldo: Mapped[str] = mapped_column("nameDescTsueldo", String(250), nullable=True)
    codeDescTsueldo: Mapped[str] = mapped_column("codeDescTsueldo", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameDescTsueldo", name="uq_descTsueldo_name"), UniqueConstraint("codeDescTsueldo", name="uq_descTsueldo_code"),)
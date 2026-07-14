from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class Absenteeism(Base):
    __tablename__ = "loan_absenteeism"

    IdAbsenteeism: Mapped[int] = mapped_column("IdAbsenteeism", Integer, primary_key=True, autoincrement=True)
    nameAbsenteeism: Mapped[str] = mapped_column("nameAbsenteeism", String(250), nullable=True)
    codeAbsenteeism: Mapped[str] = mapped_column("codeAbsenteeism", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("nameAbsenteeism", name="uq_absenteeism_name"), UniqueConstraint("codeAbsenteeism", name="uq_absenteeism_code"),)
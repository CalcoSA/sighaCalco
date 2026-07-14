from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column

class Diagnosis(Base):
    __tablename__ = "loan_diagnosis"
    
    IdDiagnosis: Mapped[int] = mapped_column("IdDiagnosis", Integer, primary_key=True, autoincrement=False)
    nameDiagnosis: Mapped[str] = mapped_column("nameDiagnosis", String(250), nullable=True)
    codeDiagnosis: Mapped[str] = mapped_column("codeDiagnosis", String(100), nullable=True)

    __table_args__ = (UniqueConstraint("IdDiagnosis", name="uq_diagnosis_id"), UniqueConstraint("nameDiagnosis", name="uq_diagnosis_name"), UniqueConstraint("codeDiagnosis", name="uq_diagnosis_code"),)
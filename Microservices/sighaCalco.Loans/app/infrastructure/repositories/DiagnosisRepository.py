from app.domain.interfaces.IDiagnosisRepository import IDiagnosisRepository
from app.common.pagination import PaginatedResult, PaginationParams
from app.domain.entities.diagnosis import Diagnosis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, cast, String
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

class DiagnosisRepository(IDiagnosisRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Diagnosis]:
        query = self.db.query(Diagnosis)

        if pagination.search and pagination.search.strip():
            searchValue = f"%{pagination.search.strip()}%"

            query = query.filter(
                or_(
                    cast(Diagnosis.IdDiagnosis, String).like(searchValue),
                    Diagnosis.codeDiagnosis.like(searchValue),
                    Diagnosis.nameDiagnosis.like(searchValue),
                )
            )

        total = query.count()
        items = (query.order_by(Diagnosis.IdDiagnosis.asc()).offset(pagination.offset).limit(pagination.pageSize).all())
        totalPages = ceil(total / pagination.pageSize) if pagination.pageSize > 0 else 0

        return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=pagination.pageSize, totalPages=totalPages,)

    def getById(self, IdDiagnosis: int) -> Optional[Diagnosis]:
        return (self.db.query(Diagnosis).filter(Diagnosis.IdDiagnosis == IdDiagnosis).first())
    
    def getByName(self, nameDiagnosis: str) -> Optional[Diagnosis]:
        return (self.db.query(Diagnosis).filter(Diagnosis.nameDiagnosis == nameDiagnosis.strip()).first())

    def getByCode(self, codeDiagnosis: str) -> Optional[Diagnosis]:
        return (self.db.query(Diagnosis).filter(Diagnosis.codeDiagnosis == codeDiagnosis.strip()).first())

    def create(self, diagnosisData: Diagnosis) -> Diagnosis:
        try:
            self.db.add(diagnosisData)
            self.db.commit()
            self.db.refresh(diagnosisData)
            return diagnosisData
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")

    def update(self, IdDiagnosis: int, diagnosisData: Diagnosis) -> Optional[Diagnosis]:
        try:
            diagnosisFound = self.getById(IdDiagnosis)

            if not diagnosisFound:
                return None

            diagnosisFound.nameDiagnosis = diagnosisData.nameDiagnosis
            diagnosisFound.codeDiagnosis = diagnosisData.codeDiagnosis

            self.db.commit()
            self.db.refresh(diagnosisFound)

            return diagnosisFound
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")

    def delete(self, IdDiagnosis: int) -> bool:
        try:
            diagnosisFound = self.getById(IdDiagnosis)

            if not diagnosisFound:
                return False

            self.db.delete(diagnosisFound)
            self.db.commit()

            return True
        
        except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Error al eliminar: {str(e)}")
from app.application.interfaces.IDiagnosisApplication import IDiagnosisApplication
from app.domain.interfaces.IDiagnosisRepository import IDiagnosisRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.diagnosis import Diagnosis
from typing import Optional

class DiagnosisApplication(IDiagnosisApplication):

    def __init__(self, diagnosisRepository: IDiagnosisRepository):
        self.diagnosisRepository = diagnosisRepository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Diagnosis]:
        return self.diagnosisRepository.getAll(pagination)

    def getById(self, IdDiagnosis: int) -> Diagnosis:
        DiagnosisFound = self.diagnosisRepository.getById(IdDiagnosis)

        if not DiagnosisFound:
            raise ValueError("Diagnóstico no encontrado.")

        return DiagnosisFound

    def create(self, diagnosisData: Diagnosis) -> Diagnosis:
        
        if diagnosisData.IdDiagnosis is None:
            raise ValueError("El ID del Diagnóstico es obligatorio.")

        DiagnosisExists = self.diagnosisRepository.getById(diagnosisData.IdDiagnosis)

        if DiagnosisExists:
            raise ValueError("Ya existe un Diagnóstico con ese ID.")

        diagnosisData.nameDiagnosis = self._normalizeText(diagnosisData.nameDiagnosis)
        diagnosisData.codeDiagnosis = self._normalizeText(diagnosisData.codeDiagnosis)

        if diagnosisData.nameDiagnosis:
            nameExists = self.diagnosisRepository.getByName(diagnosisData.nameDiagnosis)

            if nameExists:
                raise ValueError("Ya existe un Diagnóstico con ese nombre.")

        if diagnosisData.codeDiagnosis:
            codeExists = self.diagnosisRepository.getByCode(diagnosisData.codeDiagnosis)

            if codeExists:
                raise ValueError("Ya existe un Diagnóstico con ese código.")

        return self.diagnosisRepository.create(diagnosisData)

    def update(self, IdDiagnosis: int, diagnosisData: Diagnosis) -> Diagnosis:
        DiagnosisFound = self.diagnosisRepository.getById(IdDiagnosis)

        if not DiagnosisFound:
            raise ValueError("Diagnóstico no encontrado.")

        diagnosisData.nameDiagnosis = self._normalizeText(diagnosisData.nameDiagnosis)
        diagnosisData.codeDiagnosis = self._normalizeText(diagnosisData.codeDiagnosis)

        if diagnosisData.nameDiagnosis:
            nameExists = self.diagnosisRepository.getByName(diagnosisData.nameDiagnosis)

            if nameExists and nameExists.IdDiagnosis != IdDiagnosis:
                raise ValueError("Ya existe otro Diagnóstico con ese nombre.")

        if diagnosisData.codeDiagnosis:
            codeExists = self.diagnosisRepository.getByCode(diagnosisData.codeDiagnosis)

            if codeExists and codeExists.IdDiagnosis != IdDiagnosis:
                raise ValueError("Ya existe otro Diagnóstico con ese código.")

        DiagnosisUpdated = self.diagnosisRepository.update(IdDiagnosis, diagnosisData)

        if not DiagnosisUpdated:
            raise ValueError("Diagnóstico no encontrado.")

        return DiagnosisUpdated

    def delete(self, IdDiagnosis: int) -> bool:
        DiagnosisFound = self.diagnosisRepository.getById(IdDiagnosis)

        if not DiagnosisFound:
            raise ValueError("Diagnóstico no encontrado.")

        return self.diagnosisRepository.delete(IdDiagnosis)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
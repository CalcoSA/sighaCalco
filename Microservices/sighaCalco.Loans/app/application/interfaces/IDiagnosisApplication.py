from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.diagnosis import Diagnosis
from abc import ABC, abstractmethod

class IDiagnosisApplication(ABC):

    @abstractmethod
    def getAll(self, pagination: PaginationParams) -> PaginatedResult[Diagnosis]:
        pass

    @abstractmethod
    def getById(self, IdDiagnosis: int) -> Diagnosis:
        pass

    @abstractmethod
    def create(self, diagnosisData: Diagnosis) -> Diagnosis:
        pass

    @abstractmethod
    def update(self, IdDiagnosis: int, diagnosisData: Diagnosis) -> Diagnosis:
        pass

    @abstractmethod
    def delete(self, IdDiagnosis: int) -> bool:
        pass
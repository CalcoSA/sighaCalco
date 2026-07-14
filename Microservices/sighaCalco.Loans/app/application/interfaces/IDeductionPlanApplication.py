from app.domain.entities.deductionPlan import DeductionPlan
from abc import ABC, abstractmethod
from typing import List

class IDeductionPlanApplication(ABC):

    @abstractmethod
    def getAll(self) -> List[DeductionPlan]:
        pass

    @abstractmethod
    def getById(self, IdDeductionPlan: int) -> DeductionPlan:
        pass

    @abstractmethod
    def create(self, deductionPlanData: DeductionPlan) -> DeductionPlan:
        pass

    @abstractmethod
    def update(self, IdDeductionPlan: int, deductionPlanData: DeductionPlan) -> DeductionPlan:
        pass

    @abstractmethod
    def delete(self, IdDeductionPlan: int) -> bool:
        pass
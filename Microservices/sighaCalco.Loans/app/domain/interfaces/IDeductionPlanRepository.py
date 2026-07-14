from app.domain.entities.deductionPlan import DeductionPlan
from abc import ABC, abstractmethod
from typing import List, Optional

class IDeductionPlanRepository(ABC):

    @abstractmethod
    def getAll(self) -> List[DeductionPlan]:
        pass

    @abstractmethod
    def getById(self, IdDeductionPlan: int) -> Optional[DeductionPlan]:
        pass

    @abstractmethod
    def create(self, deductionPlanData: DeductionPlan) -> DeductionPlan:
        pass

    @abstractmethod
    def update(self, IdDeductionPlan: int, deductionPlanData: DeductionPlan) -> Optional[DeductionPlan]:
        pass

    @abstractmethod
    def delete(self, IdDeductionPlan: int) -> bool:
        pass
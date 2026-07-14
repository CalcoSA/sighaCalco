from app.application.interfaces.IDeductionPlanApplication import IDeductionPlanApplication
from app.domain.interfaces.IDeductionPlanRepository import IDeductionPlanRepository
from app.domain.entities.deductionPlan import DeductionPlan
from typing import List

class DeductionPlanApplication(IDeductionPlanApplication):

    def __init__(self, deductionPlanRepository: IDeductionPlanRepository):
        self.deductionPlanRepository = deductionPlanRepository

    def getAll(self) -> List[DeductionPlan]:
        return self.deductionPlanRepository.getAll()

    def getById(self, IdDeductionPlan: int) -> DeductionPlan:
        deductionPlanFound = self.deductionPlanRepository.getById(IdDeductionPlan)

        if not deductionPlanFound:
            raise ValueError("Plan de deducción no encontrado.")

        return deductionPlanFound

    def create(self, deductionPlanData: DeductionPlan) -> DeductionPlan:

        if not deductionPlanData.nameDeductionPlan.strip():
            raise ValueError("El nombre del plan de deducción es obligatorio.")

        return self.deductionPlanRepository.create(deductionPlanData)

    def update(self, IdDeductionPlan: int, deductionPlanData: DeductionPlan) -> DeductionPlan:
        deductionPlanFound = self.deductionPlanRepository.getById(IdDeductionPlan)

        if not deductionPlanFound:
            raise ValueError("Plan de deducción no encontrado.")

        if deductionPlanData.nameDeductionPlan is not None and not deductionPlanData.nameDeductionPlan.strip():
            raise ValueError("El nombre del plan de deducción es obligatorio.")

        updatedDeductionPlan = self.deductionPlanRepository.update(IdDeductionPlan, deductionPlanData)

        if not updatedDeductionPlan:
            raise ValueError("Plan de deducción no encontrado.")

        return updatedDeductionPlan

    def delete(self, IdDeductionPlan: int) -> bool:
        deductionPlanFound = self.deductionPlanRepository.getById(IdDeductionPlan)

        if not deductionPlanFound:
            raise ValueError("Plan de deducción no encontrado.")

        return self.deductionPlanRepository.delete(IdDeductionPlan)
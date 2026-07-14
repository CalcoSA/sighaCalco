from app.application.interfaces.IPayrollSinergyApplication import IPayrollSinergyApplication
from app.domain.interfaces.IPayrollSinergyRepository import IPayrollSinergyRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.payrollSinergy import PayrollSinergy
from typing import Optional, List

class PayrollSinergyApplication(IPayrollSinergyApplication):

    def __init__(self, payrollSinergyRepository: IPayrollSinergyRepository):
        self.payrollSinergyRepository = payrollSinergyRepository

    def getAll(self, pagination: PaginationParams) -> PaginatedResult[PayrollSinergy]:
        return self.payrollSinergyRepository.getAll(pagination)
    
    def getAllPayroll(self, search: Optional[str] = None) -> List[PayrollSinergy]:
        return self.payrollSinergyRepository.getAllPayroll(search)

    def getById(self, IdPayrollSinergy: int) -> PayrollSinergy:
        PayrollSinergyFound = self.payrollSinergyRepository.getById(IdPayrollSinergy)

        if not PayrollSinergyFound:
            raise ValueError("Concepto de nómina no encontrado.")

        return PayrollSinergyFound

    def create(self, payrollSinergyData: PayrollSinergy) -> PayrollSinergy:
        payrollSinergyData.namePayrollSinergy = self._normalizeText(payrollSinergyData.namePayrollSinergy)
        payrollSinergyData.codePayrollSinergy = self._normalizeText(payrollSinergyData.codePayrollSinergy)

        if payrollSinergyData.namePayrollSinergy:
            nameExists = self.payrollSinergyRepository.getByName(payrollSinergyData.namePayrollSinergy)

            if nameExists:
                raise ValueError("Ya existe un Concepto de nómina con ese nombre.")

        if payrollSinergyData.codePayrollSinergy:
            codeExists = self.payrollSinergyRepository.getByCode(payrollSinergyData.codePayrollSinergy)

            if codeExists:
                raise ValueError("Ya existe un Concepto de nómina con ese código.")

        return self.payrollSinergyRepository.create(payrollSinergyData)

    def update(self, IdPayrollSinergy: int, payrollSinergyData: PayrollSinergy) -> PayrollSinergy:
        PayrollSinergyFound = self.payrollSinergyRepository.getById(IdPayrollSinergy)

        if not PayrollSinergyFound:
            raise ValueError("Concepto de nómina no encontrado.")

        payrollSinergyData.namePayrollSinergy = self._normalizeText(payrollSinergyData.namePayrollSinergy)
        payrollSinergyData.codePayrollSinergy = self._normalizeText(payrollSinergyData.codePayrollSinergy)

        if payrollSinergyData.namePayrollSinergy:
            nameExists = self.payrollSinergyRepository.getByName(payrollSinergyData.namePayrollSinergy)

            if nameExists and nameExists.IdPayrollSinergy != IdPayrollSinergy:
                raise ValueError("Ya existe otro Concepto de nómina con ese nombre.")

        if payrollSinergyData.codePayrollSinergy:
            codeExists = self.payrollSinergyRepository.getByCode(payrollSinergyData.codePayrollSinergy)

            if codeExists and codeExists.IdPayrollSinergy != IdPayrollSinergy:
                raise ValueError("Ya existe otro Concepto de nómina con ese código.")

        PayrollSinergyUpdated = self.payrollSinergyRepository.update(IdPayrollSinergy, payrollSinergyData)

        if not PayrollSinergyUpdated:
            raise ValueError("Concepto de nómina no encontrado.")

        return PayrollSinergyUpdated

    def delete(self, IdPayrollSinergy: int) -> bool:
        PayrollSinergyFound = self.payrollSinergyRepository.getById(IdPayrollSinergy)

        if not PayrollSinergyFound:
            raise ValueError("Concepto de nómina no encontrado.")

        return self.payrollSinergyRepository.delete(IdPayrollSinergy)

    def _normalizeText(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
from app.application.interfaces.ILoanApplication import ILoanApplication
from app.domain.interfaces.ILoanLogRepository import ILoanLogRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.interfaces.ILoanRepository import ILoanRepository
from app.domain.entities.loanInstallment import LoanInstallment
from app.domain.dtos.LoanDto import LoanCreateDto, LoanDto
from app.domain.entities.loanLog import LoanLog
from app.domain.entities.loan import Loan
from decimal import Decimal
from typing import Optional
from datetime import date

class LoanApplication(ILoanApplication):

    def __init__(self, loanRepository: ILoanRepository, loanLogRepository: ILoanLogRepository):
        self.loanRepository = loanRepository
        self.loanLogRepository = loanLogRepository

    def getAll(self, pagination: PaginationParams, employeeDocumentNumber: Optional[str] = None, IdLoanStatus: Optional[int] = None, requestDateFrom: Optional[date] = None, requestDateTo: Optional[date] = None) -> PaginatedResult[LoanDto]:
        data = self.loanRepository.getAll(pagination=pagination, employeeDocumentNumber=employeeDocumentNumber, IdLoanStatus=IdLoanStatus, requestDateFrom=requestDateFrom, requestDateTo=requestDateTo)
        return PaginatedResult(items=[self._toDto(item) for item in data.items], total=data.total, page=data.page, pageSize=data.pageSize, totalPages=data.totalPages,)
    
    def _toDto(self, loan: Loan) -> LoanDto:
        return LoanDto.model_validate(loan)

    def create(self, loanData: LoanCreateDto) -> LoanDto:
        self._validateCreate(loanData)

        loan = Loan(
            employeeDocumentNumber=loanData.employeeDocumentNumber.strip(),
            employeeFullName=loanData.employeeFullName.strip(),
            employeeRoleName=self._normalizeText(loanData.employeeRoleName),
            employeeCostCenterName=self._normalizeText(loanData.employeeCostCenterName),
            crossDocument=self._normalizeText(loanData.crossDocument),
            IdConcept=loanData.IdConcept,
            conceptName=loanData.conceptName.strip(),
            IdDeductionPlan=loanData.IdDeductionPlan,
            deductionPlanName=loanData.deductionPlanName.strip(),
            IdLoanStatus=loanData.IdLoanStatus,
            loanStatusName=loanData.loanStatusName.strip(),
            loanAmount=loanData.loanAmount,
            numberInstallments=loanData.numberInstallments,
            paidInstallments=0,
            remainingAmount=loanData.loanAmount,
            requestDate=loanData.requestDate,
            startDiscountDate=loanData.startDiscountDate,
            endDiscountDate=loanData.endDiscountDate,
            observation=self._normalizeText(loanData.observation),
            createdByUserName=loanData.createdByUserName.strip(),
            updatedByUserName=None,
        )

        loan.loanInstallments = [
            LoanInstallment(
                installmentNumber=item.installmentNumber,
                installmentValue=item.installmentValue,
                isPaid=item.isPaid,
                commitmentDate=item.commitmentDate,
                paymentDate=item.paymentDate,
            )
            for item in loanData.loanInstallments
        ]

        createdLoan = self.loanRepository.create(loan)

        self._createLoanLogs(createdLoan)

        return createdLoan

    def _validateCreate(self, loanData: LoanCreateDto) -> None:

        if not loanData.employeeDocumentNumber.strip():
            raise ValueError("El documento del colaborador es obligatorio.")

        if not loanData.employeeFullName.strip():
            raise ValueError("El nombre del colaborador es obligatorio.")

        if loanData.IdConcept <= 0:
            raise ValueError("El concepto es obligatorio.")

        if not loanData.conceptName.strip():
            raise ValueError("El nombre del concepto es obligatorio.")

        if loanData.IdDeductionPlan <= 0:
            raise ValueError("El plan de deducción es obligatorio.")

        if not loanData.deductionPlanName.strip():
            raise ValueError("El nombre del plan de deducción es obligatorio.")

        if loanData.IdLoanStatus <= 0:
            raise ValueError("El estado del préstamo es obligatorio.")

        if not loanData.loanStatusName.strip():
            raise ValueError("El nombre del estado del préstamo es obligatorio.")

        if loanData.loanAmount <= Decimal("0"):
            raise ValueError("El valor del préstamo debe ser mayor a cero.")
        
        if not loanData.loanInstallments:
            raise ValueError("Debe ingresar al menos una cuota.")
        
        if len(loanData.loanInstallments) != loanData.numberInstallments:
            raise ValueError("La cantidad de cuotas ingresadas debe ser igual al número de cuotas del préstamo.")

        totalInstallments = Decimal("0")

        for item in loanData.loanInstallments:

            if item.installmentNumber <= 0:
                raise ValueError("El número de cuota debe ser mayor a cero.")

            if item.installmentValue <= Decimal("0"):
                raise ValueError("El valor de cada cuota debe ser mayor a cero.")
            
            if not item.commitmentDate:
                raise ValueError("La fecha compromiso de cada cuota es obligatoria.")
            
            totalInstallments += item.installmentValue

        if totalInstallments.quantize(Decimal("0.01")) != loanData.loanAmount.quantize(Decimal("0.01")):
            raise ValueError("La suma del valor de las cuotas debe ser igual al valor del préstamo.")

        if loanData.startDiscountDate < loanData.requestDate:
            raise ValueError("La fecha de inicio del descuento no puede ser menor a la fecha de solicitud.")

        if loanData.endDiscountDate and loanData.endDiscountDate < loanData.startDiscountDate:
            raise ValueError("La fecha final del descuento no puede ser menor a la fecha inicial del descuento.")

        if not loanData.createdByUserName.strip():
            raise ValueError("El usuario que crea el préstamo es obligatorio.")

    def _normalizeText(self, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value if value else None
    
    def _createLoanLogs(self, loan: Loan) -> None:
        self.loanLogRepository.create(
            LoanLog(
                actionType="Creación",
                IdLoan=loan.IdLoan,
                IdLoanInstallment=None,
                installmentNumber=None,
                employeeDocumentNumber=loan.employeeDocumentNumber,
                conceptName=loan.conceptName,
                loanStatusName=loan.loanStatusName,
                installmentStatusName=None,
                observation=loan.observation,
                actorUserName=loan.createdByUserName,
            )
        )

        for installment in loan.loanInstallments:
            self.loanLogRepository.create(
                LoanLog(
                    actionType="Creación",
                    IdLoan=loan.IdLoan,
                    IdLoanInstallment=installment.IdLoanInstallment,
                    installmentNumber=installment.installmentNumber,
                    employeeDocumentNumber=loan.employeeDocumentNumber,
                    conceptName=loan.conceptName,
                    loanStatusName=loan.loanStatusName,
                    installmentStatusName="Pagada" if installment.isPaid else "Pendiente",
                    observation=f"Se creó la cuota número {installment.installmentNumber} con fecha compromiso {installment.commitmentDate}.",
                    actorUserName=loan.createdByUserName,
                )
            )
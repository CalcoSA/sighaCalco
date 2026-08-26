from app.domain.interfaces.ILoanStatusHistoryRepository import ILoanStatusHistoryRepository
from app.domain.interfaces.ILoanStatusRepository import ILoanStatusRepository
from app.domain.dtos.LoanDto import LoanCreateDto, LoanDto, LoanUpdateDto
from app.application.interfaces.ILoanApplication import ILoanApplication
from app.domain.interfaces.ILoanLogRepository import ILoanLogRepository
from app.common.pagination import PaginationParams, PaginatedResult
from app.domain.entities.loanStatusHistory import LoanStatusHistory
from app.domain.interfaces.ILoanRepository import ILoanRepository
from app.domain.entities.loanInstallment import LoanInstallment
from app.domain.dtos.LoanScheduledDto import LoanScheduledDto
from app.domain.entities.loanLog import LoanLog
from sqlalchemy.exc import SQLAlchemyError
from app.domain.entities.loan import Loan
from datetime import date, datetime
from calendar import monthrange
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import Optional

class LoanApplication(ILoanApplication):

    def __init__(self, loanRepository: ILoanRepository, loanLogRepository: ILoanLogRepository, loanStatusHistoryRepository: ILoanStatusHistoryRepository, loanStatusRepository: ILoanStatusRepository):
        self.loanRepository = loanRepository
        self.loanLogRepository = loanLogRepository
        self.loanStatusHistoryRepository = loanStatusHistoryRepository
        self.loanStatusRepository = loanStatusRepository

    def _nowColombia(self) -> datetime:
        return datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)

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
        self._createLoanStatusHistory(createdLoan)
        self.loanRepository.commit()
        self._createLoanLogs(createdLoan)

        return self._toDto(createdLoan)

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

    def _createLoanStatusHistory(self, loan: Loan) -> None:
        self.loanStatusHistoryRepository.create(
            LoanStatusHistory(
                IdLoan=loan.IdLoan,
                IdLoanStatus=loan.IdLoanStatus,
                observation="Creación.",
                createdAt=loan.createdAt,
                createdByUserName=loan.createdByUserName,
            )
        )

    def updateLoanStatus(self, IdLoan: int, loanData: LoanUpdateDto) -> LoanDto:
        observation = loanData.observation.strip()
        updatedByUserName = (loanData.updatedByUserName.strip())

        if not observation:
            raise ValueError("La observación es obligatoria.")

        if not updatedByUserName:
            raise ValueError("El usuario que modifica el préstamo es obligatorio.")

        try:
            loanFound = self.loanRepository.getByIdForUpdate(IdLoan)

            if not loanFound:
                raise ValueError("Préstamo no encontrado.")

            if loanFound.IdLoanStatus == 4:
                raise ValueError("No se puede modificar un préstamo que se encuentra Terminado.")

            if loanFound.IdLoanStatus == 5:
                raise ValueError("No se puede modificar un préstamo que se encuentra Cancelado.")

            loanStatusFound = self.loanStatusRepository.getById(loanData.IdLoanStatus)

            if not loanStatusFound:
                raise ValueError("El estado seleccionado no existe.")

            previousStatusId = loanFound.IdLoanStatus
            previousStatusName = loanFound.loanStatusName
            newStatusName = loanStatusFound.nameLoanStatus
            nowColombia = self._nowColombia()

            updatedLoan = self.loanRepository.updateStatus(
                loanData=loanFound,
                IdLoanStatus=loanData.IdLoanStatus,
                loanStatusName=newStatusName,
                updatedByUserName=updatedByUserName,
                updatedAt=nowColombia,
            )

            wasReactivated = (previousStatusId == 3 and loanData.IdLoanStatus == 1)

            if wasReactivated:
                self._recalculatePendingInstallmentDates(loan=updatedLoan, reactivationDate=nowColombia.date())

            self.loanStatusHistoryRepository.create(
                LoanStatusHistory(
                    IdLoan=updatedLoan.IdLoan,
                    IdLoanStatus=loanData.IdLoanStatus,
                    observation=observation,
                    createdAt=nowColombia,
                    createdByUserName=updatedByUserName,
                )
            )

            recalculationMessage = (
                " Se recalcularon las fechas de las cuotas pendientes."
                if wasReactivated
                else ""
            )

            self.loanLogRepository.add(
                LoanLog(
                    actionType="Actualización de estado",
                    IdLoan=updatedLoan.IdLoan,
                    IdLoanInstallment=None,
                    installmentNumber=None,
                    employeeDocumentNumber=(updatedLoan.employeeDocumentNumber),
                    conceptName=updatedLoan.conceptName,
                    loanStatusName=newStatusName,
                    installmentStatusName=None,
                    observation=(
                        f"El estado del préstamo cambió de "
                        f"{previousStatusName} a "
                        f"{newStatusName}."
                        f"{recalculationMessage} "
                        f"Observación: {observation}"
                    ),
                    actorUserName=updatedByUserName,
                )
            )

            self.loanRepository.commit()
            refreshedLoan = self.loanRepository.getById(IdLoan)

            if not refreshedLoan:
                raise Exception("No fue posible recuperar el préstamo actualizado.")

            return LoanDto.model_validate(refreshedLoan)

        except ValueError:
            self.loanRepository.rollback()
            raise

        except SQLAlchemyError as exception:
            self.loanRepository.rollback()

            raise Exception("Error de base de datos al actualizar " f"el estado del préstamo: {str(exception)}") from exception

        except Exception as exception:
            self.loanRepository.rollback()

            raise Exception("Error al actualizar el estado del " f"préstamo: {str(exception)}") from exception

    def processScheduledLoans(self, actorUserName: str) -> LoanScheduledDto:
        currentDate = datetime.now(ZoneInfo("America/Bogota")).date()
        (cycleName, targetInstallmentDate, allowedPlans) = self.getCurrentScheduledCycle(currentDate)
        result = LoanScheduledDto(executionDate=currentDate, cycleName=cycleName, targetInstallmentDate=targetInstallmentDate)
        loanIds = self.loanRepository.getScheduledLoanIds()
        result.reviewedLoans = len(loanIds)
        self.loanRepository.rollback()

        for IdLoan in loanIds:
            try:
                loan = self.loanRepository.getByIdForScheduled(IdLoan)

                if not loan:
                    result.skippedLoans += 1
                    self.loanRepository.rollback()
                    continue

                wasModified = self._processScheduledLoan(
                    loan=loan,
                    targetInstallmentDate=targetInstallmentDate,
                    allowedPlans=allowedPlans,
                    actorUserName=actorUserName,
                    result=result,
                )

                if wasModified:
                    self.loanRepository.commit()
                else:
                    self.loanRepository.rollback()

            except Exception as exception:
                self.loanRepository.rollback()
                result.failedLoans += 1
                result.errors.append(f"Préstamo {IdLoan}: {str(exception)}")

        return result

    def getCurrentScheduledCycle(self, currentDate: date,) -> tuple[str, date, set[str]]:

        if currentDate.day <= 15:
            targetInstallmentDate = date(currentDate.year, currentDate.month, 15,)

            return ("Primera quincena", targetInstallmentDate, { "primera quincena", "ambas quincenas", },)

        lastDayOfMonth = monthrange(currentDate.year, currentDate.month,)[1]
        targetInstallmentDate = date(currentDate.year, currentDate.month, lastDayOfMonth,)

        return ("Segunda quincena", targetInstallmentDate, { "segunda quincena", "ambas quincenas", },)
    
    def _recalculatePendingInstallmentDates(self, loan: Loan, reactivationDate: date) -> None:

        pendingInstallments = sorted(
            [
                installment
                for installment in loan.loanInstallments
                if not installment.isPaid
            ],
            key=lambda installment: installment.installmentNumber,
        )

        if not pendingInstallments:
            return

        deductionPlanName = loan.deductionPlanName.strip().lower()

        newCommitmentDates = self._calculateCommitmentDates(startDate=reactivationDate, numberInstallments=len(pendingInstallments), deductionPlanName=deductionPlanName)

        for installment, commitmentDate in zip(pendingInstallments, newCommitmentDates):
            installment.commitmentDate = commitmentDate
            installment.paymentDate = None

        loan.endDiscountDate = newCommitmentDates[-1]

    def _processScheduledLoan(self, loan: Loan, targetInstallmentDate: date, allowedPlans: set[str], actorUserName: str, result: LoanScheduledDto,) -> bool:

        if loan.IdLoanStatus not in [1, 2]:
            result.skippedLoans += 1
            return False

        deductionPlanName = (loan.deductionPlanName.strip().lower())

        if deductionPlanName not in allowedPlans:
            result.skippedLoans += 1
            return False

        if loan.startDiscountDate > targetInstallmentDate:
            result.skippedLoans += 1
            return False

        registeredInstallments = len(loan.loanInstallments)

        if registeredInstallments != loan.numberInstallments:
            self._addScheduledLoanLog(
                loan=loan,
                actionType="Validación de cuotas",
                observation=("No se procesó el préstamo porque " f"numberInstallments indica " f"{loan.numberInstallments} cuotas, pero " f"se encontraron {registeredInstallments} cuotas registradas."),
                actorUserName=actorUserName,
            )

            result.failedLoans += 1
            result.errors.append(f"Préstamo {loan.IdLoan}: el número de cuotas no coincide con las cuotas registradas.")

            return True

        wasModified = False

        if loan.IdLoanStatus == 2:
            nowColombia = self._nowColombia()
            loan.IdLoanStatus = 1
            loan.loanStatusName = "Activo"
            loan.updatedByUserName = actorUserName
            loan.updatedAt = nowColombia
            activationObservation = ("El préstamo cambió de Inactivo a Activo porque llegó la quincena correspondiente para iniciar el descuento.")

            self._addScheduledLoanStatusHistory(loan=loan, observation=activationObservation, actorUserName=actorUserName, createdAt=nowColombia)
            self._addScheduledLoanLog(loan=loan, actionType="Activación automática", observation=activationObservation, actorUserName=actorUserName)

            result.activatedLoans += 1
            wasModified = True

        pendingInstallments = sorted(
            [
                installment
                for installment in loan.loanInstallments
                if not installment.isPaid
            ],
            key=lambda installment: (installment.commitmentDate, installment.installmentNumber,),
        )

        if not pendingInstallments:
            result.skippedLoans += 1
            return wasModified

        targetInstallments = [
            installment
            for installment in pendingInstallments
            if (installment.commitmentDate == targetInstallmentDate)
        ]

        if not targetInstallments:
            result.skippedLoans += 1
            return wasModified

        if len(targetInstallments) > 1:
            raise ValueError("Existe más de una cuota pendiente con fecha " f"compromiso {targetInstallmentDate}.")

        installment = targetInstallments[0]
        installment.isPaid = True
        installment.paymentDate = targetInstallmentDate
        loan.updatedByUserName = actorUserName
        loan.updatedAt = self._nowColombia()

        self._recalculateScheduledLoan(loan)
        self._addScheduledLoanLog(
            loan=loan,
            actionType="Pago automático de cuota",
            IdLoanInstallment=(installment.IdLoanInstallment),
            installmentNumber=(installment.installmentNumber),
            installmentStatusName="Pagada",
            observation=("La tarea marcó como pagada la cuota número " f"{installment.installmentNumber}, con fecha " f"compromiso {installment.commitmentDate} y " f"valor {installment.installmentValue}."),
            actorUserName=actorUserName,
        )

        result.paidInstallments += 1
        result.processedLoanIds.append(loan.IdLoan)

        remainingPendingInstallments = [
            currentInstallment
            for currentInstallment in loan.loanInstallments
            if not currentInstallment.isPaid
        ]

        if not remainingPendingInstallments:
            nowColombia = self._nowColombia()
            loan.IdLoanStatus = 4
            loan.loanStatusName = "Terminado"
            loan.endDiscountDate = targetInstallmentDate
            loan.updatedByUserName = actorUserName
            loan.updatedAt = nowColombia
            finishedObservation = ("El préstamo cambió a Terminado porque todas sus cuotas se encuentran pagadas.")

            self._addScheduledLoanStatusHistory(loan=loan, observation=finishedObservation, actorUserName=actorUserName, createdAt=nowColombia)
            self._addScheduledLoanLog(loan=loan, actionType="Terminación automática", observation=finishedObservation, actorUserName=actorUserName)

            result.finishedLoans += 1

        return True

    def _recalculateScheduledLoan(self, loan: Loan,) -> None:

        paidInstallments = [
            installment
            for installment in loan.loanInstallments
            if installment.isPaid
        ]

        pendingInstallments = [
            installment
            for installment in loan.loanInstallments
            if not installment.isPaid
        ]

        loan.paidInstallments = len(paidInstallments)

        loan.remainingAmount = sum(
            (
                installment.installmentValue
                for installment in pendingInstallments
            ),
            Decimal("0"),
        ).quantize(Decimal("0.01"))

    def _addScheduledLoanLog(self, loan: Loan, actionType: str, observation: str, actorUserName: str, IdLoanInstallment: Optional[int] = None, installmentNumber: Optional[int] = None, installmentStatusName: Optional[str] = None,) -> None:
        self.loanLogRepository.add(
            LoanLog(
                actionType=actionType,
                IdLoan=loan.IdLoan,
                IdLoanInstallment=IdLoanInstallment,
                installmentNumber=installmentNumber,
                employeeDocumentNumber=(loan.employeeDocumentNumber),
                conceptName=loan.conceptName,
                loanStatusName=loan.loanStatusName,
                installmentStatusName=(installmentStatusName),
                observation=observation,
                actorUserName=actorUserName,
            )
        )

    def _addScheduledLoanStatusHistory(self, loan: Loan, observation: str, actorUserName: str, createdAt: datetime) -> None:
        self.loanStatusHistoryRepository.create(
            LoanStatusHistory(
                IdLoan=loan.IdLoan,
                IdLoanStatus=loan.IdLoanStatus,
                observation=observation,
                createdAt=createdAt,
                createdByUserName=actorUserName,
            )
        )
    
    def _calculateCommitmentDates(self, startDate: date, numberInstallments: int, deductionPlanName: str) -> list[date]:
        dates: list[date] = []

        if deductionPlanName == "primera quincena":
            firstMonthOffset = 0 if startDate.day <= 15 else 1

            for index in range(numberInstallments):
                monthIndex = (startDate.month - 1 + firstMonthOffset + index)
                year = startDate.year + (monthIndex // 12)
                month = (monthIndex % 12) + 1
                dates.append(date(year, month, 15))

            return dates

        if deductionPlanName == "segunda quincena":

            for index in range(numberInstallments):
                monthIndex = (startDate.month - 1 + index)
                year = startDate.year + (monthIndex // 12)
                month = (monthIndex % 12) + 1
                lastDay = monthrange(year, month)[1]
                dates.append(date(year, month, lastDay))

            return dates

        if deductionPlanName == "ambas quincenas":
            currentYear = startDate.year
            currentMonth = startDate.month
            isFirstFortnight = startDate.day <= 15

            for _ in range(numberInstallments):

                if isFirstFortnight:
                    dates.append(date(currentYear, currentMonth, 15))

                    isFirstFortnight = False

                else:
                    lastDay = monthrange(currentYear, currentMonth)[1]
                    dates.append(date(currentYear, currentMonth, lastDay))
                    isFirstFortnight = True
                    currentMonth += 1

                    if currentMonth > 12:
                        currentMonth = 1
                        currentYear += 1

            return dates

        raise ValueError("El plan de deducción del préstamo no es válido.")
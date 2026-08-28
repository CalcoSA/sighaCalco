from app.infrastructure.repositories.ServiceDiscountHistoryRepository import ServiceDiscountHistoryRepository
from app.infrastructure.repositories.LoanStatusHistoryRepository import LoanStatusHistoryRepository
from app.infrastructure.repositories.LoanStatusRepository import LoanStatusRepository
from app.domain.dtos.LoanDto import LoanCreateDto, LoanDto, LoanUpdateDto
from app.infrastructure.repositories.LoanLogRepository import LoanLogRepository
from app.domain.dtos.ServiceDiscountHistoryDto import ServiceValueUpdateDto
from app.infrastructure.repositories.LoanRepository import LoanRepository
from app.application.interfaces.ILoanApplication import ILoanApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.application.services.LoanApplication import LoanApplication
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.dtos.LoanScheduledDto import LoanScheduledDto
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

router = APIRouter(prefix="/loans/loan", tags=["loan"])
logger = getLogger(__name__)

def getLoanApplication(db: Session = Depends(getDb)) -> ILoanApplication:
    loanRepository = LoanRepository(db)
    loanLogRepository = LoanLogRepository(db)
    loanStatusHistoryRepository = LoanStatusHistoryRepository(db)
    loanStatusRepository = LoanStatusRepository(db)
    serviceDiscountHistoryRepository = ServiceDiscountHistoryRepository(db)

    return LoanApplication(
        loanRepository=loanRepository,
        loanLogRepository=loanLogRepository,
        loanStatusHistoryRepository=loanStatusHistoryRepository,
        loanStatusRepository=loanStatusRepository,
        serviceDiscountHistoryRepository=serviceDiscountHistoryRepository
    )

@router.get("/", response_model=apiResponse)
def getAllLoans(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), employeeDocumentNumber: Optional[str] = Query(None), IdLoanStatus: Optional[int] = Query(None), requestDateFrom: Optional[date] = Query(None), requestDateTo: Optional[date] = Query(None), service: ILoanApplication = Depends(getLoanApplication),):
    try:
        pagination = PaginationParams(page=page, pageSize=pageSize)
        data = service.getAll(pagination=pagination, employeeDocumentNumber=employeeDocumentNumber, IdLoanStatus=IdLoanStatus, requestDateFrom=requestDateFrom, requestDateTo=requestDateTo,)

        if not data.items:
            logger.info("No existen préstamos registrados con los filtros enviados.")
            return apiResponse(isSuccess=False, Message="No existen préstamos registrados.", result=data)

        return apiResponse(isSuccess=True, Message="Préstamos obtenidos correctamente.", result=data)

    except Exception:
        logger.exception("Error inesperado obteniendo préstamos.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los préstamos.")
"""
@router.get("/{IdLoan}", response_model=apiResponseDto[LoanResponseDto])
def getLoanById(IdLoan: int, service: ILoanApplication = Depends(getLoanApplication)):
    try:
        logger.info("Consultando opción de menú | IdLoan=%s", IdLoan)
        data = service.getById(IdLoan)
        logger.info("Opción de menú obtenida correctamente | IdLoan=%s", IdLoan)
        return apiResponseDto(isSuccess=True, Message="Opción de menú obtenida correctamente.", result=data)

    except ValueError as e:
        logger.warning("Opción de menú no encontrada | IdLoan=%s | error=%s", IdLoan, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo opción de menú | IdLoan=%s", IdLoan)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la opción de menú.")
"""
@router.post("/", response_model=apiResponse[LoanDto], status_code=status.HTTP_201_CREATED)
def createLoan(loanData: LoanCreateDto, service: ILoanApplication = Depends(getLoanApplication)):
    try:
        logger.info("Creando préstamo al colaborador | employeeFullName=%s ", getattr(loanData, "employeeFullName", None))
        data = service.create(loanData)
        logger.info("Préstamo creado correctamente | IdLoan=%s ", getattr(data, "IdLoan", None))
        return apiResponse(isSuccess=True, Message="Préstamo creado correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación creando préstamo al colaborador | employeeFullName=%s | error=%s", getattr(loanData, "employeeFullName", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando préstado al colaborador | employeeFullName=%s ", getattr(loanData, "employeeFullName", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear préstamo.")

@router.post("/scheduled", response_model=apiResponse[LoanScheduledDto],)
def scheduledLoansManually(service: ILoanApplication = Depends(getLoanApplication),):
    try:
        logger.info("Ejecutando manualmente el proceso " "programado de préstamos.")
        data = service.processScheduledLoans(actorUserName="EJECUCION_MANUAL")
        logger.info(
            "Proceso programado ejecutado manualmente "
            "| executionDate=%s "
            "| cycleName=%s "
            "| paidInstallments=%s "
            "| finishedLoans=%s",
            data.executionDate,
            data.cycleName,
            data.paidInstallments,
            data.finishedLoans,
        )
        return apiResponse(isSuccess=True, Message=("Proceso programado de préstamos " "ejecutado correctamente."), result=data,)

    except ValueError as exception:
        logger.warning("Validación ejecutando manualmente " "el proceso programado " "| error=%s", str(exception),)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception),)

    except Exception:
        logger.exception("Error inesperado ejecutando manualmente " "el proceso programado de préstamos.")
        raise HTTPException(status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR), detail=("Error al ejecutar el proceso " "programado de préstamos."),)

@router.put("/{IdLoan}/status", response_model=apiResponse[LoanDto])
def updateLoanStatus(IdLoan: int, loanData: LoanUpdateDto, service: ILoanApplication = Depends(getLoanApplication)):
    try:
        logger.info("Actualizando estado del préstamo | IdLoan=%s | IdLoanStatus=%s | updatedByUserName=%s", IdLoan, loanData.IdLoanStatus, loanData.updatedByUserName)
        data = service.updateLoanStatus(IdLoan=IdLoan, loanData=loanData)
        logger.info("Estado del préstamo actualizado correctamente | IdLoan=%s | IdLoanStatus=%s", IdLoan, loanData.IdLoanStatus)
        return apiResponse(isSuccess=True, Message="Estado del préstamo actualizado correctamente.", result=data)

    except ValueError as exception:
        message = str(exception)

        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "préstamo no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        logger.warning("Validación actualizando estado | IdLoan=%s | IdLoanStatus=%s | status=%s | error=%s", IdLoan, loanData.IdLoanStatus, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando estado | IdLoan=%s | IdLoanStatus=%s", IdLoan, loanData.IdLoanStatus)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el estado del préstamo.")

@router.put("/{IdLoan}/service-value", response_model=apiResponse[LoanDto])
def updateServiceValue(IdLoan: int, serviceData: ServiceValueUpdateDto, service: ILoanApplication = Depends(getLoanApplication)):
    try:
        logger.info("Actualizando valor del servicio | IdLoan=%s | serviceValue=%s", IdLoan, serviceData.serviceValue)
        data = (service.updateServiceValue(IdLoan=IdLoan, serviceData=serviceData))
        return apiResponse(isSuccess=True, Message="Valor del servicio actualizado correctamente.", result=data)

    except ValueError as exception:
        message = str(exception)

        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado"
            in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error actualizando valor | IdLoan=%s", IdLoan)

        raise HTTPException(status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR), detail=("Error al actualizar el valor del servicio."))
    
"""
@router.put("/{IdLoan}", response_model=apiResponseDto[LoanResponseDto])
def updateLoan(IdLoan: int, LoanData: LoanUpdateDto, service: ILoanApplication = Depends(getLoanApplication)):
    try:
        logger.info("Actualizando opción de menú | IdLoan=%s | nameLoan=%s | pathLoan=%s", IdLoan, getattr(LoanData, "nameLoan", None), getattr(LoanData, "pathLoan", None))
        data = service.update(IdLoan, LoanData)
        logger.info("Opción de menú actualizada correctamente | IdLoan=%s", IdLoan)
        return apiResponseDto(isSuccess=True, Message="Opción de menú actualizada correctamente.", result=data)

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrada" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando opción de menú | IdLoan=%s | status=%s | error=%s", IdLoan, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando opción de menú | IdLoan=%s", IdLoan)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar la opción de menú.")

@router.delete("/{IdLoan}", response_model=apiResponseDto[dict])
def deleteLoan(IdLoan: int, service: ILoanApplication = Depends(getLoanApplication)):
    try:
        logger.info("Eliminando opción de menú | IdLoan=%s", IdLoan)
        service.delete(IdLoan)
        logger.info("Opción de menú eliminada correctamente | IdLoan=%s", IdLoan)
        return apiResponseDto(isSuccess=True, Message="Opción de menú eliminada correctamente.", result={})

    except ValueError as e:
        logger.warning("Opción de menú no encontrada al eliminar | IdLoan=%s | error=%s", IdLoan, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando opción de menú | IdLoan=%s", IdLoan)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar la opción de menú.")
"""
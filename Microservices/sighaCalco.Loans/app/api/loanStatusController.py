from app.infrastructure.repositories.LoanStatusRepository import LoanStatusRepository
from app.application.interfaces.ILoanStatusApplication import ILoanStatusApplication
from app.application.services.LoanStatusApplication import LoanStatusApplication
from fastapi import APIRouter, Depends, HTTPException, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.entities.loanStatus import LoanStatus
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/loans/status-loan", tags=["status-loan"])
logger = getLogger(__name__)

def getLoanStatusApplication(db: Session = Depends(getDb)) -> ILoanStatusApplication:
    repository = LoanStatusRepository(db)
    return LoanStatusApplication(repository)

def LoanStatusToDict(item: LoanStatus) -> dict:
    return {
        "IdLoanStatus": item.IdLoanStatus,
        "nameLoanStatus": item.nameLoanStatus,
    }

def LoanStatussToDict(items: List[LoanStatus]) -> list[dict]:
    return [LoanStatusToDict(item) for item in items]

@router.get("/", response_model=apiResponse)
def getAllLoanStatuss(service: ILoanStatusApplication = Depends(getLoanStatusApplication)):
    try:
        logger.info("Consultando estados")
        data = service.getAll()
        result = LoanStatussToDict(data)

        if not result:
            logger.info("No existen estados registrados.")
            return apiResponse(isSuccess=False, Message="No existen estados registrados.", result=[])

        logger.info("Estados obtenidos correctamente | total=%s", len(result))
        return apiResponse(isSuccess=True, Message="Estados obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo los estados.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los estados.")

@router.get("/{IdLoanStatus}", response_model=apiResponse)
def getLoanStatusById(IdLoanStatus: int, service: ILoanStatusApplication = Depends(getLoanStatusApplication)):
    try:
        logger.info("Consultando estados | IdLoanStatus=%s", IdLoanStatus)
        data = service.getById(IdLoanStatus)
        logger.info("Estado obtenido correctamente | IdLoanStatus=%s", IdLoanStatus)
        return apiResponse(isSuccess=True, Message="Estado obtenido correctamente.", result=LoanStatusToDict(data))

    except ValueError as e:
        logger.warning("Estado no encontrado | IdLoanStatus=%s | error=%s", IdLoanStatus, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo el estado | IdLoanStatus=%s", IdLoanStatus)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el estado.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createLoanStatus(loanStatusData: dict, service: ILoanStatusApplication = Depends(getLoanStatusApplication)):
    try:
        logger.info("Creando estado | nameLoanStatus=%s | ", loanStatusData.get("nameLoanStatus"))
        entity = LoanStatus(nameLoanStatus=loanStatusData.get("nameLoanStatus") or "",)
        data = service.create(entity)
        logger.info("Estado creado correctamente | IdLoanStatus=%s | nameLoanStatus=%s", getattr(data, "IdLoanStatus", None), getattr(data, "nameLoanStatus", None))
        return apiResponse(isSuccess=True, Message="Estado creado correctamente.", result=LoanStatusToDict(data))

    except ValueError as e:
        logger.warning("Validación creando estado | nameLoanStatus=%s | error=%s", loanStatusData.get("nameLoanStatus"), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando estado | nameLoanStatus=%s", loanStatusData.get("nameLoanStatus"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el estado.")

@router.put("/{IdLoanStatus}", response_model=apiResponse)
def updateLoanStatus(IdLoanStatus: int, loanStatusData: dict, service: ILoanStatusApplication = Depends(getLoanStatusApplication)):
    try:
        logger.info("Actualizando estado | IdLoanStatus=%s | nameLoanStatus=%s | ", IdLoanStatus, loanStatusData.get("nameLoanStatus"),)
        entity = LoanStatus(nameLoanStatus=loanStatusData.get("nameLoanStatus"),)
        data = service.update(IdLoanStatus, entity)
        logger.info("Estado actualizado correctamente | IdLoanStatus=%s", IdLoanStatus)
        return apiResponse(isSuccess=True, Message="Estado actualizado correctamente.", result=LoanStatusToDict(data))

    except ValueError as e:
        message = str(e)

        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        logger.warning("Validación actualizando estado | IdLoanStatus=%s | status=%s | error=%s", IdLoanStatus, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando estado | IdLoanStatus=%s", IdLoanStatus)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el estado.")

@router.delete("/{IdLoanStatus}", response_model=apiResponse)
def deleteLoanStatus(IdLoanStatus: int, service: ILoanStatusApplication = Depends(getLoanStatusApplication)):
    try:
        logger.info("Eliminando estado | IdLoanStatus=%s", IdLoanStatus)
        service.delete(IdLoanStatus)
        logger.info("Estado eliminado correctamente | IdLoanStatus=%s", IdLoanStatus)
        return apiResponse(isSuccess=True, Message="Estado eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Estado no encontrado al eliminar | IdLoanStatus=%s | error=%s", IdLoanStatus, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando estado | IdLoanStatus=%s", IdLoanStatus)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el estado.")
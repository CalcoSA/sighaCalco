from app.infrastructure.repositories.DiagnosisRepository import DiagnosisRepository
from app.application.interfaces.IDiagnosisApplication import IDiagnosisApplication
from app.application.services.DiagnosisApplication import DiagnosisApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.entities.diagnosis import Diagnosis
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/diagnosis", tags=["diagnosis"])
logger = getLogger(__name__)

def getDiagnosisApplication(db: Session = Depends(getDb)) -> IDiagnosisApplication:
    repository = DiagnosisRepository(db)
    return DiagnosisApplication(repository)

def diagnosisToDict(item: Diagnosis) -> dict:
    return {
        "IdDiagnosis": item.IdDiagnosis,
        "nameDiagnosis": item.nameDiagnosis,
        "codeDiagnosis": item.codeDiagnosis,
    }

def paginatedDiagnosisToDict(data) -> dict:
    return {
        "items": [diagnosisToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllDiagnosiss(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IDiagnosisApplication = Depends(getDiagnosisApplication)):
    try:
        logger.info("Consultando diagnósticos | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedDiagnosisToDict(data)

        if not data.items:
            logger.info("No existen diagnósticos registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen diagnósticos registrados.", result=result)
        
        logger.info("Diagnósticos obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="Diagnósticos obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo diagnósticos.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los diagnósticos.")

@router.get("/{IdDiagnosis}", response_model=apiResponse)
def getDiagnosisById(IdDiagnosis: int, service: IDiagnosisApplication = Depends(getDiagnosisApplication)):
    try:
        logger.info("Consultando diagnóstico | IdDiagnosis=%s", IdDiagnosis)
        data = service.getById(IdDiagnosis)
        logger.info("Diagnóstico obtenido correctamente | IdDiagnosis=%s", IdDiagnosis)
        return apiResponse(isSuccess=True, Message="Diagnóstico obtenido correctamente.", result=diagnosisToDict(data))

    except ValueError as e:
        logger.warning("Diagnóstico no encontrado | IdDiagnosis=%s | error=%s", IdDiagnosis, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo diagnóstico | IdDiagnosis=%s", IdDiagnosis)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el diagnóstico.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createDiagnosis(diagnosisData: dict, service: IDiagnosisApplication = Depends(getDiagnosisApplication)):
    try:
        logger.info("Creando diagnóstico | nameDiagnosis=%s | codeDiagnosis=%s", getattr(diagnosisData, "nameDiagnosis", None), getattr(diagnosisData, "codeDiagnosis", None))
        entity = Diagnosis(IdDiagnosis=diagnosisData.get("IdDiagnosis"), nameDiagnosis=diagnosisData.get("nameDiagnosis"), codeDiagnosis=diagnosisData.get("codeDiagnosis"))
        data = service.create(entity)
        logger.info("Diagnóstico creado correctamente | IdDiagnosis=%s | nameDiagnosis=%s", getattr(data, "IdDiagnosis", None), getattr(data, "nameDiagnosis", None))
        return apiResponse(isSuccess=True, Message="Diagnóstico creado correctamente.", result=diagnosisToDict(data))

    except ValueError as e:
        logger.warning("Validación creando diagnóstico | nameDiagnosis=%s | error=%s", getattr(diagnosisData, "nameDiagnosis", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando diagnóstico | nameDiagnosis=%s | codeDiagnosis=%s", getattr(diagnosisData, "nameDiagnosis", None), getattr(diagnosisData, "codeDiagnosis", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el diagnóstico.")

@router.put("/{IdDiagnosis}", response_model=apiResponse)
def updateDiagnosis(IdDiagnosis: int, diagnosisData: dict, service: IDiagnosisApplication = Depends(getDiagnosisApplication)):
    try:
        logger.info("Actualizando diagnóstico | IdDiagnosis=%s | nameDiagnosis=%s | codeDiagnosis=%s", IdDiagnosis, getattr(diagnosisData, "nameDiagnosis", None), getattr(diagnosisData, "codeDiagnosis", None))
        entity = Diagnosis(IdDiagnosis=diagnosisData.get("IdDiagnosis"), nameDiagnosis=diagnosisData.get("nameDiagnosis"), codeDiagnosis=diagnosisData.get("codeDiagnosis"))
        data = service.update(IdDiagnosis, entity)
        logger.info("Diagnóstico actualizado correctamente | IdDiagnosis=%s", IdDiagnosis)
        return apiResponse(isSuccess=True, Message="Diagnóstico actualizado correctamente.", result=diagnosisToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando diagnóstico | IdDiagnosis=%s | status=%s | error=%s", IdDiagnosis, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando diagnóstico | IdDiagnosis=%s", IdDiagnosis)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el diagnóstico.")

@router.delete("/{IdDiagnosis}", response_model=apiResponse)
def deleteDiagnosis(IdDiagnosis: int, service: IDiagnosisApplication = Depends(getDiagnosisApplication)):
    try:
        logger.info("Eliminando Diagnóstico | IdDiagnosis=%s", IdDiagnosis)
        service.delete(IdDiagnosis)
        logger.info("Diagnóstico eliminado correctamente | IdDiagnosis=%s", IdDiagnosis)
        return apiResponse(isSuccess=True, Message="Diagnóstico eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Diagnóstico no encontrado al eliminar | IdDiagnosis=%s | error=%s", IdDiagnosis, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando diagnóstico | IdDiagnosis=%s", IdDiagnosis)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el diagnóstico.")
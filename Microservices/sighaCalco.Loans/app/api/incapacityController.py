from app.infrastructure.repositories.IncapacityRepository import IncapacityRepository
from app.application.interfaces.IIncapacityApplication import IIncapacityApplication
from app.application.services.IncapacityApplication import IncapacityApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.entities.incapacity import Incapacity
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/incapacity", tags=["incapacity"])
logger = getLogger(__name__)

def getIncapacityApplication(db: Session = Depends(getDb)) -> IIncapacityApplication:
    repository = IncapacityRepository(db)
    return IncapacityApplication(repository)

def incapacityToDict(item: Incapacity) -> dict:
    return {
        "IdIncapacity": item.IdIncapacity,
        "nameIncapacity": item.nameIncapacity,
        "codeIncapacity": item.codeIncapacity,
    }

def paginatedIncapacityToDict(data) -> dict:
    return {
        "items": [incapacityToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllIncapacitys(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IIncapacityApplication = Depends(getIncapacityApplication)):
    try:
        logger.info("Consultando tipo de incapacidades | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedIncapacityToDict(data)

        if not data.items:
            logger.info("No existen tipo de incapacidades registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen Tipo de incapacidades registrados.", result=result)
        
        logger.info("Tipo de incapacidades obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="Tipo de incapacidades obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo tipo de incapacidades.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los tipo de incapacidades.")

@router.get("/{IdIncapacity}", response_model=apiResponse)
def getIncapacityById(IdIncapacity: int, service: IIncapacityApplication = Depends(getIncapacityApplication)):
    try:
        logger.info("Consultando tipo de incapacidad | IdIncapacity=%s", IdIncapacity)
        data = service.getById(IdIncapacity)
        logger.info("Tipo de incapacidad obtenido correctamente | IdIncapacity=%s", IdIncapacity)
        return apiResponse(isSuccess=True, Message="Tipo de incapacidad obtenido correctamente.", result=incapacityToDict(data))

    except ValueError as e:
        logger.warning("Tipo de incapacidad no encontrado | IdIncapacity=%s | error=%s", IdIncapacity, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo tipo de incapacidad | IdIncapacity=%s", IdIncapacity)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el tipo de incapacidad.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createIncapacity(incapacityData: dict, service: IIncapacityApplication = Depends(getIncapacityApplication)):
    try:
        logger.info("Creando tipo de incapacidad | nameIncapacity=%s | codeIncapacity=%s", getattr(incapacityData, "nameIncapacity", None), getattr(incapacityData, "codeIncapacity", None))
        entity = Incapacity(nameIncapacity=incapacityData.get("nameIncapacity"), codeIncapacity=incapacityData.get("codeIncapacity"))
        data = service.create(entity)
        logger.info("Tipo de incapacidad creado correctamente | IdIncapacity=%s | nameIncapacity=%s", getattr(data, "IdIncapacity", None), getattr(data, "nameIncapacity", None))
        return apiResponse(isSuccess=True, Message="Tipo de incapacidad creado correctamente.", result=incapacityToDict(data))

    except ValueError as e:
        logger.warning("Validación creando tipo de incapacidad | nameIncapacity=%s | error=%s", getattr(incapacityData, "nameIncapacity", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando tipo de incapacidad | nameIncapacity=%s | codeIncapacity=%s", getattr(incapacityData, "nameIncapacity", None), getattr(incapacityData, "codeIncapacity", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el tipo de incapacidad.")

@router.put("/{IdIncapacity}", response_model=apiResponse)
def updateIncapacity(IdIncapacity: int, incapacityData: dict, service: IIncapacityApplication = Depends(getIncapacityApplication)):
    try:
        logger.info("Actualizando tipo de incapacidad | IdIncapacity=%s | nameIncapacity=%s | codeIncapacity=%s", IdIncapacity, getattr(incapacityData, "nameIncapacity", None), getattr(incapacityData, "codeIncapacity", None))
        entity = Incapacity(nameIncapacity=incapacityData.get("nameIncapacity"), codeIncapacity=incapacityData.get("codeIncapacity"))
        data = service.update(IdIncapacity, entity)
        logger.info("Tipo de incapacidad actualizado correctamente | IdIncapacity=%s", IdIncapacity)
        return apiResponse(isSuccess=True, Message="Tipo de incapacidad actualizado correctamente.", result=incapacityToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando tipo de incapacidad | IdIncapacity=%s | status=%s | error=%s", IdIncapacity, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando tipo de incapacidad | IdIncapacity=%s", IdIncapacity)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el tipo de incapacidad.")

@router.delete("/{IdIncapacity}", response_model=apiResponse)
def deleteIncapacity(IdIncapacity: int, service: IIncapacityApplication = Depends(getIncapacityApplication)):
    try:
        logger.info("Eliminando tipo de incapacidad | IdIncapacity=%s", IdIncapacity)
        service.delete(IdIncapacity)
        logger.info("Tipo de incapacidad eliminado correctamente | IdIncapacity=%s", IdIncapacity)
        return apiResponse(isSuccess=True, Message="Tipo de incapacidad eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Tipo de incapacidad no encontrado al eliminar | IdIncapacity=%s | error=%s", IdIncapacity, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando tipo de incapacidad | IdIncapacity=%s", IdIncapacity)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el tipo de incapacidad.")
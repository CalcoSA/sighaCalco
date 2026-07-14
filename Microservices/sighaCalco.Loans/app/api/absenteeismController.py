from app.infrastructure.repositories.AbsenteeismRepository import AbsenteeismRepository
from app.application.interfaces.IAbsenteeismApplication import IAbsenteeismApplication
from app.application.services.AbsenteeismApplication import AbsenteeismApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.entities.absenteeism import Absenteeism
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/absenteeism", tags=["absenteeism"])
logger = getLogger(__name__)

def getAbsenteeismApplication(db: Session = Depends(getDb)) -> IAbsenteeismApplication:
    repository = AbsenteeismRepository(db)
    return AbsenteeismApplication(repository)

def absenteeismToDict(item: Absenteeism) -> dict:
    return {
        "IdAbsenteeism": item.IdAbsenteeism,
        "nameAbsenteeism": item.nameAbsenteeism,
        "codeAbsenteeism": item.codeAbsenteeism,
    }

def paginatedAbsenteeismToDict(data) -> dict:
    return {
        "items": [absenteeismToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllAbsenteeisms(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IAbsenteeismApplication = Depends(getAbsenteeismApplication)):
    try:
        logger.info("Consultando ausentismos | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedAbsenteeismToDict(data)

        if not data.items:
            logger.info("No existen ausentismos registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen ausentismos registrados.", result=result)
        
        logger.info("Ausentismos obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="Ausentismos obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo ausentismos.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los ausentismos.")

@router.get("/{IdAbsenteeism}", response_model=apiResponse)
def getAbsenteeismById(IdAbsenteeism: int, service: IAbsenteeismApplication = Depends(getAbsenteeismApplication)):
    try:
        logger.info("Consultando ausentismo | IdAbsenteeism=%s", IdAbsenteeism)
        data = service.getById(IdAbsenteeism)
        logger.info("Ausentismo obtenido correctamente | IdAbsenteeism=%s", IdAbsenteeism)
        return apiResponse(isSuccess=True, Message="Ausentismo obtenido correctamente.", result=absenteeismToDict(data))

    except ValueError as e:
        logger.warning("Ausentismo no encontrado | IdAbsenteeism=%s | error=%s", IdAbsenteeism, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo ausentismo | IdAbsenteeism=%s", IdAbsenteeism)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el ausentismo.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createAbsenteeism(absenteeismData: dict, service: IAbsenteeismApplication = Depends(getAbsenteeismApplication)):
    try:
        logger.info("Creando ausentismo | nameAbsenteeism=%s | codeAbsenteeism=%s", getattr(absenteeismData, "nameAbsenteeism", None), getattr(absenteeismData, "codeAbsenteeism", None))
        entity = Absenteeism(nameAbsenteeism=absenteeismData.get("nameAbsenteeism"), codeAbsenteeism=absenteeismData.get("codeAbsenteeism"))
        data = service.create(entity)
        logger.info("Ausentismo creado correctamente | IdAbsenteeism=%s | nameAbsenteeism=%s", getattr(data, "IdAbsenteeism", None), getattr(data, "nameAbsenteeism", None))
        return apiResponse(isSuccess=True, Message="Ausentismo creado correctamente.", result=absenteeismToDict(data))

    except ValueError as e:
        logger.warning("Validación creando ausentismo | nameAbsenteeism=%s | error=%s", getattr(absenteeismData, "nameAbsenteeism", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando ausentismo | nameAbsenteeism=%s | codeAbsenteeism=%s", getattr(absenteeismData, "nameAbsenteeism", None), getattr(absenteeismData, "codeAbsenteeism", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el ausentismo.")

@router.put("/{IdAbsenteeism}", response_model=apiResponse)
def updateAbsenteeism(IdAbsenteeism: int, absenteeismData: dict, service: IAbsenteeismApplication = Depends(getAbsenteeismApplication)):
    try:
        logger.info("Actualizando ausentismo | IdAbsenteeism=%s | nameAbsenteeism=%s | codeAbsenteeism=%s", IdAbsenteeism, getattr(absenteeismData, "nameAbsenteeism", None), getattr(absenteeismData, "codeAbsenteeism", None))
        entity = Absenteeism(nameAbsenteeism=absenteeismData.get("nameAbsenteeism"), codeAbsenteeism=absenteeismData.get("codeAbsenteeism"))
        data = service.update(IdAbsenteeism, entity)
        logger.info("Ausentismo actualizado correctamente | IdAbsenteeism=%s", IdAbsenteeism)
        return apiResponse(isSuccess=True, Message="Ausentismo actualizado correctamente.", result=absenteeismToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando ausentismo | IdAbsenteeism=%s | status=%s | error=%s", IdAbsenteeism, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando ausentismo | IdAbsenteeism=%s", IdAbsenteeism)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el ausentismo.")

@router.delete("/{IdAbsenteeism}", response_model=apiResponse)
def deleteAbsenteeism(IdAbsenteeism: int, service: IAbsenteeismApplication = Depends(getAbsenteeismApplication)):
    try:
        logger.info("Eliminando ausentismo | IdAbsenteeism=%s", IdAbsenteeism)
        service.delete(IdAbsenteeism)
        logger.info("Ausentismo eliminado correctamente | IdAbsenteeism=%s", IdAbsenteeism)
        return apiResponse(isSuccess=True, Message="Ausentismo eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Ausentismo no encontrado al eliminar | IdAbsenteeism=%s | error=%s", IdAbsenteeism, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando ausentismo | IdAbsenteeism=%s", IdAbsenteeism)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el ausentismo.")
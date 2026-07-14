from app.infrastructure.repositories.DescCen3Repository import DescCen3Repository
from app.application.interfaces.IDescCen3Application import IDescCen3Application
from app.application.services.DescCen3Application import DescCen3Application
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.domain.entities.descCen3 import DescCen3
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/descCen3", tags=["descCen3"])
logger = getLogger(__name__)

def getDescCen3Application(db: Session = Depends(getDb)) -> IDescCen3Application:
    repository = DescCen3Repository(db)
    return DescCen3Application(repository)

def descCen3ToDict(item: DescCen3) -> dict:
    return {
        "IdDescCen3": item.IdDescCen3,
        "nameDescCen3": item.nameDescCen3,
        "codeDescCen3": item.codeDescCen3,
    }

def paginatedDescCen3ToDict(data) -> dict:
    return {
        "items": [descCen3ToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllDescCen3s(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IDescCen3Application = Depends(getDescCen3Application)):
    try:
        logger.info("Consultando descCen3s | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedDescCen3ToDict(data)

        if not data.items:
            logger.info("No existen descCen3s registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen descCen3s registrados.", result=result)
        
        logger.info("DescCen3s obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="DescCen3s obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo descCen3s.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los descCen3s.")

@router.get("/{IdDescCen3}", response_model=apiResponse)
def getDescCen3ById(IdDescCen3: int, service: IDescCen3Application = Depends(getDescCen3Application)):
    try:
        logger.info("Consultando descCen3 | IdDescCen3=%s", IdDescCen3)
        data = service.getById(IdDescCen3)
        logger.info("DescCen3 obtenido correctamente | IdDescCen3=%s", IdDescCen3)
        return apiResponse(isSuccess=True, Message="DescCen3 obtenido correctamente.", result=descCen3ToDict(data))

    except ValueError as e:
        logger.warning("DescCen3 no encontrado | IdDescCen3=%s | error=%s", IdDescCen3, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo descCen3 | IdDescCen3=%s", IdDescCen3)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el descCen3.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createDescCen3(descCen3Data: dict, service: IDescCen3Application = Depends(getDescCen3Application)):
    try:
        logger.info("Creando descCen3 | nameDescCen3=%s | codeDescCen3=%s", getattr(descCen3Data, "nameDescCen3", None), getattr(descCen3Data, "codeDescCen3", None))
        entity = DescCen3(nameDescCen3=descCen3Data.get("nameDescCen3"), codeDescCen3=descCen3Data.get("codeDescCen3"))
        data = service.create(entity)
        logger.info("DescCen3 creado correctamente | IdDescCen3=%s | nameDescCen3=%s", getattr(data, "IdDescCen3", None), getattr(data, "nameDescCen3", None))
        return apiResponse(isSuccess=True, Message="DescCen3 creado correctamente.", result=descCen3ToDict(data))

    except ValueError as e:
        logger.warning("Validación creando descCen3 | nameDescCen3=%s | error=%s", getattr(descCen3Data, "nameDescCen3", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando descCen3 | nameDescCen3=%s | codeDescCen3=%s", getattr(descCen3Data, "nameDescCen3", None), getattr(descCen3Data, "codeDescCen3", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el descCen3.")

@router.put("/{IdDescCen3}", response_model=apiResponse)
def updateDescCen3(IdDescCen3: int, descCen3Data: dict, service: IDescCen3Application = Depends(getDescCen3Application)):
    try:
        logger.info("Actualizando descCen3 | IdDescCen3=%s | nameDescCen3=%s | codeDescCen3=%s", IdDescCen3, getattr(descCen3Data, "nameDescCen3", None), getattr(descCen3Data, "codeDescCen3", None))
        entity = DescCen3(nameDescCen3=descCen3Data.get("nameDescCen3"), codeDescCen3=descCen3Data.get("codeDescCen3"))
        data = service.update(IdDescCen3, entity)
        logger.info("DescCen3 actualizado correctamente | IdDescCen3=%s", IdDescCen3)
        return apiResponse(isSuccess=True, Message="DescCen3 actualizado correctamente.", result=descCen3ToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando descCen3 | IdDescCen3=%s | status=%s | error=%s", IdDescCen3, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando descCen3 | IdDescCen3=%s", IdDescCen3)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el descCen3.")

@router.delete("/{IdDescCen3}", response_model=apiResponse)
def deleteDescCen3(IdDescCen3: int, service: IDescCen3Application = Depends(getDescCen3Application)):
    try:
        logger.info("Eliminando descCen3 | IdDescCen3=%s", IdDescCen3)
        service.delete(IdDescCen3)
        logger.info("DescCen3 eliminado correctamente | IdDescCen3=%s", IdDescCen3)
        return apiResponse(isSuccess=True, Message="DescCen3 eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("DescCen3 no encontrado al eliminar | IdDescCen3=%s | error=%s", IdDescCen3, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando descCen3 | IdDescCen3=%s", IdDescCen3)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el descCen3.")
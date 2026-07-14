from app.infrastructure.repositories.DescCen1Repository import DescCen1Repository
from app.application.interfaces.IDescCen1Application import IDescCen1Application
from app.application.services.DescCen1Application import DescCen1Application
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.domain.entities.descCen1 import DescCen1
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/descCen1", tags=["descCen1"])
logger = getLogger(__name__)

def getDescCen1Application(db: Session = Depends(getDb)) -> IDescCen1Application:
    repository = DescCen1Repository(db)
    return DescCen1Application(repository)

def descCen1ToDict(item: DescCen1) -> dict:
    return {
        "IdDescCen1": item.IdDescCen1,
        "nameDescCen1": item.nameDescCen1,
        "codeDescCen1": item.codeDescCen1,
    }

def paginatedDescCen1ToDict(data) -> dict:
    return {
        "items": [descCen1ToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllDescCen1s(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IDescCen1Application = Depends(getDescCen1Application)):
    try:
        logger.info("Consultando descCen1s | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedDescCen1ToDict(data)

        if not data.items:
            logger.info("No existen descCen1s registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen descCen1s registrados.", result=result)
        
        logger.info("DescCen1s obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="DescCen1s obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo descCen1s.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los descCen1s.")

@router.get("/{IdDescCen1}", response_model=apiResponse)
def getDescCen1ById(IdDescCen1: int, service: IDescCen1Application = Depends(getDescCen1Application)):
    try:
        logger.info("Consultando descCen1 | IdDescCen1=%s", IdDescCen1)
        data = service.getById(IdDescCen1)
        logger.info("DescCen1 obtenido correctamente | IdDescCen1=%s", IdDescCen1)
        return apiResponse(isSuccess=True, Message="DescCen1 obtenido correctamente.", result=descCen1ToDict(data))

    except ValueError as e:
        logger.warning("DescCen1 no encontrado | IdDescCen1=%s | error=%s", IdDescCen1, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo descCen1 | IdDescCen1=%s", IdDescCen1)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el descCen1.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createDescCen1(descCen1Data: dict, service: IDescCen1Application = Depends(getDescCen1Application)):
    try:
        logger.info("Creando descCen1 | nameDescCen1=%s | codeDescCen1=%s", getattr(descCen1Data, "nameDescCen1", None), getattr(descCen1Data, "codeDescCen1", None))
        entity = DescCen1(nameDescCen1=descCen1Data.get("nameDescCen1"), codeDescCen1=descCen1Data.get("codeDescCen1"))
        data = service.create(entity)
        logger.info("DescCen1 creado correctamente | IdDescCen1=%s | nameDescCen1=%s", getattr(data, "IdDescCen1", None), getattr(data, "nameDescCen1", None))
        return apiResponse(isSuccess=True, Message="DescCen1 creado correctamente.", result=descCen1ToDict(data))

    except ValueError as e:
        logger.warning("Validación creando descCen1 | nameDescCen1=%s | error=%s", getattr(descCen1Data, "nameDescCen1", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando descCen1 | nameDescCen1=%s | codeDescCen1=%s", getattr(descCen1Data, "nameDescCen1", None), getattr(descCen1Data, "codeDescCen1", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el descCen1.")

@router.put("/{IdDescCen1}", response_model=apiResponse)
def updateDescCen1(IdDescCen1: int, descCen1Data: dict, service: IDescCen1Application = Depends(getDescCen1Application)):
    try:
        logger.info("Actualizando descCen1 | IdDescCen1=%s | nameDescCen1=%s | codeDescCen1=%s", IdDescCen1, getattr(descCen1Data, "nameDescCen1", None), getattr(descCen1Data, "codeDescCen1", None))
        entity = DescCen1(nameDescCen1=descCen1Data.get("nameDescCen1"), codeDescCen1=descCen1Data.get("codeDescCen1"))
        data = service.update(IdDescCen1, entity)
        logger.info("DescCen1 actualizado correctamente | IdDescCen1=%s", IdDescCen1)
        return apiResponse(isSuccess=True, Message="DescCen1 actualizado correctamente.", result=descCen1ToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando descCen1 | IdDescCen1=%s | status=%s | error=%s", IdDescCen1, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando descCen1 | IdDescCen1=%s", IdDescCen1)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el descCen1.")

@router.delete("/{IdDescCen1}", response_model=apiResponse)
def deleteDescCen1(IdDescCen1: int, service: IDescCen1Application = Depends(getDescCen1Application)):
    try:
        logger.info("Eliminando descCen1 | IdDescCen1=%s", IdDescCen1)
        service.delete(IdDescCen1)
        logger.info("DescCen1 eliminado correctamente | IdDescCen1=%s", IdDescCen1)
        return apiResponse(isSuccess=True, Message="DescCen1 eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("DescCen1 no encontrado al eliminar | IdDescCen1=%s | error=%s", IdDescCen1, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando descCen1 | IdDescCen1=%s", IdDescCen1)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el descCen1.")
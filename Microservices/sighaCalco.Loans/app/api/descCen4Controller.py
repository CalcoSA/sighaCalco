from app.infrastructure.repositories.DescCen4Repository import DescCen4Repository
from app.application.interfaces.IDescCen4Application import IDescCen4Application
from app.application.services.DescCen4Application import DescCen4Application
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.domain.entities.descCen4 import DescCen4
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/descCen4", tags=["descCen4"])
logger = getLogger(__name__)

def getDescCen4Application(db: Session = Depends(getDb)) -> IDescCen4Application:
    repository = DescCen4Repository(db)
    return DescCen4Application(repository)

def descCen4ToDict(item: DescCen4) -> dict:
    return {
        "IdDescCen4": item.IdDescCen4,
        "nameDescCen4": item.nameDescCen4,
        "codeDescCen4": item.codeDescCen4,
    }

def paginatedDescCen4ToDict(data) -> dict:
    return {
        "items": [descCen4ToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllDescCen4s(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IDescCen4Application = Depends(getDescCen4Application)):
    try:
        logger.info("Consultando descCen4s | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedDescCen4ToDict(data)

        if not data.items:
            logger.info("No existen descCen4s registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen descCen4s registrados.", result=result)
        
        logger.info("DescCen4s obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="DescCen4s obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo descCen4s.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los descCen4s.")

@router.get("/{IdDescCen4}", response_model=apiResponse)
def getDescCen4ById(IdDescCen4: int, service: IDescCen4Application = Depends(getDescCen4Application)):
    try:
        logger.info("Consultando descCen4 | IdDescCen4=%s", IdDescCen4)
        data = service.getById(IdDescCen4)
        logger.info("DescCen4 obtenido correctamente | IdDescCen4=%s", IdDescCen4)
        return apiResponse(isSuccess=True, Message="DescCen4 obtenido correctamente.", result=descCen4ToDict(data))

    except ValueError as e:
        logger.warning("DescCen4 no encontrado | IdDescCen4=%s | error=%s", IdDescCen4, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo descCen4 | IdDescCen4=%s", IdDescCen4)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el descCen4.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createDescCen4(descCen4Data: dict, service: IDescCen4Application = Depends(getDescCen4Application)):
    try:
        logger.info("Creando descCen4 | nameDescCen4=%s | codeDescCen4=%s", getattr(descCen4Data, "nameDescCen4", None), getattr(descCen4Data, "codeDescCen4", None))
        entity = DescCen4(nameDescCen4=descCen4Data.get("nameDescCen4"), codeDescCen4=descCen4Data.get("codeDescCen4"))
        data = service.create(entity)
        logger.info("DescCen4 creado correctamente | IdDescCen4=%s | nameDescCen4=%s", getattr(data, "IdDescCen4", None), getattr(data, "nameDescCen4", None))
        return apiResponse(isSuccess=True, Message="DescCen4 creado correctamente.", result=descCen4ToDict(data))

    except ValueError as e:
        logger.warning("Validación creando descCen4 | nameDescCen4=%s | error=%s", getattr(descCen4Data, "nameDescCen4", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando descCen4 | nameDescCen4=%s | codeDescCen4=%s", getattr(descCen4Data, "nameDescCen4", None), getattr(descCen4Data, "codeDescCen4", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el descCen4.")

@router.put("/{IdDescCen4}", response_model=apiResponse)
def updateDescCen4(IdDescCen4: int, descCen4Data: dict, service: IDescCen4Application = Depends(getDescCen4Application)):
    try:
        logger.info("Actualizando descCen4 | IdDescCen4=%s | nameDescCen4=%s | codeDescCen4=%s", IdDescCen4, getattr(descCen4Data, "nameDescCen4", None), getattr(descCen4Data, "codeDescCen4", None))
        entity = DescCen4(nameDescCen4=descCen4Data.get("nameDescCen4"), codeDescCen4=descCen4Data.get("codeDescCen4"))
        data = service.update(IdDescCen4, entity)
        logger.info("DescCen4 actualizado correctamente | IdDescCen4=%s", IdDescCen4)
        return apiResponse(isSuccess=True, Message="DescCen4 actualizado correctamente.", result=descCen4ToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando descCen4 | IdDescCen4=%s | status=%s | error=%s", IdDescCen4, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando descCen4 | IdDescCen4=%s", IdDescCen4)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el descCen4.")

@router.delete("/{IdDescCen4}", response_model=apiResponse)
def deleteDescCen4(IdDescCen4: int, service: IDescCen4Application = Depends(getDescCen4Application)):
    try:
        logger.info("Eliminando descCen4 | IdDescCen4=%s", IdDescCen4)
        service.delete(IdDescCen4)
        logger.info("DescCen4 eliminado correctamente | IdDescCen4=%s", IdDescCen4)
        return apiResponse(isSuccess=True, Message="DescCen4 eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("DescCen4 no encontrado al eliminar | IdDescCen4=%s | error=%s", IdDescCen4, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando descCen4 | IdDescCen4=%s", IdDescCen4)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el descCen4.")
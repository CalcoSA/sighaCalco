from app.infrastructure.repositories.DescCen2Repository import DescCen2Repository
from app.application.interfaces.IDescCen2Application import IDescCen2Application
from app.application.services.DescCen2Application import DescCen2Application
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.domain.entities.descCen2 import DescCen2
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/descCen2", tags=["descCen2"])
logger = getLogger(__name__)

def getDescCen2Application(db: Session = Depends(getDb)) -> IDescCen2Application:
    repository = DescCen2Repository(db)
    return DescCen2Application(repository)

def descCen2ToDict(item: DescCen2) -> dict:
    return {
        "IdDescCen2": item.IdDescCen2,
        "nameDescCen2": item.nameDescCen2,
        "codeDescCen2": item.codeDescCen2,
    }

def paginatedDescCen2ToDict(data) -> dict:
    return {
        "items": [descCen2ToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllDescCen2s(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IDescCen2Application = Depends(getDescCen2Application)):
    try:
        logger.info("Consultando descCen2s | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedDescCen2ToDict(data)

        if not data.items:
            logger.info("No existen descCen2s registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen descCen2s registrados.", result=result)
        
        logger.info("DescCen2s obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="DescCen2s obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo descCen2s.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los descCen2s.")

@router.get("/{IdDescCen2}", response_model=apiResponse)
def getDescCen2ById(IdDescCen2: int, service: IDescCen2Application = Depends(getDescCen2Application)):
    try:
        logger.info("Consultando descCen2 | IdDescCen2=%s", IdDescCen2)
        data = service.getById(IdDescCen2)
        logger.info("DescCen2 obtenido correctamente | IdDescCen2=%s", IdDescCen2)
        return apiResponse(isSuccess=True, Message="DescCen2 obtenido correctamente.", result=descCen2ToDict(data))

    except ValueError as e:
        logger.warning("DescCen2 no encontrado | IdDescCen2=%s | error=%s", IdDescCen2, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo descCen2 | IdDescCen2=%s", IdDescCen2)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el descCen2.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createDescCen2(descCen2Data: dict, service: IDescCen2Application = Depends(getDescCen2Application)):
    try:
        logger.info("Creando descCen2 | nameDescCen2=%s | codeDescCen2=%s", getattr(descCen2Data, "nameDescCen2", None), getattr(descCen2Data, "codeDescCen2", None))
        entity = DescCen2(nameDescCen2=descCen2Data.get("nameDescCen2"), codeDescCen2=descCen2Data.get("codeDescCen2"))
        data = service.create(entity)
        logger.info("DescCen2 creado correctamente | IdDescCen2=%s | nameDescCen2=%s", getattr(data, "IdDescCen2", None), getattr(data, "nameDescCen2", None))
        return apiResponse(isSuccess=True, Message="DescCen2 creado correctamente.", result=descCen2ToDict(data))

    except ValueError as e:
        logger.warning("Validación creando descCen2 | nameDescCen2=%s | error=%s", getattr(descCen2Data, "nameDescCen2", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando descCen2 | nameDescCen2=%s | codeDescCen2=%s", getattr(descCen2Data, "nameDescCen2", None), getattr(descCen2Data, "codeDescCen2", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el descCen2.")

@router.put("/{IdDescCen2}", response_model=apiResponse)
def updateDescCen2(IdDescCen2: int, descCen2Data: dict, service: IDescCen2Application = Depends(getDescCen2Application)):
    try:
        logger.info("Actualizando descCen2 | IdDescCen2=%s | nameDescCen2=%s | codeDescCen2=%s", IdDescCen2, getattr(descCen2Data, "nameDescCen2", None), getattr(descCen2Data, "codeDescCen2", None))
        entity = DescCen2(nameDescCen2=descCen2Data.get("nameDescCen2"), codeDescCen2=descCen2Data.get("codeDescCen2"))
        data = service.update(IdDescCen2, entity)
        logger.info("DescCen2 actualizado correctamente | IdDescCen2=%s", IdDescCen2)
        return apiResponse(isSuccess=True, Message="DescCen2 actualizado correctamente.", result=descCen2ToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando descCen2 | IdDescCen2=%s | status=%s | error=%s", IdDescCen2, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando descCen2 | IdDescCen2=%s", IdDescCen2)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el descCen2.")

@router.delete("/{IdDescCen2}", response_model=apiResponse)
def deleteDescCen2(IdDescCen2: int, service: IDescCen2Application = Depends(getDescCen2Application)):
    try:
        logger.info("Eliminando descCen2 | IdDescCen2=%s", IdDescCen2)
        service.delete(IdDescCen2)
        logger.info("DescCen2 eliminado correctamente | IdDescCen2=%s", IdDescCen2)
        return apiResponse(isSuccess=True, Message="DescCen2 eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("DescCen2 no encontrado al eliminar | IdDescCen2=%s | error=%s", IdDescCen2, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando descCen2 | IdDescCen2=%s", IdDescCen2)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el descCen2.")
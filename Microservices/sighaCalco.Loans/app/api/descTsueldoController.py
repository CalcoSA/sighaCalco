from app.infrastructure.repositories.DescTsueldoRepository import DescTsueldoRepository
from app.application.interfaces.IDescTsueldoApplication import IDescTsueldoApplication
from app.application.services.DescTsueldoApplication import DescTsueldoApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.entities.descTsueldo import DescTsueldo
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/descTsueldo", tags=["descTsueldo"])
logger = getLogger(__name__)

def getDescTsueldoApplication(db: Session = Depends(getDb)) -> IDescTsueldoApplication:
    repository = DescTsueldoRepository(db)
    return DescTsueldoApplication(repository)

def descTsueldoToDict(item: DescTsueldo) -> dict:
    return {
        "IdDescTsueldo": item.IdDescTsueldo,
        "nameDescTsueldo": item.nameDescTsueldo,
        "codeDescTsueldo": item.codeDescTsueldo,
    }

def paginatedDescTsueldoToDict(data) -> dict:
    return {
        "items": [descTsueldoToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllDescTsueldos(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IDescTsueldoApplication = Depends(getDescTsueldoApplication)):
    try:
        logger.info("Consultando descTsueldos | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedDescTsueldoToDict(data)

        if not data.items:
            logger.info("No existen descTsueldos registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen descTsueldos registrados.", result=result)
        
        logger.info("DescTsueldos obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="DescTsueldos obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo descTsueldos.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los descTsueldos.")

@router.get("/{IdDescTsueldo}", response_model=apiResponse)
def getDescTsueldoById(IdDescTsueldo: int, service: IDescTsueldoApplication = Depends(getDescTsueldoApplication)):
    try:
        logger.info("Consultando descTsueldo | IdDescTsueldo=%s", IdDescTsueldo)
        data = service.getById(IdDescTsueldo)
        logger.info("DescTsueldo obtenido correctamente | IdDescTsueldo=%s", IdDescTsueldo)
        return apiResponse(isSuccess=True, Message="DescTsueldo obtenido correctamente.", result=descTsueldoToDict(data))

    except ValueError as e:
        logger.warning("DescTsueldo no encontrado | IdDescTsueldo=%s | error=%s", IdDescTsueldo, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo descTsueldo | IdDescTsueldo=%s", IdDescTsueldo)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el descTsueldo.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createDescTsueldo(descTsueldoData: dict, service: IDescTsueldoApplication = Depends(getDescTsueldoApplication)):
    try:
        logger.info("Creando descTsueldo | nameDescTsueldo=%s | codeDescTsueldo=%s", getattr(descTsueldoData, "nameDescTsueldo", None), getattr(descTsueldoData, "codeDescTsueldo", None))
        entity = DescTsueldo(nameDescTsueldo=descTsueldoData.get("nameDescTsueldo"), codeDescTsueldo=descTsueldoData.get("codeDescTsueldo"))
        data = service.create(entity)
        logger.info("DescTsueldo creado correctamente | IdDescTsueldo=%s | nameDescTsueldo=%s", getattr(data, "IdDescTsueldo", None), getattr(data, "nameDescTsueldo", None))
        return apiResponse(isSuccess=True, Message="DescTsueldo creado correctamente.", result=descTsueldoToDict(data))

    except ValueError as e:
        logger.warning("Validación creando descTsueldo | nameDescTsueldo=%s | error=%s", getattr(descTsueldoData, "nameDescTsueldo", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando descTsueldo | nameDescTsueldo=%s | codeDescTsueldo=%s", getattr(descTsueldoData, "nameDescTsueldo", None), getattr(descTsueldoData, "codeDescTsueldo", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el descTsueldo.")

@router.put("/{IdDescTsueldo}", response_model=apiResponse)
def updateDescTsueldo(IdDescTsueldo: int, descTsueldoData: dict, service: IDescTsueldoApplication = Depends(getDescTsueldoApplication)):
    try:
        logger.info("Actualizando descTsueldo | IdDescTsueldo=%s | nameDescTsueldo=%s | codeDescTsueldo=%s", IdDescTsueldo, getattr(descTsueldoData, "nameDescTsueldo", None), getattr(descTsueldoData, "codeDescTsueldo", None))
        entity = DescTsueldo(nameDescTsueldo=descTsueldoData.get("nameDescTsueldo"), codeDescTsueldo=descTsueldoData.get("codeDescTsueldo"))
        data = service.update(IdDescTsueldo, entity)
        logger.info("DescTsueldo actualizado correctamente | IdDescTsueldo=%s", IdDescTsueldo)
        return apiResponse(isSuccess=True, Message="DescTsueldo actualizado correctamente.", result=descTsueldoToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando descTsueldo | IdDescTsueldo=%s | status=%s | error=%s", IdDescTsueldo, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando descTsueldo | IdDescTsueldo=%s", IdDescTsueldo)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el descTsueldo.")

@router.delete("/{IdDescTsueldo}", response_model=apiResponse)
def deleteDescTsueldo(IdDescTsueldo: int, service: IDescTsueldoApplication = Depends(getDescTsueldoApplication)):
    try:
        logger.info("Eliminando descTsueldo | IdDescTsueldo=%s", IdDescTsueldo)
        service.delete(IdDescTsueldo)
        logger.info("DescTsueldo eliminado correctamente | IdDescTsueldo=%s", IdDescTsueldo)
        return apiResponse(isSuccess=True, Message="DescTsueldo eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("DescTsueldo no encontrado al eliminar | IdDescTsueldo=%s | error=%s", IdDescTsueldo, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando descTsueldo | IdDescTsueldo=%s", IdDescTsueldo)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el descTsueldo.")
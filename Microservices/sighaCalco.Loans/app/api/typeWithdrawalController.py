from app.infrastructure.repositories.TypeWithdrawalRepository import TypeWithdrawalRepository
from app.application.interfaces.ITypeWithdrawalApplication import ITypeWithdrawalApplication
from app.application.services.TypeWithdrawalApplication import TypeWithdrawalApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.entities.typeWithdrawal import TypeWithdrawal
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/typeWithdrawal", tags=["typeWithdrawal"])
logger = getLogger(__name__)

def getTypeWithdrawalApplication(db: Session = Depends(getDb)) -> ITypeWithdrawalApplication:
    repository = TypeWithdrawalRepository(db)
    return TypeWithdrawalApplication(repository)

def typeWithdrawalToDict(item: TypeWithdrawal) -> dict:
    return {
        "IdTypeWithdrawal": item.IdTypeWithdrawal,
        "nameTypeWithdrawal": item.nameTypeWithdrawal,
        "codeTypeWithdrawal": item.codeTypeWithdrawal,
    }

def paginatedTypeWithdrawalToDict(data) -> dict:
    return {
        "items": [typeWithdrawalToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllTypeWithdrawals(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: ITypeWithdrawalApplication = Depends(getTypeWithdrawalApplication)):
    try:
        logger.info("Consultando tipos de retiro | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedTypeWithdrawalToDict(data)

        if not data.items:
            logger.info("No existen tipos de retiro registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen Tipos de retiro registrados.", result=result)
        
        logger.info("Tipos de retiro obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="Tipos de retiro obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo tipos de retiro.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los tipos de retiro.")

@router.get("/{IdTypeWithdrawal}", response_model=apiResponse)
def getTypeWithdrawalById(IdTypeWithdrawal: int, service: ITypeWithdrawalApplication = Depends(getTypeWithdrawalApplication)):
    try:
        logger.info("Consultando tipo de retiro | IdTypeWithdrawal=%s", IdTypeWithdrawal)
        data = service.getById(IdTypeWithdrawal)
        logger.info("Tipo de retiro obtenido correctamente | IdTypeWithdrawal=%s", IdTypeWithdrawal)
        return apiResponse(isSuccess=True, Message="Tipo de retiro obtenido correctamente.", result=typeWithdrawalToDict(data))

    except ValueError as e:
        logger.warning("Tipo de retiro no encontrado | IdTypeWithdrawal=%s | error=%s", IdTypeWithdrawal, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo tipo de retiro | IdTypeWithdrawal=%s", IdTypeWithdrawal)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el tipo de retiro.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createTypeWithdrawal(typeWithdrawalData: dict, service: ITypeWithdrawalApplication = Depends(getTypeWithdrawalApplication)):
    try:
        logger.info("Creando tipo de retiro | nameTypeWithdrawal=%s | codeTypeWithdrawal=%s", getattr(typeWithdrawalData, "nameTypeWithdrawal", None), getattr(typeWithdrawalData, "codeTypeWithdrawal", None))
        entity = TypeWithdrawal(nameTypeWithdrawal=typeWithdrawalData.get("nameTypeWithdrawal"), codeTypeWithdrawal=typeWithdrawalData.get("codeTypeWithdrawal"))
        data = service.create(entity)
        logger.info("Tipo de retiro creado correctamente | IdTypeWithdrawal=%s | nameTypeWithdrawal=%s", getattr(data, "IdTypeWithdrawal", None), getattr(data, "nameTypeWithdrawal", None))
        return apiResponse(isSuccess=True, Message="Tipo de retiro creado correctamente.", result=typeWithdrawalToDict(data))

    except ValueError as e:
        logger.warning("Validación creando tipo de retiro | nameTypeWithdrawal=%s | error=%s", getattr(typeWithdrawalData, "nameTypeWithdrawal", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando tipo de retiro | nameTypeWithdrawal=%s | codeTypeWithdrawal=%s", getattr(typeWithdrawalData, "nameTypeWithdrawal", None), getattr(typeWithdrawalData, "codeTypeWithdrawal", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el tipo de retiro.")

@router.put("/{IdTypeWithdrawal}", response_model=apiResponse)
def updateTypeWithdrawal(IdTypeWithdrawal: int, typeWithdrawalData: dict, service: ITypeWithdrawalApplication = Depends(getTypeWithdrawalApplication)):
    try:
        logger.info("Actualizando tipo de retiro | IdTypeWithdrawal=%s | nameTypeWithdrawal=%s | codeTypeWithdrawal=%s", IdTypeWithdrawal, getattr(typeWithdrawalData, "nameTypeWithdrawal", None), getattr(typeWithdrawalData, "codeTypeWithdrawal", None))
        entity = TypeWithdrawal(nameTypeWithdrawal=typeWithdrawalData.get("nameTypeWithdrawal"), codeTypeWithdrawal=typeWithdrawalData.get("codeTypeWithdrawal"))
        data = service.update(IdTypeWithdrawal, entity)
        logger.info("Tipo de retiro actualizado correctamente | IdTypeWithdrawal=%s", IdTypeWithdrawal)
        return apiResponse(isSuccess=True, Message="Tipo de retiro actualizado correctamente.", result=typeWithdrawalToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando tipo de retiro | IdTypeWithdrawal=%s | status=%s | error=%s", IdTypeWithdrawal, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando tipo de retiro | IdTypeWithdrawal=%s", IdTypeWithdrawal)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el tipo de retiro.")

@router.delete("/{IdTypeWithdrawal}", response_model=apiResponse)
def deleteTypeWithdrawal(IdTypeWithdrawal: int, service: ITypeWithdrawalApplication = Depends(getTypeWithdrawalApplication)):
    try:
        logger.info("Eliminando tipo de retiro | IdTypeWithdrawal=%s", IdTypeWithdrawal)
        service.delete(IdTypeWithdrawal)
        logger.info("Tipo de retiro eliminado correctamente | IdTypeWithdrawal=%s", IdTypeWithdrawal)
        return apiResponse(isSuccess=True, Message="Tipo de retiro eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Tipo de retiro no encontrado al eliminar | IdTypeWithdrawal=%s | error=%s", IdTypeWithdrawal, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando tipo de retiro | IdTypeWithdrawal=%s", IdTypeWithdrawal)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el tipo de retiro.")
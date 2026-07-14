from app.infrastructure.repositories.TypeBankAccountRepository import TypeBankAccountRepository
from app.application.interfaces.ITypeBankAccountApplication import ITypeBankAccountApplication
from app.application.services.TypeBankAccountApplication import TypeBankAccountApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.domain.entities.typeBankAccount import TypeBankAccount
from app.infrastructure.logging.loggerConfig import getLogger
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/typeBankAccount", tags=["typeBankAccount"])
logger = getLogger(__name__)

def getTypeBankAccountApplication(db: Session = Depends(getDb)) -> ITypeBankAccountApplication:
    repository = TypeBankAccountRepository(db)
    return TypeBankAccountApplication(repository)

def typeBankAccountToDict(item: TypeBankAccount) -> dict:
    return {
        "IdTypeBankAccount": item.IdTypeBankAccount,
        "nameTypeBankAccount": item.nameTypeBankAccount,
        "codeTypeBankAccount": item.codeTypeBankAccount,
    }

def paginatedTypeBankAccountToDict(data) -> dict:
    return {
        "items": [typeBankAccountToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllTypeBankAccounts(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: ITypeBankAccountApplication = Depends(getTypeBankAccountApplication)):
    try:
        logger.info("Consultando tipos de cuenta bancaria | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedTypeBankAccountToDict(data)

        if not data.items:
            logger.info("No existen tipos de cuenta bancaria registradas | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen tipos de cuenta bancaria registradas.", result=result)
        
        logger.info("Tipos de cuenta bancaria obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="Tipos de cuenta bancaria obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo tipos de cuenta bancaria.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los tipos de cuenta bancaria.")

@router.get("/{IdTypeBankAccount}", response_model=apiResponse)
def getTypeBankAccountById(IdTypeBankAccount: int, service: ITypeBankAccountApplication = Depends(getTypeBankAccountApplication)):
    try:
        logger.info("Consultando tipo de cuenta bancaria | IdTypeBankAccount=%s", IdTypeBankAccount)
        data = service.getById(IdTypeBankAccount)
        logger.info("Tipo de cuenta bancaria obtenido correctamente | IdTypeBankAccount=%s", IdTypeBankAccount)
        return apiResponse(isSuccess=True, Message="Tipo de cuenta bancaria obtenido correctamente.", result=typeBankAccountToDict(data))

    except ValueError as e:
        logger.warning("Tipo de cuenta bancaria no encontrado | IdTypeBankAccount=%s | error=%s", IdTypeBankAccount, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo tipo de cuenta bancaria | IdTypeBankAccount=%s", IdTypeBankAccount)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el tipo de cuenta bancaria.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createTypeBankAccount(typeBankAccountData: dict, service: ITypeBankAccountApplication = Depends(getTypeBankAccountApplication)):
    try:
        logger.info("Creando tipo de cuenta bancaria | nameTypeBankAccount=%s | codeTypeBankAccount=%s", getattr(typeBankAccountData, "nameTypeBankAccount", None), getattr(typeBankAccountData, "codeTypeBankAccount", None))
        entity = TypeBankAccount(nameTypeBankAccount=typeBankAccountData.get("nameTypeBankAccount"), codeTypeBankAccount=typeBankAccountData.get("codeTypeBankAccount"))
        data = service.create(entity)
        logger.info("Tipo de cuenta bancaria creado correctamente | IdTypeBankAccount=%s | nameTypeBankAccount=%s", getattr(data, "IdTypeBankAccount", None), getattr(data, "nameTypeBankAccount", None))
        return apiResponse(isSuccess=True, Message="Tipo de cuenta bancaria creado correctamente.", result=typeBankAccountToDict(data))

    except ValueError as e:
        logger.warning("Validación creando tipo de cuenta bancaria | nameTypeBankAccount=%s | error=%s", getattr(typeBankAccountData, "nameTypeBankAccount", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando tipo de cuenta bancaria | nameTypeBankAccount=%s | codeTypeBankAccount=%s", getattr(typeBankAccountData, "nameTypeBankAccount", None), getattr(typeBankAccountData, "codeTypeBankAccount", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el tipo de cuenta bancaria.")

@router.put("/{IdTypeBankAccount}", response_model=apiResponse)
def updateTypeBankAccount(IdTypeBankAccount: int, typeBankAccountData: dict, service: ITypeBankAccountApplication = Depends(getTypeBankAccountApplication)):
    try:
        logger.info("Actualizando tipo de cuenta bancaria | IdTypeBankAccount=%s | nameTypeBankAccount=%s | codeTypeBankAccount=%s", IdTypeBankAccount, getattr(typeBankAccountData, "nameTypeBankAccount", None), getattr(typeBankAccountData, "codeTypeBankAccount", None))
        entity = TypeBankAccount(nameTypeBankAccount=typeBankAccountData.get("nameTypeBankAccount"), codeTypeBankAccount=typeBankAccountData.get("codeTypeBankAccount"))
        data = service.update(IdTypeBankAccount, entity)
        logger.info("Tipo de cuenta bancaria actualizado correctamente | IdTypeBankAccount=%s", IdTypeBankAccount)
        return apiResponse(isSuccess=True, Message="Tipo de cuenta bancaria actualizado correctamente.", result=typeBankAccountToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando tipo de cuenta bancaria | IdTypeBankAccount=%s | status=%s | error=%s", IdTypeBankAccount, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando tipo de cuenta bancaria | IdTypeBankAccount=%s", IdTypeBankAccount)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el tipo de cuenta bancaria.")

@router.delete("/{IdTypeBankAccount}", response_model=apiResponse)
def deleteTypeBankAccount(IdTypeBankAccount: int, service: ITypeBankAccountApplication = Depends(getTypeBankAccountApplication)):
    try:
        logger.info("Eliminando tipo de cuenta bancaria | IdTypeBankAccount=%s", IdTypeBankAccount)
        service.delete(IdTypeBankAccount)
        logger.info("Tipo de cuenta bancaria eliminado correctamente | IdTypeBankAccount=%s", IdTypeBankAccount)
        return apiResponse(isSuccess=True, Message="Tipo de cuenta bancaria eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Tipo de cuenta bancaria no encontrado al eliminar | IdTypeBankAccount=%s | error=%s", IdTypeBankAccount, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando tipo de cuenta bancaria | IdTypeBankAccount=%s", IdTypeBankAccount)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el tipo de cuenta bancaria.")
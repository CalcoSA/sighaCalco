from app.infrastructure.repositories.BankRepository import BankRepository
from app.application.interfaces.IBankApplication import IBankApplication
from app.application.services.BankApplication import BankApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from app.domain.entities.bank import Bank
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/bank", tags=["bank"])
logger = getLogger(__name__)

def getBankApplication(db: Session = Depends(getDb)) -> IBankApplication:
    repository = BankRepository(db)
    return BankApplication(repository)

def bankToDict(item: Bank) -> dict:
    return {
        "IdBank": item.IdBank,
        "nameBank": item.nameBank,
        "codeBank": item.codeBank,
    }

def paginatedBankToDict(data) -> dict:
    return {
        "items": [bankToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllBanks(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IBankApplication = Depends(getBankApplication)):
    try:
        logger.info("Consultando bancos | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedBankToDict(data)

        if not data.items:
            logger.info("No existen bancos registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen bancos registrados.", result=result)
        
        logger.info("Bancos obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="Bancos obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo bancos.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los bancos.")

@router.get("/{IdBank}", response_model=apiResponse)
def getBankById(IdBank: int, service: IBankApplication = Depends(getBankApplication)):
    try:
        logger.info("Consultando banco | IdBank=%s", IdBank)
        data = service.getById(IdBank)
        logger.info("Banco obtenido correctamente | IdBank=%s", IdBank)
        return apiResponse(isSuccess=True, Message="Banco obtenido correctamente.", result=bankToDict(data))

    except ValueError as e:
        logger.warning("Banco no encontrado | IdBank=%s | error=%s", IdBank, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo Banco | IdBank=%s", IdBank)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el banco.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createBank(bankData: dict, service: IBankApplication = Depends(getBankApplication)):
    try:
        logger.info("Creando Banco | nameBank=%s | codeBank=%s", getattr(bankData, "nameBank", None), getattr(bankData, "codeBank", None))
        entity = Bank(nameBank=bankData.get("nameBank"), codeBank=bankData.get("codeBank"))
        data = service.create(entity)
        logger.info("Banco creado correctamente | IdBank=%s | nameBank=%s", getattr(data, "IdBank", None), getattr(data, "nameBank", None))
        return apiResponse(isSuccess=True, Message="Banco creado correctamente.", result=bankToDict(data))

    except ValueError as e:
        logger.warning("Validación creando Banco | nameBank=%s | error=%s", getattr(bankData, "nameBank", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando banco | nameBank=%s | codeBank=%s", getattr(bankData, "nameBank", None), getattr(bankData, "codeBank", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el banco.")

@router.put("/{IdBank}", response_model=apiResponse)
def updateBank(IdBank: int, bankData: dict, service: IBankApplication = Depends(getBankApplication)):
    try:
        logger.info("Actualizando Banco | IdBank=%s | nameBank=%s | codeBank=%s", IdBank, getattr(bankData, "nameBank", None), getattr(bankData, "codeBank", None))
        entity = Bank(nameBank=bankData.get("nameBank"), codeBank=bankData.get("codeBank"))
        data = service.update(IdBank, entity)
        logger.info("Banco actualizado correctamente | IdBank=%s", IdBank)
        return apiResponse(isSuccess=True, Message="Banco actualizado correctamente.", result=bankToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando Banco | IdBank=%s | status=%s | error=%s", IdBank, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando banco | IdBank=%s", IdBank)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el banco.")

@router.delete("/{IdBank}", response_model=apiResponse)
def deleteBank(IdBank: int, service: IBankApplication = Depends(getBankApplication)):
    try:
        logger.info("Eliminando banco | IdBank=%s", IdBank)
        service.delete(IdBank)
        logger.info("Banco eliminado correctamente | IdBank=%s", IdBank)
        return apiResponse(isSuccess=True, Message="Banco eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Banco no encontrado al eliminar | IdBank=%s | error=%s", IdBank, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando banco | IdBank=%s", IdBank)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el banco.")
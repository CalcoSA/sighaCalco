from app.infrastructure.repositories.PayrollSinergyRepository import PayrollSinergyRepository
from app.application.interfaces.IPayrollSinergyApplication import IPayrollSinergyApplication
from app.application.services.PayrollSinergyApplication import PayrollSinergyApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.entities.payrollSinergy import PayrollSinergy
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/loans/payrollSinergy", tags=["payrollSinergy"])
logger = getLogger(__name__)

def getPayrollSinergyApplication(db: Session = Depends(getDb)) -> IPayrollSinergyApplication:
    repository = PayrollSinergyRepository(db)
    return PayrollSinergyApplication(repository)

def payrollSinergyToDict(item: PayrollSinergy) -> dict:
    return {
        "IdPayrollSinergy": item.IdPayrollSinergy,
        "namePayrollSinergy": item.namePayrollSinergy,
        "codePayrollSinergy": item.codePayrollSinergy,
    }

def paginatedPayrollSinergyToDict(data) -> dict:
    return {
        "items": [payrollSinergyToDict(item) for item in data.items],
        "total": data.total,
        "page": data.page,
        "pageSize": data.pageSize,
        "totalPages": data.totalPages,
    }

@router.get("/", response_model=apiResponse)
def getAllPayrollSinergys(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), search: Optional[str] = Query(None), service: IPayrollSinergyApplication = Depends(getPayrollSinergyApplication)):
    try:
        logger.info("Consultando conceptos de nómina | page=%s | pageSize=%s | search=%s", page, pageSize, search)
        pagination = PaginationParams(page=page, pageSize=pageSize, search=search)
        data = service.getAll(pagination)
        result = paginatedPayrollSinergyToDict(data)

        if not data.items:
            logger.info("No existen conceptos de nómina registrados | page=%s | pageSize=%s | search=%s", page, pageSize, search)
            return apiResponse(isSuccess=False, Message="No existen conceptos de nómina registrados.", result=result)
        
        logger.info("Conceptos de nómina obtenidos correctamente | total=%s | page=%s", data.total, data.page)
        return apiResponse(isSuccess=True, Message="Conceptos de nómina obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo conceptos de nómina.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los conceptos de nómina.")
    
@router.get("/payroll", response_model=apiResponse)
def getAllPayroll(search: Optional[str] = Query(None), service: IPayrollSinergyApplication = Depends(getPayrollSinergyApplication)):
    try:
        logger.info("Consultando conceptos de nómina | search=%s", search)
        data = service.getAllPayroll(search)
        result = [payrollSinergyToDict(item) for item in data]

        if not result:
            logger.info("No existen conceptos de nómina registrados | search=%s", search)
            return apiResponse(isSuccess=False, Message="No existen conceptos de nómina registrados.", result=[])

        logger.info("Conceptos de nómina obtenidos correctamente | total=%s", len(result))
        return apiResponse(isSuccess=True, Message="Conceptos de nómina obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo conceptos de nómina.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los conceptos de nómina.")

@router.get("/{IdPayrollSinergy}", response_model=apiResponse)
def getPayrollSinergyById(IdPayrollSinergy: int, service: IPayrollSinergyApplication = Depends(getPayrollSinergyApplication)):
    try:
        logger.info("Consultando concepto de nómina | IdPayrollSinergy=%s", IdPayrollSinergy)
        data = service.getById(IdPayrollSinergy)
        logger.info("Concepto de nómina obtenido correctamente | IdPayrollSinergy=%s", IdPayrollSinergy)
        return apiResponse(isSuccess=True, Message="Concepto de nómina obtenido correctamente.", result=payrollSinergyToDict(data))

    except ValueError as e:
        logger.warning("Concepto de nómina no encontrado | IdPayrollSinergy=%s | error=%s", IdPayrollSinergy, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo concepto de nómina | IdPayrollSinergy=%s", IdPayrollSinergy)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el concepto de nómina.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createPayrollSinergy(payrollSinergyData: dict, service: IPayrollSinergyApplication = Depends(getPayrollSinergyApplication)):
    try:
        logger.info("Creando concepto de nómina | namePayrollSinergy=%s | codePayrollSinergy=%s", getattr(payrollSinergyData, "namePayrollSinergy", None), getattr(payrollSinergyData, "codePayrollSinergy", None))
        entity = PayrollSinergy(namePayrollSinergy=payrollSinergyData.get("namePayrollSinergy"), codePayrollSinergy=payrollSinergyData.get("codePayrollSinergy"))
        data = service.create(entity)
        logger.info("Concepto de nómina creado correctamente | IdPayrollSinergy=%s | namePayrollSinergy=%s", getattr(data, "IdPayrollSinergy", None), getattr(data, "namePayrollSinergy", None))
        return apiResponse(isSuccess=True, Message="Concepto de nómina creado correctamente.", result=payrollSinergyToDict(data))

    except ValueError as e:
        logger.warning("Validación creando concepto de nómina | namePayrollSinergy=%s | error=%s", getattr(payrollSinergyData, "namePayrollSinergy", None), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando concepto de nómina | namePayrollSinergy=%s | codePayrollSinergy=%s", getattr(payrollSinergyData, "namePayrollSinergy", None), getattr(payrollSinergyData, "codePayrollSinergy", None))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el concepto de nómina.")

@router.put("/{IdPayrollSinergy}", response_model=apiResponse)
def updatePayrollSinergy(IdPayrollSinergy: int, payrollSinergyData: dict, service: IPayrollSinergyApplication = Depends(getPayrollSinergyApplication)):
    try:
        logger.info("Actualizando concepto de nómina | IdPayrollSinergy=%s | namePayrollSinergy=%s | codePayrollSinergy=%s", IdPayrollSinergy, getattr(payrollSinergyData, "namePayrollSinergy", None), getattr(payrollSinergyData, "codePayrollSinergy", None))
        entity = PayrollSinergy(namePayrollSinergy=payrollSinergyData.get("namePayrollSinergy"), codePayrollSinergy=payrollSinergyData.get("codePayrollSinergy"))
        data = service.update(IdPayrollSinergy, entity)
        logger.info("Concepto de nómina actualizado correctamente | IdPayrollSinergy=%s", IdPayrollSinergy)
        return apiResponse(isSuccess=True, Message="Concepto de nómina actualizado correctamente.", result=payrollSinergyToDict(data))

    except ValueError as e:
        message = str(e)
        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        logger.warning("Validación actualizando concepto de nómina | IdPayrollSinergy=%s | status=%s | error=%s", IdPayrollSinergy, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando concepto de nómina | IdPayrollSinergy=%s", IdPayrollSinergy)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el concepto de nómina.")

@router.delete("/{IdPayrollSinergy}", response_model=apiResponse)
def deletePayrollSinergy(IdPayrollSinergy: int, service: IPayrollSinergyApplication = Depends(getPayrollSinergyApplication)):
    try:
        logger.info("Eliminando concepto de nómina | IdPayrollSinergy=%s", IdPayrollSinergy)
        service.delete(IdPayrollSinergy)
        logger.info("Concepto de nómina eliminado correctamente | IdPayrollSinergy=%s", IdPayrollSinergy)
        return apiResponse(isSuccess=True, Message="Concepto de nómina eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Concepto de nómina no encontrado al eliminar | IdPayrollSinergy=%s | error=%s", IdPayrollSinergy, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando concepto de nómina | IdPayrollSinergy=%s", IdPayrollSinergy)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el concepto de nómina.")
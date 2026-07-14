from app.infrastructure.repositories.LoanLogRepository import LoanLogRepository
from app.application.interfaces.ILoanLogApplication import ILoanLogApplication
from app.application.services.LoanLogApplication import LoanLogApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

router = APIRouter(prefix="/loans/loan-log", tags=["loan-log"])
logger = getLogger(__name__)

def getLoanLogApplication(db: Session = Depends(getDb)) -> ILoanLogApplication:
    repository = LoanLogRepository(db)
    return LoanLogApplication(repository)

@router.get("/", response_model=apiResponse)
def getAllLoanLogs(page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), employeeDocumentNumber: Optional[str] = Query(None), actionDateFrom: Optional[date] = Query(None), actionDateTo: Optional[date] = Query(None), service: ILoanLogApplication = Depends(getLoanLogApplication),):
    try:
        logger.info("Consultando logs | page=%s | pageSize=%s | employeeDocumentNumber=%s | actionDateFrom=%s | actionDateTo=%s", page, pageSize, employeeDocumentNumber, actionDateFrom, actionDateTo,)
        pagination = PaginationParams(page=page, pageSize=pageSize)
        data = service.getAll(pagination=pagination, employeeDocumentNumber=employeeDocumentNumber, actionDateFrom=actionDateFrom, actionDateTo=actionDateTo,)

        if not data.items:
            logger.info("No existen logs con los filtros enviados.")
            return apiResponse(isSuccess=False, Message="No existen logs registrados.", result=data,)

        logger.info("Logs obtenidos correctamente | total=%s | page=%s", data.total, data.page,)
        return apiResponse(isSuccess=True, Message="Logs obtenidos correctamente.", result=data,)

    except Exception:
        logger.exception("Error inesperado obteniendo logs.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los logs.",)
from app.infrastructure.repositories.LoanStatusHistoryRepository import LoanStatusHistoryRepository
from app.application.interfaces.ILoanStatusHistoryApplication import ILoanStatusHistoryApplication
from app.application.services.LoanStatusHistoryApplication import LoanStatusHistoryApplication
from app.infrastructure.repositories.LoanRepository import LoanRepository
from app.domain.dtos.LoanStatusHistoryDto import LoanStatusHistoryDto
from fastapi import APIRouter, Depends, HTTPException, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/loans/loan-status-history", tags=["loan-status-history"],)
logger = getLogger(__name__)

def getLoanStatusHistoryApplication(db: Session = Depends(getDb)) -> ILoanStatusHistoryApplication:
    loanRepository = LoanRepository(db)
    historyRepository = LoanStatusHistoryRepository(db)

    return LoanStatusHistoryApplication(loanRepository, historyRepository)

@router.get("/{IdLoanStatusHistory}", response_model=apiResponse[LoanStatusHistoryDto])
def getHistoryById(IdLoanStatusHistory: int, service: ILoanStatusHistoryApplication = Depends(getLoanStatusHistoryApplication)):
    try:
        logger.info("Consultando histórico | IdLoanStatusHistory=%s", IdLoanStatusHistory)
        data = service.getById(IdLoanStatusHistory)
        logger.info("Histórico obtenido correctamente | IdLoanStatusHistory=%s", IdLoanStatusHistory)
        return apiResponse(isSuccess=True, Message="Histórico obtenido correctamente.", result=data)

    except ValueError as exception:
        logger.warning("Histórico no encontrado | IdLoanStatusHistory=%s | error=%s", IdLoanStatusHistory, str(exception))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))

    except Exception:
        logger.exception("Error inesperado obteniendo histórico | IdLoanStatusHistory=%s", IdLoanStatusHistory)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el histórico.")

@router.get("/loan/{IdLoan}", response_model=apiResponse[list[LoanStatusHistoryDto]])
def getHistoriesByIdLoan(IdLoan: int, service: ILoanStatusHistoryApplication = Depends(getLoanStatusHistoryApplication)):
    try:
        logger.info("Consultando históricos por préstamo | IdLoan=%s", IdLoan)
        data = service.getByIdLoan(IdLoan)

        if not data:
            logger.info("No existen históricos registrados | IdLoan=%s", IdLoan)
            return apiResponse(isSuccess=False, Message="No existen históricos registrados para este préstamo.", result=[])
        
        logger.info("Históricos obtenidos correctamente | IdLoan=%s | total=%s", IdLoan, len(data))
        return apiResponse(isSuccess=True, Message="Históricos del préstamo obtenidos correctamente.", result=data)

    except Exception:
        logger.exception("Error inesperado obteniendo históricos | IdLoan=%s", IdLoan)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los históricos del préstamo.")
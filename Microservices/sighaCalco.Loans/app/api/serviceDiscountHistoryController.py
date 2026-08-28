from app.infrastructure.repositories.ServiceDiscountHistoryRepository import ServiceDiscountHistoryRepository
from app.application.interfaces.IServiceDiscountHistoryApplication import IServiceDiscountHistoryApplication
from app.application.services.ServiceDiscountHistoryApplication import ServiceDiscountHistoryApplication
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.common.pagination import PaginationParams
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/loans/service-discount-history", tags=["service-discount-history"])

def getServiceDiscountHistoryApplication(db: Session = Depends(getDb)) -> IServiceDiscountHistoryApplication:
    repository = ServiceDiscountHistoryRepository(db)

    return ServiceDiscountHistoryApplication(repository)

@router.get("/loan/{IdLoan}", response_model=apiResponse)
def getByIdLoan(IdLoan: int, page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=100), service: IServiceDiscountHistoryApplication = Depends(getServiceDiscountHistoryApplication)):
    try:
        pagination = PaginationParams(page=page, pageSize=pageSize)
        data = service.getByIdLoan(IdLoan=IdLoan, pagination=pagination)

        if not data.items:
            return apiResponse(isSuccess=False, Message="No existen descuentos registrados para este emolumento.", result=data)

        return apiResponse(isSuccess=True, Message="Histórico de descuentos obtenido correctamente.", result=data)

    except Exception:
        raise HTTPException(status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR), detail=("Error al obtener el histórico de descuentos."))
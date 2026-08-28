from app.domain.interfaces.IServiceDiscountHistoryRepository import IServiceDiscountHistoryRepository
from app.domain.entities.serviceDiscountHistory import ServiceDiscountHistory
from app.common.pagination import PaginationParams, PaginatedResult
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import date
from math import ceil

class ServiceDiscountHistoryRepository(IServiceDiscountHistoryRepository):

    def __init__(self, db: Session):
        self.db = db

    def getByIdLoan(self, IdLoan: int, pagination: PaginationParams) -> PaginatedResult[ServiceDiscountHistory]:
        try:
            query = self.db.query(ServiceDiscountHistory).filter(ServiceDiscountHistory.IdLoan == IdLoan)
            total = query.count()
            items = query.order_by(ServiceDiscountHistory.discountDate.desc(), ServiceDiscountHistory.IdServiceDiscountHistory.desc()).offset(pagination.offset).limit(pagination.pageSize).all()
            totalPages = (
                ceil(total / pagination.pageSize)
                if pagination.pageSize > 0
                else 0
            )

            return PaginatedResult(items=items, total=total, page=pagination.page, pageSize=(pagination.pageSize), totalPages=totalPages)

        except SQLAlchemyError as e:
            raise Exception("Error consultando el histórico de descuentos: " f"{str(e)}")

    def exists(self, IdLoan: int, discountDate: date) -> bool:
        try:
            historyFound = self.db.query(ServiceDiscountHistory).filter(ServiceDiscountHistory.IdLoan == IdLoan, ServiceDiscountHistory.discountDate == discountDate).first()

            return historyFound is not None
        
        except SQLAlchemyError as e:
            raise Exception("Error validando el histórico de descuentos: " f"{str(e)}")

    def create(self, historyData: ServiceDiscountHistory) -> ServiceDiscountHistory:
        try:
            self.db.add(historyData)
            self.db.flush()
            self.db.refresh(historyData)

            return historyData

        except SQLAlchemyError as e:
            raise Exception("Error creando el histórico " f"de descuento: {str(e)}")
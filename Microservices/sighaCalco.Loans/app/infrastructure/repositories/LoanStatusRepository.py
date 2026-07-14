from app.domain.interfaces.ILoanStatusRepository import ILoanStatusRepository
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.domain.entities.loanStatus import LoanStatus
from sqlalchemy.orm import Session
from typing import List, Optional

class LoanStatusRepository(ILoanStatusRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self) -> List[LoanStatus]:
        return (self.db.query(LoanStatus).order_by(LoanStatus.IdLoanStatus.asc()).all())

    def getById(self, IdLoanStatus: int) -> Optional[LoanStatus]:
        return (self.db.query(LoanStatus).filter(LoanStatus.IdLoanStatus == IdLoanStatus).first())

    def create(self, loanStatusData: LoanStatus) -> LoanStatus:
        try:
            newLoanStatus = LoanStatus(nameLoanStatus=loanStatusData.nameLoanStatus.strip(),)

            self.db.add(newLoanStatus)
            self.db.commit()
            self.db.refresh(newLoanStatus)

            return newLoanStatus

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un estado con ese nombre.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el estado: {str(e)}")

    def update(self, IdLoanStatus: int, loanStatusData: LoanStatus) -> Optional[LoanStatus]:
        try:
            loanStatusFound = self.getById(IdLoanStatus)

            if not loanStatusFound:
                return None

            if loanStatusData.nameLoanStatus is not None:
                loanStatusFound.nameLoanStatus = loanStatusData.nameLoanStatus.strip()

            self.db.commit()
            self.db.refresh(loanStatusFound)

            return loanStatusFound

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un estado con ese nombre.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar el estado: {str(e)}")

    def delete(self, IdLoanStatus: int) -> bool:
        try:
            loanStatusFound = self.getById(IdLoanStatus)

            if not loanStatusFound:
                return False

            self.db.delete(loanStatusFound)
            self.db.commit()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar el estado: {str(e)}")
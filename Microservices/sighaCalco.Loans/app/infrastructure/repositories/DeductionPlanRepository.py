from app.domain.interfaces.IDeductionPlanRepository import IDeductionPlanRepository
from app.domain.entities.deductionPlan import DeductionPlan
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional

class DeductionPlanRepository(IDeductionPlanRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self) -> List[DeductionPlan]:
        return (self.db.query(DeductionPlan).order_by(DeductionPlan.IdDeductionPlan.asc()).all())

    def getById(self, IdDeductionPlan: int) -> Optional[DeductionPlan]:
        return (self.db.query(DeductionPlan).filter(DeductionPlan.IdDeductionPlan == IdDeductionPlan).first())

    def create(self, deductionPlanData: DeductionPlan) -> DeductionPlan:
        try:
            newDeductionPlan = DeductionPlan(
                nameDeductionPlan=deductionPlanData.nameDeductionPlan.strip(),
                firstFortnight=deductionPlanData.firstFortnight,
                secondFortnight=deductionPlanData.secondFortnight,
            )

            self.db.add(newDeductionPlan)
            self.db.commit()
            self.db.refresh(newDeductionPlan)

            return newDeductionPlan

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un plan de deducción con ese nombre.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el plan de deducción: {str(e)}")

    def update(self, IdDeductionPlan: int, deductionPlanData: DeductionPlan) -> Optional[DeductionPlan]:
        try:
            deductionPlanFound = self.getById(IdDeductionPlan)

            if not deductionPlanFound:
                return None

            if deductionPlanData.nameDeductionPlan is not None:
                deductionPlanFound.nameDeductionPlan = deductionPlanData.nameDeductionPlan.strip()

            if deductionPlanData.firstFortnight is not None:
                deductionPlanFound.firstFortnight = deductionPlanData.firstFortnight

            if deductionPlanData.secondFortnight is not None:
                deductionPlanFound.secondFortnight = deductionPlanData.secondFortnight

            self.db.commit()
            self.db.refresh(deductionPlanFound)

            return deductionPlanFound

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un plan de deducción con ese nombre.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar el plan de deducción: {str(e)}")

    def delete(self, IdDeductionPlan: int) -> bool:
        try:
            deductionPlanFound = self.getById(IdDeductionPlan)

            if not deductionPlanFound:
                return False

            self.db.delete(deductionPlanFound)
            self.db.commit()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar el plan de deducción: {str(e)}")
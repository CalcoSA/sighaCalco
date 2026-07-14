from app.infrastructure.repositories.DeductionPlanRepository import DeductionPlanRepository
from app.application.interfaces.IDeductionPlanApplication import IDeductionPlanApplication
from app.application.services.DeductionPlanApplication import DeductionPlanApplication
from fastapi import APIRouter, Depends, HTTPException, status
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.entities.deductionPlan import DeductionPlan
from app.infrastructure.db.connection import getDb
from app.common.ApiResponse import apiResponse
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/loans/deduction-plan", tags=["deduction-plan"])
logger = getLogger(__name__)

def getDeductionPlanApplication(db: Session = Depends(getDb)) -> IDeductionPlanApplication:
    repository = DeductionPlanRepository(db)
    return DeductionPlanApplication(repository)

def deductionPlanToDict(item: DeductionPlan) -> dict:
    return {
        "IdDeductionPlan": item.IdDeductionPlan,
        "nameDeductionPlan": item.nameDeductionPlan,
        "firstFortnight": item.firstFortnight,
        "secondFortnight": item.secondFortnight,
    }

def deductionPlansToDict(items: List[DeductionPlan]) -> list[dict]:
    return [deductionPlanToDict(item) for item in items]

@router.get("/", response_model=apiResponse)
def getAllDeductionPlans(service: IDeductionPlanApplication = Depends(getDeductionPlanApplication)):
    try:
        logger.info("Consultando planes de deducción")
        data = service.getAll()
        result = deductionPlansToDict(data)

        if not result:
            logger.info("No existen planes de deducción registrados.")
            return apiResponse(isSuccess=False, Message="No existen planes de deducción registrados.", result=[])

        logger.info("Planes de deducción obtenidos correctamente | total=%s", len(result))
        return apiResponse(isSuccess=True, Message="Planes de deducción obtenidos correctamente.", result=result)

    except Exception:
        logger.exception("Error inesperado obteniendo planes de deducción.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los planes de deducción.")

@router.get("/{IdDeductionPlan}", response_model=apiResponse)
def getDeductionPlanById(IdDeductionPlan: int, service: IDeductionPlanApplication = Depends(getDeductionPlanApplication)):
    try:
        logger.info("Consultando plan de deducción | IdDeductionPlan=%s", IdDeductionPlan)
        data = service.getById(IdDeductionPlan)
        logger.info("Plan de deducción obtenido correctamente | IdDeductionPlan=%s", IdDeductionPlan)
        return apiResponse(isSuccess=True, Message="Plan de deducción obtenido correctamente.", result=deductionPlanToDict(data))

    except ValueError as e:
        logger.warning("Plan de deducción no encontrado | IdDeductionPlan=%s | error=%s", IdDeductionPlan, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado obteniendo plan de deducción | IdDeductionPlan=%s", IdDeductionPlan)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el plan de deducción.")

@router.post("/", response_model=apiResponse, status_code=status.HTTP_201_CREATED)
def createDeductionPlan(deductionPlanData: dict, service: IDeductionPlanApplication = Depends(getDeductionPlanApplication)):
    try:
        logger.info("Creando plan de deducción | nameDeductionPlan=%s | firstFortnight=%s | secondFortnight=%s", deductionPlanData.get("nameDeductionPlan"), deductionPlanData.get("firstFortnight"), deductionPlanData.get("secondFortnight"))
        entity = DeductionPlan(nameDeductionPlan=deductionPlanData.get("nameDeductionPlan") or "",  firstFortnight=deductionPlanData.get("firstFortnight", False), secondFortnight=deductionPlanData.get("secondFortnight", False))
        data = service.create(entity)
        logger.info("Plan de deducción creado correctamente | IdDeductionPlan=%s | nameDeductionPlan=%s", getattr(data, "IdDeductionPlan", None), getattr(data, "nameDeductionPlan", None))
        return apiResponse(isSuccess=True, Message="Plan de deducción creado correctamente.", result=deductionPlanToDict(data))

    except ValueError as e:
        logger.warning("Validación creando plan de deducción | nameDeductionPlan=%s | error=%s", deductionPlanData.get("nameDeductionPlan"), str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error inesperado creando plan de deducción | nameDeductionPlan=%s", deductionPlanData.get("nameDeductionPlan"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el plan de deducción.")

@router.put("/{IdDeductionPlan}", response_model=apiResponse)
def updateDeductionPlan(IdDeductionPlan: int, deductionPlanData: dict, service: IDeductionPlanApplication = Depends(getDeductionPlanApplication)):
    try:
        logger.info("Actualizando plan de deducción | IdDeductionPlan=%s | nameDeductionPlan=%s | firstFortnight=%s | secondFortnight=%s", IdDeductionPlan, deductionPlanData.get("nameDeductionPlan"), deductionPlanData.get("firstFortnight"), deductionPlanData.get("secondFortnight"))
        entity = DeductionPlan(nameDeductionPlan=deductionPlanData.get("nameDeductionPlan"), firstFortnight=deductionPlanData.get("firstFortnight"), secondFortnight=deductionPlanData.get("secondFortnight"))
        data = service.update(IdDeductionPlan, entity)
        logger.info("Plan de deducción actualizado correctamente | IdDeductionPlan=%s", IdDeductionPlan)
        return apiResponse(isSuccess=True, Message="Plan de deducción actualizado correctamente.", result=deductionPlanToDict(data))

    except ValueError as e:
        message = str(e)

        statusCode = (
            status.HTTP_404_NOT_FOUND
            if "no encontrado" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        logger.warning("Validación actualizando plan de deducción | IdDeductionPlan=%s | status=%s | error=%s", IdDeductionPlan, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)

    except Exception:
        logger.exception("Error inesperado actualizando plan de deducción | IdDeductionPlan=%s", IdDeductionPlan)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el plan de deducción.")

@router.delete("/{IdDeductionPlan}", response_model=apiResponse)
def deleteDeductionPlan(IdDeductionPlan: int, service: IDeductionPlanApplication = Depends(getDeductionPlanApplication)):
    try:
        logger.info("Eliminando plan de deducción | IdDeductionPlan=%s", IdDeductionPlan)
        service.delete(IdDeductionPlan)
        logger.info("Plan de deducción eliminado correctamente | IdDeductionPlan=%s", IdDeductionPlan)
        return apiResponse(isSuccess=True, Message="Plan de deducción eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Plan de deducción no encontrado al eliminar | IdDeductionPlan=%s | error=%s", IdDeductionPlan, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error inesperado eliminando plan de deducción | IdDeductionPlan=%s", IdDeductionPlan)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el plan de deducción.")
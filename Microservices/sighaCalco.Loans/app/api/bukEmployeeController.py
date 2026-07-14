from app.infrastructure.external.BukEmployeeClient import BukEmployeeClient
from app.infrastructure.logging.loggerConfig import getLogger
from fastapi import APIRouter, HTTPException, Query, status
from app.common.ApiResponse import apiResponse
import httpx

router = APIRouter(prefix="/loans/buk", tags=["buk"])
logger = getLogger(__name__)

@router.get("/employee-by-document", response_model=apiResponse)
async def getEmployeeByDocument(document_number: str = Query(..., min_length=3)):
    try:
        logger.info("Consultando colaborador en BUK | document_number=%s", document_number)
        client = BukEmployeeClient()
        data = await client.getEmployeeByDocument(document_number)

        if not data:
            logger.info("Colaborador no encontrado en BUK | document_number=%s", document_number)
            return apiResponse(isSuccess=False, Message="No se encontró ningún colaborador con ese documento.", result=None)

        logger.info("Colaborador obtenido correctamente desde BUK | document_number=%s", document_number)
        return apiResponse(isSuccess=True, Message="Colaborador obtenido correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación consultando colaborador BUK | document_number=%s | error=%s", document_number, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except httpx.HTTPStatusError as e:
        logger.exception("Error HTTP consultando BUK | document_number=%s | status=%s | response=%s", document_number, e.response.status_code, e.response.text)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Error consultando la API de BUK.")

    except Exception:
        logger.exception("Error inesperado consultando colaborador BUK | document_number=%s", document_number)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al consultar el colaborador en BUK.")
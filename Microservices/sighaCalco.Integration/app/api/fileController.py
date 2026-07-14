from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from app.infrastructure.storage.GeneratedFileStorage import GeneratedFileStorage
from app.application.interfaces.IFileApplication import IFileApplication
from app.application.services.FileApplication import FileApplication
from app.infrastructure.excel.ExcelReader import ExcelReader
from fastapi.responses import FileResponse, JSONResponse
from app.common.ApiResponse import apiResponse
from datetime import date

router = APIRouter(prefix="/integration/sinergy", tags=["sinergy"])

def getFileApplication() -> IFileApplication:
    excelReader = ExcelReader()
    storage = GeneratedFileStorage()
    return FileApplication(excelReader, storage)

@router.post("/generate", response_model=apiResponse)
async def generateReport(file: UploadFile = File(...), dateFrom: date = Form(...), dateTo: date = Form(...), service: IFileApplication = Depends(getFileApplication),):
    try:
        content = await file.read()
        data = service.generate(fileName=file.filename or "", content=content, dateFrom=dateFrom, dateTo=dateTo,)
        return apiResponse(isSuccess=True, Message="Archivo generado correctamente.", result=data,)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al generar el reporte: {str(e)}",)

@router.get("/files/{fileId}")
def getGeneratedFile(fileId: str):
    try:
        storage = GeneratedFileStorage()
        filePath = storage.getPath(fileId)

        return FileResponse(path=filePath, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=fileId,)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e),)

@router.post("/onlyoffice/callback/{fileId}")
async def onlyOfficeCallback(fileId: str):
    return JSONResponse({"error": 0})
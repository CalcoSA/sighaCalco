from app.infrastructure.storage.GeneratedFileStorage import GeneratedFileStorage
from app.application.interfaces.IFileApplication import IFileApplication
from app.domain.dtos.OnlyOfficeDto import OnlyOfficeConfigDto
from app.infrastructure.excel.ExcelReader import ExcelReader
from datetime import date
import jwt
import os

class FileApplication(IFileApplication):

    def __init__(self, excelReader: ExcelReader, storage: GeneratedFileStorage):
        self.excelReader = excelReader
        self.storage = storage

    def generate(self, fileName: str, content: bytes, dateFrom: date, dateTo: date,) -> OnlyOfficeConfigDto:

        if not fileName:
            raise ValueError("El nombre del archivo es obligatorio.")

        if not fileName.lower().endswith(".xlsx"):
            raise ValueError("El archivo debe ser formato .xlsx.")

        if not content:
            raise ValueError("El archivo está vacío.")

        if dateFrom > dateTo:
            raise ValueError("La fecha desde no puede ser mayor a la fecha hasta.")

        generatedFile = self.excelReader.generateTemplate(fileName=fileName, content=content, dateFrom=dateFrom, dateTo=dateTo,)

        fileId, _ = self.storage.save(generatedFile.content)

        integrationPublicUrl = os.getenv("INTEGRATION_PUBLIC_URL", "http://host.docker.internal:8002")
        onlyofficePublicUrl = os.getenv("ONLYOFFICE_PUBLIC_URL", "http://127.0.0.1:8085")
        jwtSecret = os.getenv("ONLYOFFICE_JWT_SECRET", "sighacalco_onlyoffice_secret_2026")

        config = {
            "documentType": "cell",
            "type": "desktop",
            "document": {
                "fileType": "xlsx",
                "key": fileId.replace(".", "_"),
                "title": generatedFile.fileName,
                "url": f"{integrationPublicUrl}/integration/sinergy/files/{fileId}",
                "permissions": {
                    "edit": False,
                    "download": True,
                    "print": True,
                },
            },
            "editorConfig": {
                "mode": "view",
                "lang": "es",
                "region": "es-CO",
                "callbackUrl": f"{integrationPublicUrl}/integration/sinergy/onlyoffice/callback/{fileId}",
                "customization": {
                    "forcesave": False,
                    "autosave": False,
                },
                "user": {
                    "id": "sigha-calco-user",
                    "name": "SIGHA CALCO",
                },
            },
        }

        token = jwt.encode(config, jwtSecret, algorithm="HS256")
        config["token"] = token

        return OnlyOfficeConfigDto(documentServerUrl=onlyofficePublicUrl, config=config,)
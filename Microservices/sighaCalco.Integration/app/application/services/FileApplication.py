from app.infrastructure.storage.GeneratedFileStorage import GeneratedFileStorage
from app.application.interfaces.IFileApplication import IFileApplication
from app.domain.dtos.OnlyOfficeDto import OnlyOfficeConfigDto
from app.infrastructure.excel.ExcelReader import ExcelReader
from app.infrastructure.storage.Master import Master
from datetime import date, datetime, timedelta
from pathlib import Path
import jwt
import os

class FileApplication(IFileApplication):

    def __init__(self, excelReader: ExcelReader, storage: GeneratedFileStorage):
        self.excelReader = excelReader
        self.storage = storage
        self.master = Master()

    def generate(self, fileName: str, content: bytes, dateFrom: date, dateTo: date,) -> OnlyOfficeConfigDto:

        if not fileName:
            raise ValueError("El nombre del archivo es obligatorio.")

        if not fileName.lower().endswith(".xlsx"):
            raise ValueError("El archivo debe ser formato .xlsx.")

        if not content:
            raise ValueError("El archivo está vacío.")

        if dateFrom > dateTo:
            raise ValueError("La fecha desde no puede ser mayor a la fecha hasta.")
        
        self._cleanupOldGeneratedExcels()

        previousMaster = self.master.readLatest()

        generatedFile = self.excelReader.generateTemplate(fileName=fileName, content=content, dateFrom=dateFrom, dateTo=dateTo, previousMaster=previousMaster)

        fileId, _ = self.storage.save(generatedFile.content)

        self.master.saveLatest(content)

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
    
    def _cleanupOldGeneratedExcels(self) -> None:
        retentionDays = 7

        generatedFolder = Path(__file__).resolve().parents[3] / "generated" / "sinergy"

        if not generatedFolder.exists():
            return

        limitDate = datetime.now() - timedelta(days=retentionDays)

        for filePath in generatedFolder.glob("*.xlsx"):
            try:
                fileModifiedDate = datetime.fromtimestamp(filePath.stat().st_mtime)

                if fileModifiedDate <= limitDate:
                    filePath.unlink()

            except Exception as exception:
                print(f"[WARN] No se pudo eliminar el archivo generado {filePath}: {exception}")
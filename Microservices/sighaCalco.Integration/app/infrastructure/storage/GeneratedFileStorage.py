from pathlib import Path
from datetime import datetime
from uuid import uuid4

class GeneratedFileStorage:

    def __init__(self):
        appPath = Path(__file__).resolve().parents[3]
        self.basePath = appPath / "generated" / "sinergy"
        self.basePath.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes) -> tuple[str, str]:
        fileId = f"sinergy_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}.xlsx"
        filePath = self.basePath / fileId
        filePath.write_bytes(content)

        return fileId, str(filePath)

    def getPath(self, fileId: str) -> Path:
        filePath = self.basePath / fileId

        if not filePath.exists():
            raise ValueError("El archivo generado no existe.")

        return filePath
from pathlib import Path

class Master:
    FILE_NAME = "last_master.xlsx"

    def saveLatest(self, content: bytes) -> Path:
        folder = self._getStorageFolder()
        folder.mkdir(parents=True, exist_ok=True)
        latestFilePath = folder / self.FILE_NAME

        if latestFilePath.exists():
            latestFilePath.unlink()

        latestFilePath.write_bytes(content)

        return latestFilePath

    def existsLatest(self) -> bool:
        return self.getLatestFilePath().exists()

    def readLatest(self) -> bytes | None:
        latestFilePath = self.getLatestFilePath()

        if not latestFilePath.exists():
            return None

        return latestFilePath.read_bytes()

    def getLatestFilePath(self) -> Path:
        return self._getStorageFolder() / self.FILE_NAME

    def _getStorageFolder(self) -> Path:
        return self._getProjectRoot() / "master"

    def _getProjectRoot(self) -> Path:
        return Path(__file__).resolve().parents[3]
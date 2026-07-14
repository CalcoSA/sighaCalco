from app.domain.dtos.OnlyOfficeDto import OnlyOfficeConfigDto
from abc import ABC, abstractmethod
from datetime import date

class IFileApplication(ABC):

    @abstractmethod
    def generate(self, fileName: str, content: bytes, dateFrom: date, dateTo: date,) -> OnlyOfficeConfigDto:
        pass
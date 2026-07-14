from pydantic import BaseModel
from typing import Any

class OnlyOfficeConfigDto(BaseModel):
    documentServerUrl: str
    config: dict[str, Any]
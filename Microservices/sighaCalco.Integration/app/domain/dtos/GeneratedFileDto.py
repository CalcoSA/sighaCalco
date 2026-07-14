from dataclasses import dataclass

@dataclass
class GeneratedFileDto:
    fileName: str
    content: bytes
    contentType: str
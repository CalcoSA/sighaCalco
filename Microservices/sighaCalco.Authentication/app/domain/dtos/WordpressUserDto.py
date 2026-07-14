from pydantic import BaseModel

class WordpressUserDto(BaseModel):
    wordpressUserId: int
    wordpressUserLogin: str
    wordpressUserName: str
    wordpressUserEmail: str
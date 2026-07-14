from app.domain.dtos.MenuOptionDto import MenuOptionResponseDto
from app.domain.dtos.RoleDto import RoleResponseDto
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class LoginDto(BaseModel):
    username: str
    password: str

class AuthUserDto(BaseModel):
    IdUser: Optional[int] = None
    wordpressUserId: Optional[int] = None
    userLogin: str
    userEmail: str
    userName: str
    roles: List[RoleResponseDto]
    menuOptions: List[MenuOptionResponseDto]

    model_config = ConfigDict(from_attributes=True)

class AuthResponseDto(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: AuthUserDto

class IntranetAccessDto(BaseModel):
    userLogin: str
    ts: int
    sig: str
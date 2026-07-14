from app.domain.dtos.RoleDto import RoleResponseDto
from pydantic import BaseModel, Field
from typing import List, Optional

class UserCreateDto(BaseModel):
    wordpressUserId: int
    userLogin: str
    userName: str
    statusUser: bool = True
    roleIds: List[int] = Field(default_factory=list)

class UserUpdateDto(BaseModel):
    statusUser: Optional[bool] = None
    roleIds: Optional[List[int]] = None

class AssignRolesToUserDto(BaseModel):
    roleIds: List[int] = Field(default_factory=list)

class UserResponseDto(BaseModel):
    IdUser: int
    wordpressUserId: int
    userLogin: str
    userName: str
    statusUser: bool
    roles: List[RoleResponseDto]
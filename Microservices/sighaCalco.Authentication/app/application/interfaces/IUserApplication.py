from app.domain.dtos.UserDto import UserCreateDto, UserUpdateDto, UserResponseDto
from app.domain.dtos.WordpressUserDto import WordpressUserDto
from abc import ABC, abstractmethod
from typing import List

class IUserApplication(ABC):

    @abstractmethod
    def searchWordpressUsers(self, search: str) -> List[WordpressUserDto]:
        pass

    @abstractmethod
    def getAll(self) -> List[UserResponseDto]:
        pass

    @abstractmethod
    def getById(self, IdUser: int) -> UserResponseDto:
        pass

    @abstractmethod
    def create(self, userData: UserCreateDto) -> UserResponseDto:
        pass

    @abstractmethod
    def update(self, IdUser: int, userData: UserUpdateDto) -> UserResponseDto:
        pass

    @abstractmethod
    def delete(self, IdUser: int) -> bool:
        pass
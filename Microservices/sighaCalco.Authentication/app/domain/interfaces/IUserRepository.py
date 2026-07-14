from app.domain.dtos.UserDto import UserCreateDto, UserUpdateDto
from app.domain.entities.menuOption import MenuOption
from app.domain.entities.user import User
from app.domain.entities.role import Role
from abc import ABC, abstractmethod
from typing import List, Optional

class IUserRepository(ABC):

    @abstractmethod
    def getAll(self) -> List[User]:
        pass

    @abstractmethod
    def getById(self, IdUser: int) -> Optional[User]:
        pass

    @abstractmethod
    def getByWordpressUserId(self, wordpressUserId: int) -> Optional[User]:
        pass

    @abstractmethod
    def getByUserLogin(self, userLogin: str) -> Optional[User]:
        pass

    @abstractmethod
    def create(self, userData: UserCreateDto) -> User:
        pass

    @abstractmethod
    def update(self, IdUser: int, userData: UserUpdateDto) -> Optional[User]:
        pass

    @abstractmethod
    def delete(self, IdUser: int) -> bool:
        pass

    @abstractmethod
    def getRolesByUser(self, IdUser: int) -> List[Role]:
        pass

    @abstractmethod
    def setRolesToUser(self, IdUser: int, roleIds: List[int]) -> List[Role]:
        pass

    @abstractmethod
    def getMenuOptionsByUser(self, IdUser: int) -> List[MenuOption]:
        pass
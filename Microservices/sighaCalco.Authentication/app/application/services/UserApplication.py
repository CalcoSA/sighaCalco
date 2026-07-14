from app.infrastructure.repositories.WordpressUserRepository import WordpressUserRepository
from app.domain.dtos.UserDto import (UserCreateDto, UserUpdateDto, UserResponseDto)
from app.application.interfaces.IUserApplication import IUserApplication
from app.domain.interfaces.IRoleRepository import IRoleRepository
from app.domain.interfaces.IUserRepository import IUserRepository
from app.domain.dtos.WordpressUserDto import WordpressUserDto
from typing import List

class UserApplication(IUserApplication):

    def __init__(self, userRepository: IUserRepository, roleRepository: IRoleRepository, wordpressUserRepository: WordpressUserRepository):
        self.userRepository = userRepository
        self.roleRepository = roleRepository
        self.wordpressUserRepository = wordpressUserRepository

    def searchWordpressUsers(self, search: str) -> List[WordpressUserDto]:
        searchValue = search.strip()

        if len(searchValue) < 3:
            raise ValueError("Debes ingresar mínimo 3 caracteres para buscar usuarios.")

        return self.wordpressUserRepository.searchUsers(searchValue)

    def getAll(self) -> List[UserResponseDto]:
        users = self.userRepository.getAll()
        return [self._buildResponse(user) for user in users]

    def getById(self, IdUser: int) -> UserResponseDto:
        userFound = self.userRepository.getById(IdUser)

        if not userFound:
            raise ValueError("Usuario no encontrado.")

        return self._buildResponse(userFound)

    def create(self, userData: UserCreateDto) -> UserResponseDto:
        wordpressUser = self.wordpressUserRepository.getById(userData.wordpressUserId)

        if not wordpressUser:
            raise ValueError("Usuario de WordPress no encontrado.")

        if wordpressUser["wordpressUserLogin"] != userData.userLogin.strip():
            raise ValueError("El ID y el usuario de WordPress no coinciden.")

        userExists = self.userRepository.getByWordpressUserId(userData.wordpressUserId)

        if userExists:
            raise ValueError("Este usuario de WordPress ya está autorizado en el aplicativo.")

        self._validateRoles(userData.roleIds)

        userCreated = self.userRepository.create(userData)

        if userData.roleIds:
            self.userRepository.setRolesToUser(userCreated.IdUser, userData.roleIds)

        return self._buildResponse(userCreated)

    def update(self, IdUser: int, userData: UserUpdateDto) -> UserResponseDto:
        userFound = self.userRepository.getById(IdUser)

        if not userFound:
            raise ValueError("Usuario no encontrado.")

        if userData.roleIds is not None:
            self._validateRoles(userData.roleIds)

        userUpdated = self.userRepository.update(IdUser, userData)

        if not userUpdated:
            raise ValueError("Usuario no encontrado.")

        if userData.roleIds is not None:
            self.userRepository.setRolesToUser(IdUser, userData.roleIds)

        return self._buildResponse(userUpdated)

    def delete(self, IdUser: int) -> bool:
        userFound = self.userRepository.getById(IdUser)

        if not userFound:
            raise ValueError("Usuario no encontrado.")

        return self.userRepository.delete(IdUser)

    def _validateRoles(self, roleIds: List[int]) -> None:
        availableRoles = self.roleRepository.getAll()
        availableRoleIds = [role.IdRole for role in availableRoles]

        for IdRole in roleIds:
            if IdRole not in availableRoleIds:
                raise ValueError(f"El rol {IdRole} no existe.")

    def _buildResponse(self, user) -> UserResponseDto:
        roles = self.userRepository.getRolesByUser(user.IdUser)

        return UserResponseDto(
            IdUser=user.IdUser,
            wordpressUserId=user.wordpressUserId,
            userLogin=user.userLogin,
            userName=user.userName,
            statusUser=user.statusUser,
            roles=roles
        )
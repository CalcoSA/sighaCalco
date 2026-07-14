from app.domain.interfaces.IUserRepository import IUserRepository
from app.domain.dtos.UserDto import UserCreateDto, UserUpdateDto
from app.domain.entities.roleMenuOption import RoleMenuOption
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.domain.entities.menuOption import MenuOption
from app.domain.entities.userRole import UserRole
from app.domain.entities.user import User
from app.domain.entities.role import Role
from sqlalchemy.orm import Session
from typing import List, Optional

class UserRepository(IUserRepository):

    def __init__(self, db: Session):
        self.db = db

    def getAll(self) -> List[User]:
        return (self.db.query(User).order_by(User.IdUser.asc()).all())

    def getById(self, IdUser: int) -> Optional[User]:
        return (self.db.query(User).filter(User.IdUser == IdUser).first())

    def getByWordpressUserId(self, wordpressUserId: int) -> Optional[User]:
        return (self.db.query(User).filter(User.wordpressUserId == wordpressUserId).first())

    def getByUserLogin(self, userLogin: str) -> Optional[User]:
        return (self.db.query(User).filter(User.userLogin == userLogin.strip()).first())

    def create(self, userData: UserCreateDto) -> User:
        try:
            newUser = User(
                wordpressUserId=userData.wordpressUserId,
                userLogin=userData.userLogin.strip(),
                userName=userData.userName,
                statusUser=userData.statusUser
            )

            self.db.add(newUser)
            self.db.commit()
            self.db.refresh(newUser)

            return newUser

        except IntegrityError:
            self.db.rollback()
            raise ValueError("El usuario de WordPress ya está autorizado en el aplicativo.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear el usuario del aplicativo: {str(e)}")

    def update(self, IdUser: int, userData: UserUpdateDto) -> Optional[User]:
        try:
            userFound = self.getById(IdUser)

            if not userFound:
                return None

            if userData.statusUser is not None:
                userFound.statusUser = userData.statusUser

            self.db.commit()
            self.db.refresh(userFound)

            return userFound

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar el usuario del aplicativo: {str(e)}")

    def delete(self, IdUser: int) -> bool:
        try:
            userFound = self.getById(IdUser)

            if not userFound:
                return False

            self.db.delete(userFound)
            self.db.commit()

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar el usuario del aplicativo: {str(e)}")

    def getRolesByUser(self, IdUser: int) -> List[Role]:
        return (
            self.db.query(Role)
            .join(UserRole, UserRole.IdRole == Role.IdRole)
            .filter(UserRole.IdUser == IdUser)
            .filter(UserRole.statusUserRole == True)
            .filter(Role.statusRole == True)
            .order_by(Role.nameRole.asc())
            .all()
        )

    def setRolesToUser(self, IdUser: int, roleIds: List[int]) -> List[Role]:
        try:
            roleIds = list(dict.fromkeys(roleIds))

            self.db.query(UserRole).filter(UserRole.IdUser == IdUser).delete()

            for IdRole in roleIds:
                relation = UserRole(IdUser=IdUser, IdRole=IdRole, statusUserRole=True)
                self.db.add(relation)

            self.db.commit()

            return self.getRolesByUser(IdUser)

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Uno o varios roles no son válidos.")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al asignar roles al usuario: {str(e)}")

    def getMenuOptionsByUser(self, IdUser: int) -> List[MenuOption]:
        return (
            self.db.query(MenuOption)
            .join(RoleMenuOption, RoleMenuOption.IdMenuOption == MenuOption.IdMenuOption)
            .join(Role, Role.IdRole == RoleMenuOption.IdRole)
            .join(UserRole, UserRole.IdRole == Role.IdRole)
            .filter(UserRole.IdUser == IdUser)
            .filter(UserRole.statusUserRole == True)
            .filter(Role.statusRole == True)
            .filter(MenuOption.statusMenuOption == True)
            .distinct()
            .order_by(MenuOption.orderMenuOption.asc())
            .all()
        )
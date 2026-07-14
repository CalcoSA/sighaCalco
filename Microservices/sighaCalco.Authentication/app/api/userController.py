from app.infrastructure.repositories.WordpressUserRepository import WordpressUserRepository
from app.domain.dtos.UserDto import ( UserCreateDto, UserUpdateDto, UserResponseDto )
from app.infrastructure.repositories.UserRepository import UserRepository
from app.application.interfaces.IUserApplication import IUserApplication
from app.infrastructure.repositories.RoleRepository import RoleRepository
from app.infrastructure.db.wordpressConnection import getWordpressDb
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.application.services.UserApplication import UserApplication
from app.infrastructure.logging.loggerConfig import getLogger
from app.domain.dtos.WordpressUserDto import WordpressUserDto
from app.domain.dtos.ApiResponseDto import apiResponseDto
from app.infrastructure.db.connection import getDb
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/authentication/user", tags=["user"])
logger = getLogger(__name__)

def getUserApplication(db: Session = Depends(getDb), wpDb: Session = Depends(getWordpressDb)) -> IUserApplication:
    userRepository = UserRepository(db)
    roleRepository = RoleRepository(db)
    wordpressUserRepository = WordpressUserRepository(wpDb)
    return UserApplication(userRepository, roleRepository, wordpressUserRepository)

@router.get("/wordpress-users", response_model=apiResponseDto[List[WordpressUserDto]])
def searchWordpressUsers(search: str = Query(...), service: IUserApplication = Depends(getUserApplication)):
    try:
        logger.info("Buscando usuarios WordPress | search=%s", search)
        data = service.searchWordpressUsers(search)
        logger.info("Usuarios WordPress obtenidos | total=%s", len(data))
        return apiResponseDto(isSuccess=True, Message="Usuarios de WordPress obtenidos correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación buscando usuarios WordPress | search=%s | error=%s", search, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.exception("Error buscando usuarios WordPress | search=%s", search)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al buscar usuarios de WordPress: {str(e)}")

@router.get("/", response_model=apiResponseDto[List[UserResponseDto]])
def getAllUsers(service: IUserApplication = Depends(getUserApplication)):
    try:
        logger.info("Consultando usuarios del aplicativo")
        data = service.getAll()

        if not data:
            return apiResponseDto(isSuccess=False, Message="No existen usuarios del aplicativo registrados.", result=[])
        
        logger.info("Usuarios del aplicativo obtenidos | total=%s", len(data))
        return apiResponseDto(isSuccess=True, Message="Usuarios del aplicativo obtenidos correctamente.", result=data)

    except Exception:
        logger.exception("Error obteniendo usuarios del aplicativo")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los usuarios del aplicativo.")

@router.get("/{IdUser}", response_model=apiResponseDto[UserResponseDto])
def getUserById(IdUser: int, service: IUserApplication = Depends(getUserApplication)):
    try:
        logger.info("Consultando usuario del aplicativo | IdUser=%s", IdUser)
        data = service.getById(IdUser)
        logger.info("Usuario del aplicativo obtenido | IdUser=%s", IdUser)
        return apiResponseDto(isSuccess=True, Message="Usuario del aplicativo obtenido correctamente.", result=data)

    except ValueError as e:
        logger.warning("Usuario del aplicativo no encontrado | IdUser=%s | error=%s", IdUser, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error obteniendo usuario del aplicativo | IdUser=%s", IdUser)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el usuario del aplicativo.")

@router.post("/", response_model=apiResponseDto[UserResponseDto], status_code=status.HTTP_201_CREATED)
def createUser(userData: UserCreateDto, service: IUserApplication = Depends(getUserApplication)):
    try:
        logger.info("Creando usuario del aplicativo | wordpressUserId=%s", userData.wordpressUserId)
        data = service.create(userData)
        logger.info("Usuario autorizado correctamente | IdUser=%s | wordpressUserId=%s", data.IdUser, data.wordpressUserId)
        return apiResponseDto(isSuccess=True, Message="Usuario autorizado correctamente.", result=data)

    except ValueError as e:
        logger.warning("Validación creando usuario del aplicativo | wordpressUserId=%s | error=%s", userData.wordpressUserId, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception:
        logger.exception("Error autorizando usuario del aplicativo | wordpressUserId=%s", userData.wordpressUserId)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al autorizar el usuario.")

@router.put("/{IdUser}", response_model=apiResponseDto[UserResponseDto])
def updateUser(IdUser: int, userData: UserUpdateDto, service: IUserApplication = Depends(getUserApplication)):
    try:
        logger.info("Actualizando usuario del aplicativo | IdUser=%s", IdUser)
        data = service.update(IdUser, userData)
        logger.info("Usuario del aplicativo actualizado correctamente | IdUser=%s", IdUser)
        return apiResponseDto(isSuccess=True, Message="Usuario del aplicativo actualizado correctamente.", result=data)

    except ValueError as e:
        message = str(e)
        statusCode = status.HTTP_404_NOT_FOUND if "no encontrado" in message.lower() else status.HTTP_400_BAD_REQUEST
        logger.warning("Validación actualizando usuario del aplicativo | IdUser=%s | status=%s | error=%s", IdUser, statusCode, message)
        raise HTTPException(status_code=statusCode, detail=message)
    
    except Exception:
        logger.exception("Error actualizando usuario del aplicativo | IdUser=%s", IdUser)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el usuario del aplicativo.")

@router.delete("/{IdUser}", response_model=apiResponseDto[dict])
def deleteUser(IdUser: int, service: IUserApplication = Depends(getUserApplication)):
    try:
        logger.info("Eliminando usuario del aplicativo | IdUser=%s", IdUser)
        service.delete(IdUser)
        logger.info("Usuario del aplicativo eliminado correctamente | IdUser=%s", IdUser)
        return apiResponseDto(isSuccess=True, Message="Usuario del aplicativo eliminado correctamente.", result={})

    except ValueError as e:
        logger.warning("Usuario del aplicativo no encontrado al eliminar | IdUser=%s | error=%s", IdUser, str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        logger.exception("Error eliminando usuario del aplicativo | IdUser=%s", IdUser)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el usuario del aplicativo.")
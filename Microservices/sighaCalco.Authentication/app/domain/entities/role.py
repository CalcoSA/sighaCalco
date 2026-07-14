from __future__ import annotations

from sqlalchemy import Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.connection import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.entities.userRole import UserRole
    from app.domain.entities.roleMenuOption import RoleMenuOption

class Role(Base):
    __tablename__ = "authentication_role"

    IdRole: Mapped[int] = mapped_column("IdRole", Integer, primary_key=True, autoincrement=True)
    nameRole: Mapped[str] = mapped_column("nameRole", String(100), nullable=False)
    statusRole: Mapped[int] = mapped_column("statusRole", SmallInteger, nullable=False, default=1)

    user_roles: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_menu_options: Mapped[List["RoleMenuOption"]] = relationship("RoleMenuOption", back_populates="role", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("nameRole", name="uq_role_name"),)
from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from app.infrastructure.db.connection import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.entities.role import Role
    from app.domain.entities.menuOption import MenuOption

class RoleMenuOption(Base):
    __tablename__ = "authentication_roleMenuOption"

    IdRoleMenuOption: Mapped[int] = mapped_column("IdRoleMenuOption", Integer, primary_key=True, autoincrement=True)
    IdRole: Mapped[int] = mapped_column("IdRole", Integer, ForeignKey("authentication_role.IdRole", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    IdMenuOption: Mapped[int] = mapped_column("IdMenuOption", Integer, ForeignKey("authentication_menuOption.IdMenuOption", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    role: Mapped["Role"] = relationship("Role", back_populates="role_menu_options")
    menu_option: Mapped["MenuOption"] = relationship("MenuOption", back_populates="role_menu_options")

    __table_args__ = (UniqueConstraint("IdRole", "IdMenuOption", name="uq_role_menu_option"),)
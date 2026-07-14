from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.connection import Base
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.entities.roleMenuOption import RoleMenuOption

class MenuOption(Base):
    __tablename__ = "authentication_menuOption"

    IdMenuOption: Mapped[int] = mapped_column("IdMenuOption", Integer, primary_key=True, autoincrement=True)
    nameMenuOption: Mapped[str] = mapped_column("nameMenuOption", String(100), nullable=False)
    pathMenuOption: Mapped[Optional[str]] = mapped_column("pathMenuOption", String(200), nullable=True)
    parentMenuOption: Mapped[Optional[int]] = mapped_column("parentMenuOption", Integer, ForeignKey("authentication_menuOption.IdMenuOption", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    orderMenuOption: Mapped[int] = mapped_column("orderMenuOption", Integer, nullable=False, default=0)
    statusMenuOption: Mapped[int] = mapped_column("statusMenuOption", SmallInteger, nullable=False, default=1)

    parent: Mapped[Optional["MenuOption"]] = relationship("MenuOption", remote_side=[IdMenuOption], back_populates="children")
    children: Mapped[List["MenuOption"]] = relationship("MenuOption", back_populates="parent")
    role_menu_options: Mapped[List["RoleMenuOption"]] = relationship("RoleMenuOption", back_populates="menu_option", cascade="all, delete-orphan")
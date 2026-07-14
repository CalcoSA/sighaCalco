from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.connection import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.entities.user import User
    from app.domain.entities.role import Role

class UserRole(Base):
    __tablename__ = "authentication_userRole"

    IdUserRole: Mapped[int] = mapped_column("IdUserRole", Integer, primary_key=True, autoincrement=True)
    IdUser: Mapped[int] = mapped_column("IdUser", Integer, ForeignKey("authentication_user.IdUser", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    IdRole: Mapped[int] = mapped_column("IdRole", Integer, ForeignKey("authentication_role.IdRole", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    statusUserRole: Mapped[int] = mapped_column("statusUserRole", SmallInteger, nullable=False, default=1)

    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    __table_args__ = (UniqueConstraint("IdUser", "IdRole", name="uq_user_role"),)
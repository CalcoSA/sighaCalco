from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import SmallInteger, String, UniqueConstraint
from app.infrastructure.db.connection import Base
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.dialects.mysql import BIGINT

if TYPE_CHECKING:
    from app.domain.entities.userRole import UserRole

class User(Base):
    __tablename__ = "authentication_user"

    IdUser: Mapped[int] = mapped_column("IdUser", primary_key=True, autoincrement=True)
    wordpressUserId: Mapped[int] = mapped_column("wordpressUserId", BIGINT(unsigned=True), nullable=False)
    userLogin: Mapped[str] = mapped_column("userLogin", String(60), nullable=False)
    userName: Mapped[Optional[str]] = mapped_column("userName", String(250), nullable=True)
    statusUser: Mapped[int] = mapped_column("statusUser", SmallInteger, nullable=False, default=1)

    user_roles: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("wordpressUserId", name="uq_user_wordpress_id"), UniqueConstraint("userLogin", name="uq_user_wordpress_login"),)
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base

if TYPE_CHECKING:
    from .role import Role


class User(Base):
    __tablename__ = "users"

    fullname: Mapped[str | None] = mapped_column(
        String(length=255), doc="Fullname name"
    )
    phone: Mapped[str] = mapped_column(String(length=255), doc="Phone number")
    password: Mapped[str] = mapped_column(String(length=255), doc="Password")
    is_locked: Mapped[bool] = mapped_column(default=False, doc="Is locked?")
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), doc="Role ID"
    )
    role: Mapped["Role"] = relationship(back_populates="users")

    def __str__(self):
        return f"User({self.id=}, {self.phone=})"

    def __repr__(self):
        return self.__str__()

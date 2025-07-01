from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base

if TYPE_CHECKING:
    from .user import User


class Role(Base):
    __tablename__ = "roles"

    title: Mapped[str] = mapped_column(unique=True)
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __str__(self):
        return f"Role({self.id=}, {self.title=})"

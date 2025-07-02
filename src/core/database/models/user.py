from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, doc="Email address")
    fullname: Mapped[str | None] = mapped_column(
        String(length=255), doc="Fullname name"
    )
    phone: Mapped[str | None] = mapped_column(String(length=255), doc="Phone number")
    password: Mapped[str] = mapped_column(String(length=255), doc="Password")
    is_active: Mapped[bool] = mapped_column(default=True, doc="Is locked?")
    is_admin: Mapped[bool] = mapped_column(default=False, doc="Is admin?")

    def __str__(self):
        return f"User({self.id=}, {self.email=})"

    def __repr__(self):
        return self.__str__()

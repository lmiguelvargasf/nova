from advanced_alchemy.base import IdentityAuditBase
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(IdentityAuditBase):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

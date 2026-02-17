import datetime

from advanced_alchemy.exceptions import DuplicateKeyError
from advanced_alchemy.extensions.litestar import repository, service
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import UserModel

_FIELD_DISPLAY_NAMES: dict[str, str] = {
    "email": "Email",
    "first_name": "First name",
    "last_name": "Last name",
    "password": "Password",
}


class UserAlreadyExistsError(Exception):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email '{email}' already exists.")


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid credentials")


class UserFieldEmptyError(ValueError):
    def __init__(self, field_name: str) -> None:
        self.field_name = field_name
        display_name = _FIELD_DISPLAY_NAMES.get(field_name, field_name)
        super().__init__(f"{display_name} cannot be empty.")


class UserService(service.SQLAlchemyAsyncRepositoryService[UserModel]):
    class Repo(repository.SQLAlchemyAsyncRepository[UserModel]):
        model_type = UserModel

    repository_type = Repo

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def hash_password(password: str) -> str:
        return PasswordHasher().hash(password)

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        ph = PasswordHasher()
        try:
            return bool(ph.verify(password_hash, password))
        except VerifyMismatchError, InvalidHash, VerificationError:
            return False
        except Exception:  # noqa: BLE001 # security boundary: do not leak verification errors
            return False

    @staticmethod
    def _require_non_empty(value: str, field_name: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise UserFieldEmptyError(field_name)
        return cleaned_value

    async def get_authenticated_user(self, user_id: int) -> UserModel | None:
        return await self.get_one_or_none(id=user_id)

    async def ensure_email_available(
        self,
        *,
        email: str,
        exclude_user_id: int | None = None,
    ) -> None:
        existing_user = await self.get_one_or_none(email=email)
        if existing_user is None:
            return
        if exclude_user_id is not None and existing_user.id == exclude_user_id:
            return
        raise UserAlreadyExistsError(email)

    async def create_user_account(
        self,
        *,
        db_session: AsyncSession,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        is_admin: bool = False,
        is_active: bool = True,
    ) -> UserModel:
        email_clean = self.normalize_email(email)
        await self.ensure_email_available(email=email_clean)
        try:
            return await self.create(
                {
                    "email": email_clean,
                    "password_hash": self.hash_password(password),
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_admin": is_admin,
                    "is_active": is_active,
                },
                auto_commit=True,
            )
        except DuplicateKeyError:
            await db_session.rollback()
            raise UserAlreadyExistsError(email_clean) from None

    async def authenticate_for_login(
        self,
        *,
        db_session: AsyncSession,
        email: str,
        password: str,
    ) -> tuple[UserModel, bool]:
        email_clean = self.normalize_email(email)
        if not email_clean or not password:
            raise InvalidCredentialsError

        user = await self.get_one_or_none(email=email_clean)
        if user is None or not user.is_active:
            raise InvalidCredentialsError

        if not self.verify_password(user.password_hash, password):
            raise InvalidCredentialsError

        reactivated = False
        if user.deleted_at is not None:
            user.deleted_at = None
            reactivated = True

        user.last_login_at = datetime.datetime.now(datetime.UTC)
        await db_session.commit()

        return user, reactivated

    async def apply_user_updates(
        self,
        *,
        db_session: AsyncSession,
        user: UserModel,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        password: str | None = None,
    ) -> UserModel:
        has_updates = False

        if email is not None:
            cleaned_email = self._require_non_empty(email, "email")
            if cleaned_email != user.email:
                await self.ensure_email_available(
                    email=cleaned_email,
                    exclude_user_id=user.id,
                )
            user.email = cleaned_email
            has_updates = True

        if first_name is not None:
            user.first_name = self._require_non_empty(first_name, "first_name")
            has_updates = True

        if last_name is not None:
            user.last_name = self._require_non_empty(last_name, "last_name")
            has_updates = True

        if password is not None:
            if not password:
                raise UserFieldEmptyError("password")
            user.password_hash = self.hash_password(password)
            has_updates = True

        if has_updates:
            await db_session.commit()

        return user

    async def soft_delete_user(
        self,
        *,
        db_session: AsyncSession,
        user: UserModel,
    ) -> None:
        user.soft_delete()
        await db_session.commit()

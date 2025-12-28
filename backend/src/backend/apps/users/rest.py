import datetime

from advanced_alchemy.exceptions import (
    DuplicateKeyError,
    NotFoundError,
    RepositoryError,
)
from advanced_alchemy.filters import LimitOffset, SearchFilter, StatementFilter
from advanced_alchemy.service import OffsetPagination
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError
from litestar import Controller, Request, delete, get, patch, post
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from msgspec import Struct
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.auth import create_access_token
from backend.apps.users.models import UserModel
from backend.apps.users.services import UserService


class UserResponse(Struct):
    id: int
    email: str
    first_name: str
    last_name: str


class UserCreate(Struct):
    email: str
    password: str
    first_name: str
    last_name: str


class UserUpdate(Struct):
    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class LoginRequest(Struct):
    email: str
    password: str


class LoginResponse(Struct):
    token: str
    user: UserResponse
    reactivated: bool


class DeleteResponse(Struct):
    deleted: bool


def _require_user(request: Request) -> UserModel:
    user = request.user
    if not isinstance(user, UserModel):
        raise HTTPException(status_code=401, detail="User is not authenticated")
    return user


def _require_admin(user: UserModel) -> None:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access users.")


class AuthController(Controller):
    path = "/api/auth"

    @post(path="/register")
    async def register(
        self,
        db_session: AsyncSession,
        data: UserCreate,
    ) -> LoginResponse:
        users_service = UserService(db_session)
        existing_user = await users_service.get_one_or_none(email=data.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists.")

        try:
            ph = PasswordHasher()
            user = await users_service.create(
                {
                    "email": data.email,
                    "password_hash": ph.hash(data.password),
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "is_admin": False,
                    "is_active": True,
                },
                auto_commit=True,
            )
        except DuplicateKeyError:
            await db_session.rollback()
            raise HTTPException(
                status_code=409, detail="User already exists."
            ) from None
        except RepositoryError as exc:
            await db_session.rollback()
            detail = exc.detail or "Unable to create user."
            raise HTTPException(status_code=400, detail=detail) from None

        token = create_access_token(user)
        return LoginResponse(
            token=token,
            user=users_service.to_schema(user, schema_type=UserResponse),
            reactivated=False,
        )

    @post(path="/login")
    async def login(
        self,
        db_session: AsyncSession,
        data: LoginRequest,
    ) -> LoginResponse:
        users_service = UserService(db_session)
        email_clean = (data.email or "").strip().lower()
        if not email_clean or not data.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = await users_service.get_one_or_none(email=email_clean)
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        ph = PasswordHasher()
        try:
            ok = ph.verify(user.password_hash, data.password)
        except (VerifyMismatchError, InvalidHash, VerificationError):
            ok = False
        except Exception:  # noqa: BLE001 # security boundary: do not leak verification errors
            ok = False

        if not ok:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        reactivated = False
        if user.deleted_at is not None:
            user.deleted_at = None
            reactivated = True

        user.last_login_at = datetime.datetime.now(datetime.UTC)
        await db_session.commit()

        token = create_access_token(user)
        return LoginResponse(
            token=token,
            user=users_service.to_schema(user, schema_type=UserResponse),
            reactivated=reactivated,
        )


class UserController(Controller):
    path = "/api/users"

    @get(path="")
    async def list_users(
        self,
        request: Request,
        db_session: AsyncSession,
        current_page: int = Parameter(
            ge=1, query="currentPage", default=1, required=False
        ),
        page_size: int = Parameter(query="pageSize", ge=1, default=20, required=False),
        search_string: str | None = Parameter(
            title="Field to search",
            query="searchString",
            default=None,
            required=False,
        ),
        search_ignore_case: bool = Parameter(
            title="Search should be case sensitive",
            query="searchIgnoreCase",
            default=True,
            required=False,
        ),
    ) -> OffsetPagination[UserResponse]:
        user = _require_user(request)
        _require_admin(user)

        users_service = UserService(db_session)
        filters: list[StatementFilter] = [
            LimitOffset(page_size, page_size * (current_page - 1))
        ]
        if search_string:
            filters.append(
                SearchFilter(
                    field_name={"email"},
                    value=search_string,
                    ignore_case=search_ignore_case,
                )
            )
        results, total = await users_service.list_and_count(*filters)
        return users_service.to_schema(
            results, total, filters=filters, schema_type=UserResponse
        )

    @get(path="/{user_id:int}")
    async def get_user(
        self,
        db_session: AsyncSession,
        user_id: int = Parameter(title="User ID", description="The user to retrieve."),
    ) -> UserResponse:
        users_service = UserService(db_session)
        try:
            user = await users_service.get(user_id)
        except NotFoundError:
            raise HTTPException(status_code=404, detail="User not found.") from None
        return users_service.to_schema(user, schema_type=UserResponse)

    @get(path="/me")
    async def get_me(
        self,
        request: Request,
        db_session: AsyncSession,
    ) -> UserResponse:
        user = _require_user(request)
        users_service = UserService(db_session)
        return users_service.to_schema(user, schema_type=UserResponse)

    @patch(path="/me")
    async def update_me(
        self,
        request: Request,
        db_session: AsyncSession,
        data: UserUpdate,
    ) -> UserResponse:
        user = _require_user(request)
        users_service = UserService(db_session)

        if data.email is not None:
            email = data.email.strip()
            if not email:
                raise HTTPException(status_code=400, detail="Email cannot be empty.")
            if email != user.email:
                existing_user = await users_service.get_one_or_none(email=email)
                if existing_user and existing_user.id != user.id:
                    raise HTTPException(status_code=409, detail="User already exists.")
            user.email = email

        if data.first_name is not None:
            first_name = data.first_name.strip()
            if not first_name:
                raise HTTPException(
                    status_code=400, detail="First name cannot be empty."
                )
            user.first_name = first_name

        if data.last_name is not None:
            last_name = data.last_name.strip()
            if not last_name:
                raise HTTPException(
                    status_code=400, detail="Last name cannot be empty."
                )
            user.last_name = last_name

        if data.password is not None:
            if not data.password:
                raise HTTPException(status_code=400, detail="Password cannot be empty.")
            ph = PasswordHasher()
            user.password_hash = ph.hash(data.password)

        await db_session.commit()
        return users_service.to_schema(user, schema_type=UserResponse)

    @delete(path="/me", status_code=200)
    async def delete_me(
        self,
        request: Request,
        db_session: AsyncSession,
    ) -> DeleteResponse:
        user = _require_user(request)
        user.soft_delete()
        await db_session.commit()
        return DeleteResponse(deleted=True)

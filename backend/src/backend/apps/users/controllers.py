import datetime

from advanced_alchemy.exceptions import (
    DuplicateKeyError,
    NotFoundError,
    RepositoryError,
)
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError
from litestar import Controller, Request, delete, get, patch, post
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.pagination import CursorPage, CursorPageMeta
from backend.apps.users.auth import create_access_token
from backend.apps.users.models import UserModel
from backend.apps.users.pagination import UserCursorPaginator
from backend.apps.users.schemas import (
    DeleteResponse,
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from backend.apps.users.services import UserService


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
        limit: int = Parameter(query="limit", ge=1, le=100, default=20, required=False),
        cursor: str | None = Parameter(query="cursor", default=None, required=False),
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
    ) -> CursorPage[UserResponse]:
        user = _require_user(request)
        db_user = await db_session.get(UserModel, user.id)
        if db_user is None:
            raise HTTPException(status_code=401, detail="User is not authenticated")
        _require_admin(db_user)

        paginator = UserCursorPaginator(
            db_session=db_session,
            search_string=search_string,
            search_ignore_case=search_ignore_case,
        )
        page = await paginator(cursor=cursor, results_per_page=limit)
        return CursorPage(
            items=list(page.items),
            page=CursorPageMeta(
                next_cursor=page.cursor,
                limit=page.results_per_page,
                has_next=page.cursor is not None,
            ),
        )

    @get(path="/latest")
    async def latest_users(
        self,
        request: Request,
        db_session: AsyncSession,
        limit: int = Parameter(query="limit", ge=1, le=100, default=5),
    ) -> list[UserResponse]:
        user = _require_user(request)
        db_user = await db_session.get(UserModel, user.id)
        if db_user is None:
            raise HTTPException(status_code=401, detail="User is not authenticated")

        stmt = (
            select(UserModel)
            .where(UserModel.deleted_at.is_(None))
            .order_by(UserModel.created_at.desc(), UserModel.id.desc())
            .limit(limit)
        )
        result = await db_session.execute(stmt)
        users = list(result.scalars())

        users_service = UserService(db_session)
        return [users_service.to_schema(u, schema_type=UserResponse) for u in users]

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
        db_user = await db_session.get(UserModel, user.id)
        if db_user is None:
            raise HTTPException(status_code=401, detail="User is not authenticated")
        users_service = UserService(db_session)
        return users_service.to_schema(db_user, schema_type=UserResponse)

    @patch(path="/me")
    async def update_me(
        self,
        request: Request,
        db_session: AsyncSession,
        data: UserUpdate,
    ) -> UserResponse:
        user = _require_user(request)
        db_user = await db_session.get(UserModel, user.id)
        if db_user is None:
            raise HTTPException(status_code=401, detail="User is not authenticated")
        users_service = UserService(db_session)

        if data.email is not None:
            email = data.email.strip()
            if not email:
                raise HTTPException(status_code=400, detail="Email cannot be empty.")
            if email != db_user.email:
                existing_user = await users_service.get_one_or_none(email=email)
                if existing_user and existing_user.id != db_user.id:
                    raise HTTPException(status_code=409, detail="User already exists.")
            db_user.email = email

        if data.first_name is not None:
            first_name = data.first_name.strip()
            if not first_name:
                raise HTTPException(
                    status_code=400, detail="First name cannot be empty."
                )
            db_user.first_name = first_name

        if data.last_name is not None:
            last_name = data.last_name.strip()
            if not last_name:
                raise HTTPException(
                    status_code=400, detail="Last name cannot be empty."
                )
            db_user.last_name = last_name

        if data.password is not None:
            if not data.password:
                raise HTTPException(status_code=400, detail="Password cannot be empty.")
            ph = PasswordHasher()
            db_user.password_hash = ph.hash(data.password)

        await db_session.commit()
        return users_service.to_schema(db_user, schema_type=UserResponse)

    @delete(path="/me", status_code=200)
    async def delete_me(
        self,
        request: Request,
        db_session: AsyncSession,
    ) -> DeleteResponse:
        user = _require_user(request)
        db_user = await db_session.get(UserModel, user.id)
        if db_user is None:
            raise HTTPException(status_code=401, detail="User is not authenticated")
        db_user.soft_delete()
        await db_session.commit()
        return DeleteResponse(deleted=True)

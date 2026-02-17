from advanced_alchemy.exceptions import (
    NotFoundError,
    RepositoryError,
)
from litestar import Controller, Request, delete, get, patch, post
from litestar.exceptions import HTTPException
from litestar.params import Parameter
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
from backend.apps.users.services import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserFieldEmptyError,
    UserService,
)


def _require_user(request: Request) -> UserModel:
    user = request.user
    if not isinstance(user, UserModel):
        raise HTTPException(status_code=401, detail="User is not authenticated")
    return user


def _require_admin(user: UserModel) -> None:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access users.")


async def _require_authenticated_user(
    request: Request,
    users_service: UserService,
) -> UserModel:
    user = _require_user(request)
    db_user = await users_service.get_authenticated_user(user.id)
    if db_user is None:
        raise HTTPException(status_code=401, detail="User is not authenticated")
    return db_user


class AuthController(Controller):
    path = "/api/auth"

    @post(path="/register")
    async def register(
        self,
        db_session: AsyncSession,
        data: UserCreate,
    ) -> LoginResponse:
        users_service = UserService(db_session)
        try:
            user = await users_service.create_user_account(
                db_session=db_session,
                email=data.email,
                password=data.password,
                first_name=data.first_name,
                last_name=data.last_name,
                is_admin=False,
                is_active=True,
            )
        except UserAlreadyExistsError:
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
        try:
            user, reactivated = await users_service.authenticate_for_login(
                db_session=db_session,
                email=data.email,
                password=data.password,
            )
        except InvalidCredentialsError:
            raise HTTPException(status_code=401, detail="Invalid credentials") from None

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
        users_service = UserService(db_session)
        await _require_authenticated_user(request, users_service)

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
        users_service = UserService(db_session)
        db_user = await _require_authenticated_user(request, users_service)
        return users_service.to_schema(db_user, schema_type=UserResponse)

    @patch(path="/me")
    async def update_me(
        self,
        request: Request,
        db_session: AsyncSession,
        data: UserUpdate,
    ) -> UserResponse:
        users_service = UserService(db_session)
        db_user = await _require_authenticated_user(request, users_service)
        try:
            updated_user = await users_service.apply_user_updates(
                db_session=db_session,
                user=db_user,
                email=data.email,
                first_name=data.first_name,
                last_name=data.last_name,
                password=data.password,
            )
        except UserFieldEmptyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from None
        except UserAlreadyExistsError:
            raise HTTPException(
                status_code=409, detail="User already exists."
            ) from None
        return users_service.to_schema(updated_user, schema_type=UserResponse)

    @delete(path="/me", status_code=200)
    async def delete_me(
        self,
        request: Request,
        db_session: AsyncSession,
    ) -> DeleteResponse:
        users_service = UserService(db_session)
        db_user = await _require_authenticated_user(request, users_service)
        await users_service.soft_delete_user(db_session=db_session, user=db_user)
        return DeleteResponse(deleted=True)

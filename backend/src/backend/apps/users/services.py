from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from .models import UserModel


class UserRepository(SQLAlchemyAsyncRepository[UserModel]):
    model_type = UserModel


class UserService(SQLAlchemyAsyncRepositoryService[UserModel, UserRepository]):
    repository_type = UserRepository

from advanced_alchemy.extensions.litestar import repository, service

from .models import UserModel


class UserService(service.SQLAlchemyAsyncRepositoryService[UserModel]):
    class Repo(repository.SQLAlchemyAsyncRepository[UserModel]):
        model_type = UserModel

    repository_type = Repo

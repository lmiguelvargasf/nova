from advanced_alchemy.base import metadata_registry

from backend.apps.users.models import UserModel

metadata = metadata_registry[None]

__all__ = ["UserModel", "metadata"]

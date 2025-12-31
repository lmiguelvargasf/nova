---
description: How to define a backend entity with its full layer stack (model, service, GraphQL types/inputs/queries/mutations, schema registration).
globs:
  - "backend/src/backend/apps/**/*"
alwaysApply: false
---

# Backend Entity Definition

This rule defines how to create a new entity and wire it through all layers.

## Naming Conventions

| Layer | Pattern | Example |
|-------|---------|---------|
| Model (ORM) | `{Entity}Model` | `UserModel` |
| Service | `{Entity}Service` | `UserService` |
| GraphQL Type | `{Entity}Type` | `UserType` |
| GraphQL Input | `{Entity}Input` | `UserInput` |
| GraphQL Query | `{Entity}Query` | `UserQuery` |
| GraphQL Mutation | `{Entity}Mutation` | `UserMutation` |
| Admin View | `{Entity}AdminView` | `UserAdminView` |
| Table name | lowercase singular | `"user"` |

## File Structure

```
backend/src/backend/
├── apps/{app_name}/
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy models
│   ├── services.py         # Service + Repository
│   └── graphql/
│       ├── __init__.py     # Exports Query/Mutation classes
│       ├── types.py        # Output types
│       ├── inputs.py       # Input types
│       ├── queries.py      # Query resolvers
│       └── mutations.py    # Mutation resolvers
└── admin/views/
    ├── __init__.py         # ADMIN_VIEWS registry
    └── {entity}.py         # Admin view for entity
```

## 1. Model (`models.py`)

```python
from advanced_alchemy.base import IdentityAuditBase
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column


class EntityModel(IdentityAuditBase):
    __tablename__ = "entity"

    # Fields with explicit types
    name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

- Inherit from `IdentityAuditBase` (provides `id`, `created_at`, `updated_at`)
- Use `Mapped[]` type hints with `mapped_column()`
- Set `__tablename__` to lowercase singular

## 2. Service (`services.py`)

```python
from advanced_alchemy.extensions.litestar import repository, service

from .models import EntityModel


class EntityService(service.SQLAlchemyAsyncRepositoryService[EntityModel]):
    class Repo(repository.SQLAlchemyAsyncRepository[EntityModel]):
        model_type = EntityModel

    repository_type = Repo
```

- Inherit from `SQLAlchemyAsyncRepositoryService[EntityModel]`
- Define nested `Repo` class with `model_type`
- Service provides: `get()`, `get_one_or_none()`, `create()`, `update()`, `delete()`, etc.

## 3. GraphQL Type (`graphql/types.py`)

```python
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

import strawberry
from strawberry import relay

from {app}.models import EntityModel


@strawberry.type
@dataclass
class EntityType(relay.Node):
    id: relay.NodeID[int]
    name: str

    @classmethod
    async def resolve_nodes(
        cls,
        *,
        info: strawberry.Info,
        node_ids: Iterable[str],
        required: bool = False,
    ):
        # Resolve nodes in the same order as node_ids
        # Prefer fetching in bulk and mapping back to preserve order.
        ...

    @classmethod
    def from_model(cls, entity: EntityModel) -> Self:
        return cls(
            id=entity.id,
            name=entity.name,
        )
```

- Use `@strawberry.type` + `@dataclass`
- Implement `from_model()` class method for ORM → GraphQL conversion
- **Relay IDs**:
  - Implement `relay.Node` and type the id field as `relay.NodeID[int]`
  - Expose object lookup via the root `node(id: ID!)` field and/or a dedicated `*_by_id(id: ID!)` field that takes a Relay Global ID (GraphQL scalar name is `ID`)

## 4. GraphQL Input (`graphql/inputs.py`)

```python
from dataclasses import dataclass

import strawberry


@strawberry.input
@dataclass
class EntityInput:
    name: str
```

- Use `@strawberry.input` + `@dataclass`
- Include only fields needed for creation/mutation

## 5. GraphQL Query (`graphql/queries.py`)

```python
import strawberry
from strawberry.types import Info

from {app}.services import EntityService

from .types import EntityType


@strawberry.type
class EntityQuery:
    @strawberry.field
    async def entity_by_id(self, info: Info, id: strawberry.relay.GlobalID) -> EntityType:
        return await id.resolve_node(info, ensure_type=EntityType)
```

- Prefer `*_by_id(id: strawberry.relay.GlobalID)` for details lookup (Relay Global ID; schema scalar is `ID`)
- Prefer connection fields (`@strawberry.relay.connection(...)`) for lists/pagination when appropriate

## 5.1 REST List Pagination (Litestar)
When adding REST list endpoints for an entity, prefer cursor pagination:
- Request: `limit` + optional `cursor`
- Response: `{ items: [...], page: { next_cursor, limit, has_next } }`
- Use Litestar’s `AbstractAsyncCursorPaginator` for the list implementation.

## 6. GraphQL Mutation (`graphql/mutations.py`)

```python
import strawberry
from advanced_alchemy.exceptions import DuplicateKeyError, RepositoryError
from graphql.error import GraphQLError
from strawberry.types import Info

from {app}.services import EntityService

from .inputs import EntityInput
from .types import EntityType


@strawberry.type
class EntityMutation:
    @strawberry.mutation
    async def create_entity(self, info: Info[GraphQLContext, None], entity_input: EntityInput) -> EntityType:
        db_session = info.context.db_session
        entity_service: EntityService = info.context.entity_service

        try:
            entity = await entity_service.create(
                {"name": entity_input.name},
                auto_commit=True,
            )
        except DuplicateKeyError:
            await db_session.rollback()
            raise GraphQLError("Entity already exists.") from None
        except RepositoryError as exc:
            await db_session.rollback()
            raise GraphQLError(exc.detail or "Unable to create entity.") from None

        return EntityType.from_model(entity)
```

- Use `@strawberry.type` class with `@strawberry.mutation` methods
- Handle `DuplicateKeyError`, `RepositoryError` → `GraphQLError`
- Call `db_session.rollback()` on errors
- Use `auto_commit=True` for single-operation mutations

## 7. GraphQL Exports (`graphql/__init__.py`)

```python
from .mutations import EntityMutation
from .queries import EntityQuery
```

## 8. Schema Registration (`backend/src/backend/schema.py`)

Add the new Query/Mutation to the root schema via inheritance:

```python
import strawberry

from .apps.{app_name}.graphql import EntityMutation, EntityQuery


@strawberry.type
class Query(EntityQuery, OtherQuery):  # Add to inheritance chain
    pass


@strawberry.type
class Mutation(EntityMutation, OtherMutation):  # Add to inheritance chain
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
```

## 9. Service Registration (Context)

Ensure the service is available in GraphQL context. Register it in the Litestar app's dependency injection or GraphQL context factory.

## 10. Admin View (`backend/src/backend/admin/views/{entity}.py`)

```python
from starlette_admin.contrib.sqla import ModelView

from backend.apps.{app_name}.models import EntityModel


class EntityAdminView(ModelView):
    label = "Entities"
    name = "Entity"
    identity = "entity"

    exclude_fields_from_list = ()
    exclude_fields_from_detail = ()
    exclude_fields_from_create = ("created_at", "updated_at")
    exclude_fields_from_edit = ("created_at", "updated_at")

    searchable_fields = ("name",)
    sortable_fields = ("id", "name", "created_at", "updated_at")


view = EntityAdminView(EntityModel, icon="fa fa-cube")
```

- Inherit from `ModelView`
- Set `label` (plural, shown in sidebar) and `name` (singular, used in forms)
- Use `exclude_fields_from_*` to hide sensitive fields (e.g., `password_hash`)
- Export as `view` for registration

## 11. Admin Registration (`backend/src/backend/admin/views/__init__.py`)

```python
from .entity import view as entity_view

ADMIN_VIEWS = [
    entity_view,
    # ... other views
]
```

## 12. Migration

After creating the model, generate a migration:

```bash
task backend:migrate:make -- "add entity model"
```

Apply with:

```bash
task backend:migrate
```

Review the generated migration in `backend/migrations/versions/`.

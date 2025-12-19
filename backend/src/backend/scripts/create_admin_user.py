import argparse
import asyncio
from getpass import getpass

from sqlalchemy import select

from backend.apps.users.models import UserModel
from backend.config.alchemy import alchemy_config
from backend.security.passwords import hash_password


async def _create_admin(
    *,
    email: str,
    password: str,
    first_name: str | None,
    last_name: str | None,
    is_admin: bool,
) -> None:
    email = email.strip().lower()
    async with alchemy_config.get_session() as session:
        existing = await session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        if existing:
            existing.is_admin = is_admin
            existing.is_active = True
            existing.password_hash = hash_password(password)
            if first_name is not None:
                existing.first_name = first_name
            if last_name is not None:
                existing.last_name = last_name
        else:
            session.add(
                UserModel(
                    email=email,
                    password_hash=hash_password(password),
                    first_name=first_name or "",
                    last_name=last_name or "",
                    is_admin=is_admin,
                    is_active=True,
                )
            )
        await session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or update a user (interactive by default)."
    )
    parser.add_argument("--email", default=None, help="User email")
    parser.add_argument("--first-name", default=None)
    parser.add_argument("--last-name", default=None)
    parser.add_argument("--password", default=None, help="User password (optional)")

    admin_group = parser.add_mutually_exclusive_group()
    admin_group.add_argument(
        "--superuser", dest="is_admin", action="store_const", const=True
    )
    admin_group.add_argument(
        "--no-superuser", dest="is_admin", action="store_const", const=False
    )
    parser.set_defaults(is_admin=None)
    args = parser.parse_args()

    email = (args.email or "").strip()
    while not email:
        email = input("Email: ").strip()

    password = args.password or ""
    while not password:
        password = getpass("Password: ").strip()

    is_admin = args.is_admin
    while is_admin is None:
        raw = input("Superuser? (y/N): ").strip().lower()
        if raw in {"y", "yes"}:
            is_admin = True
        elif raw in {"", "n", "no"}:
            is_admin = False

    asyncio.run(
        _create_admin(
            email=email,
            password=password,
            first_name=args.first_name,
            last_name=args.last_name,
            is_admin=is_admin,
        )
    )


if __name__ == "__main__":
    main()

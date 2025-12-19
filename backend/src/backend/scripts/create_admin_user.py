import argparse
import asyncio
import os
from getpass import getpass

from sqlalchemy import select

from backend.apps.users.models import UserModel
from backend.config.alchemy import alchemy_config
from backend.security.passwords import hash_password


async def _create_admin(
    *, email: str, password: str, first_name: str, last_name: str
) -> None:
    email = email.strip().lower()
    async with alchemy_config.get_session() as session:
        existing = await session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        if existing:
            existing.is_admin = True
            existing.is_active = True
            existing.password_hash = hash_password(password)
            existing.first_name = first_name
            existing.last_name = last_name
        else:
            session.add(
                UserModel(
                    email=email,
                    password_hash=hash_password(password),
                    first_name=first_name,
                    last_name=last_name,
                    is_admin=True,
                    is_active=True,
                )
            )
        await session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an admin user.")
    parser.add_argument(
        "--email", default=os.getenv("ADMIN_EMAIL", ""), help="Admin email"
    )
    parser.add_argument("--first-name", default=os.getenv("ADMIN_FIRST_NAME", "Admin"))
    parser.add_argument("--last-name", default=os.getenv("ADMIN_LAST_NAME", "User"))
    parser.add_argument(
        "--password",
        default=os.getenv("ADMIN_PASSWORD", ""),
        help="Admin password (use env var ADMIN_PASSWORD to avoid prompt)",
    )
    args = parser.parse_args()

    if not args.email:
        raise SystemExit("Missing --email (or ADMIN_EMAIL).")

    password = args.password or getpass("Admin password: ")
    if not password:
        raise SystemExit("Missing --password (or ADMIN_PASSWORD).")

    asyncio.run(
        _create_admin(
            email=args.email,
            password=password,
            first_name=args.first_name,
            last_name=args.last_name,
        )
    )


if __name__ == "__main__":
    main()

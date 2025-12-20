import argparse
import asyncio

from argon2 import PasswordHasher
from rich.console import Console
from rich.prompt import Prompt
from sqlalchemy import select

from backend.apps.users.models import UserModel
from backend.config.alchemy import alchemy_config


async def _create_admin(*, email: str, password: str) -> bool:
    email = email.strip().lower()
    async with alchemy_config.get_session() as session:
        existing = await session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        if existing:
            return False

        ph = PasswordHasher()
        session.add(
            UserModel(
                email=email,
                password_hash=ph.hash(password),
                first_name="",
                last_name="",
                is_admin=True,
                is_active=True,
            )
        )
        await session.commit()
        return True


def _is_valid_email(email: str) -> bool:
    email = email.strip()
    if not email:
        return False
    if " " in email:
        return False
    if "@" not in email:
        return False
    local, _, domain = email.partition("@")
    if not local or not domain:
        return False
    return True


def _prompt_non_empty(*, prompt: str, password: bool = False) -> str:
    value = ""
    while not value:
        value = Prompt.ask(prompt, password=password).strip()
    return value


def main() -> None:
    console = Console()
    parser = argparse.ArgumentParser(
        description="Create or update an admin user (interactive by default)."
    )
    parser.add_argument("--email", default=None, help="User email")
    parser.add_argument("--password", default=None, help="User password (optional)")
    args = parser.parse_args()

    email = (args.email or "").strip()
    if args.email is not None:
        if not _is_valid_email(email):
            raise SystemExit("Invalid --email (expected an email-like value).")
    else:
        while not _is_valid_email(email):
            email = _prompt_non_empty(prompt="Email").strip()

    password = (args.password or "").strip()
    if args.password is not None:
        if not password:
            raise SystemExit("Invalid --password (must be non-empty).")
    else:
        if not password:
            password = _prompt_non_empty(prompt="Password", password=True)

    with console.status("Saving user..."):
        created = asyncio.run(_create_admin(email=email, password=password))

    email_norm = email.strip().lower()
    if created:
        console.print(f"[green]Created admin user:[/green] {email_norm}")
    else:
        console.print(f"[yellow]User already exists:[/yellow] {email_norm}")


if __name__ == "__main__":
    main()

import base64
import json
from typing import TypeVar

from litestar.exceptions import HTTPException
from msgspec import Struct

T = TypeVar("T")


class CursorPageMeta(Struct):
    next_cursor: str | None
    limit: int
    has_next: bool


class CursorPage[T](Struct):
    items: list[T]
    page: CursorPageMeta


def encode_cursor(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> dict[str, object]:
    try:
        padding = "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode((cursor + padding).encode("ascii"))
        decoded = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail="Invalid cursor.") from e

    if not isinstance(decoded, dict):
        raise HTTPException(status_code=400, detail="Invalid cursor.")

    return decoded

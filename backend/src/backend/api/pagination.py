import base64
import hashlib
import hmac
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


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def compute_pagination_context_hash(*, sort: str, filters: dict[str, object]) -> str:
    raw = json.dumps(
        {"sort": sort, "filters": filters},
        separators=(",", ":"),
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def encode_cursor(*, payload: dict[str, object], secret: str) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    data = _b64url_encode(raw)
    sig = hmac.new(
        secret.encode("utf-8"), data.encode("ascii"), hashlib.sha256
    ).digest()
    return f"{data}.{_b64url_encode(sig)}"


def decode_cursor(
    *, cursor: str, secret: str, expected_context_hash: str
) -> dict[str, object]:
    def _raise_invalid_cursor() -> None:
        raise HTTPException(status_code=400, detail="Invalid cursor.")

    try:
        data, sig = cursor.split(".", 1)
        expected_sig = hmac.new(
            secret.encode("utf-8"),
            data.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(_b64url_decode(sig), expected_sig):
            _raise_invalid_cursor()

        decoded = json.loads(_b64url_decode(data).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail="Invalid cursor.") from e

    if not isinstance(decoded, dict):
        _raise_invalid_cursor()

    context_hash = decoded.get("context_hash")
    if not isinstance(context_hash, str) or context_hash != expected_context_hash:
        raise HTTPException(
            status_code=400, detail="Cursor does not match request filters."
        )

    return decoded

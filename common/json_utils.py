"""
JSON conversion utilities for common usage across the HTTP Service.

Provides safe serialization/deserialization helpers and convenience
wrappers around httpx responses.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping, Optional, Sequence, Union

import httpx


def _to_jsonable(obj: Any) -> Any:
    """Convert arbitrary Python objects into JSON-serializable structures.

    - dataclasses -> dict via asdict
    - Enums -> value
    - datetime/date/time -> ISO8601 strings
    - Decimal -> string (to avoid precision loss)
    - UUID -> string
    - Path -> string
    - bytes -> base64-like str (latin-1 decode fallback)
    - Mapping/Sequence -> recursively converted
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if is_dataclass(obj):
        return _to_jsonable(asdict(obj))

    if isinstance(obj, Enum):
        return _to_jsonable(obj.value)

    if isinstance(obj, (datetime, date, time)):
        # Use ISO format for portability
        return obj.isoformat()

    if isinstance(obj, Decimal):
        # Preserve precision by converting to string
        return str(obj)

    if isinstance(obj, uuid.UUID):
        return str(obj)

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, bytes):
        try:
            return obj.decode("utf-8")
        except Exception:
            return obj.decode("latin-1", errors="replace")

    if isinstance(obj, Mapping):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}

    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        return [_to_jsonable(item) for item in obj]

    # Fallback to string representation
    return str(obj)


class EnhancedJSONEncoder(json.JSONEncoder):
    """JSON encoder that knows how to encode common Python types.

    Used internally by json_dumps; can also be used directly.
    """

    def default(self, obj: Any) -> Any:  # noqa: D401 (doc inherited)
        return _to_jsonable(obj)


def to_jsonable(obj: Any) -> Any:
    """Public helper to convert an object to a JSON-serializable form."""
    return _to_jsonable(obj)


def json_dumps(
    obj: Any,
    *,
    sort_keys: bool = False,
    indent: Optional[int] = None,
    ensure_ascii: bool = False,
) -> str:
    """Serialize object to JSON string using EnhancedJSONEncoder.

    Args:
        obj: The object to serialize
        sort_keys: Sort dictionary keys in output
        indent: Indentation level; None for compact
        ensure_ascii: Escape non-ASCII characters
    """
    return json.dumps(
        obj,
        cls=EnhancedJSONEncoder,
        sort_keys=sort_keys,
        indent=indent,
        ensure_ascii=ensure_ascii,
        separators=(",", ":") if indent is None else None,
    )


def json_loads(s: Union[str, bytes, bytearray]) -> Any:
    """Deserialize JSON string to Python object.

    Raises json.JSONDecodeError on invalid input.
    """
    if isinstance(s, (bytes, bytearray)):
        s = s.decode("utf-8")
    return json.loads(s)


def pretty_json(obj: Any) -> str:
    """Return pretty-printed JSON string."""
    return json_dumps(obj, sort_keys=True, indent=2, ensure_ascii=False)


def to_json_file(path: Union[str, Path], obj: Any) -> None:
    """Write JSON to file with UTF-8 encoding."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json_dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def from_json_file(path: Union[str, Path]) -> Any:
    """Read JSON from file with UTF-8 encoding."""
    p = Path(path)
    return json_loads(p.read_text(encoding="utf-8"))


def is_json_media_type(content_type: Optional[str]) -> bool:
    """Return True if the content type looks like JSON."""
    if not content_type:
        return False
    return "application/json" in content_type.lower() or "+json" in content_type.lower()


def parse_response_json(
    response: httpx.Response,
    *,
    raise_for_status: bool = False,
) -> Any:
    """Parse JSON content from an httpx.Response.

    Args:
        response: The HTTP response
        raise_for_status: If True, call response.raise_for_status() before parsing

    Returns:
        Parsed JSON object

    Raises:
        json.JSONDecodeError: If body is not valid JSON
        httpx.HTTPStatusError: If raise_for_status is True and status is error
    """
    if raise_for_status:
        response.raise_for_status()

    # Respect content-type when available
    ct = response.headers.get("content-type", "")
    if not is_json_media_type(ct):
        # Still attempt to parse; httpx may return JSON without header
        pass

    return json_loads(response.text)


def safe_parse_response_json(response: httpx.Response) -> tuple[Optional[Any], Optional[json.JSONDecodeError]]:
    """Parse JSON and return (data, error) tuple without raising."""
    try:
        return parse_response_json(response), None
    except json.JSONDecodeError as e:
        return None, e


__all__ = [
    "EnhancedJSONEncoder",
    "to_jsonable",
    "json_dumps",
    "json_loads",
    "pretty_json",
    "to_json_file",
    "from_json_file",
    "is_json_media_type",
    "parse_response_json",
    "safe_parse_response_json",
]



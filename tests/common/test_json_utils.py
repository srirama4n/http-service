import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

import httpx

from common import (
    to_jsonable,
    json_dumps,
    json_loads,
    pretty_json,
    is_json_media_type,
    parse_response_json,
    safe_parse_response_json,
)


class Color(Enum):
    RED = "red"
    BLUE = "blue"


@dataclass
class Item:
    id: int
    when: datetime
    color: Color
    price: Decimal


def test_to_jsonable_complex():
    item = Item(id=1, when=datetime(2020, 1, 2, 3, 4, 5), color=Color.RED, price=Decimal("12.34"))
    data = to_jsonable(item)
    assert data["id"] == 1
    assert data["when"].startswith("2020-01-02")
    assert data["color"] == "red"
    assert data["price"] == "12.34"


def test_json_roundtrip():
    original = {"a": 1, "b": [1, 2, 3], "c": {"x": 10}}
    s = json_dumps(original)
    loaded = json_loads(s)
    assert loaded == original


def test_pretty_json_contains_newlines():
    s = pretty_json({"a": 1})
    assert "\n" in s


def test_is_json_media_type():
    assert is_json_media_type("application/json")
    assert is_json_media_type("application/vnd.api+json")
    assert not is_json_media_type("text/plain")


def test_parse_response_json_success():
    req = httpx.Request("GET", "https://example.com")
    res = httpx.Response(200, request=req, headers={"content-type": "application/json"}, json={"ok": True})
    data = parse_response_json(res)
    assert data == {"ok": True}


def test_safe_parse_response_json_error():
    req = httpx.Request("GET", "https://example.com")
    res = httpx.Response(200, request=req, headers={"content-type": "application/json"}, content=b"not json")
    data, err = safe_parse_response_json(res)
    assert data is None
    assert isinstance(err, json.JSONDecodeError)



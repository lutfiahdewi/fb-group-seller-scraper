from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, TypeVar

from app.models import GroupConfig

T = TypeVar("T")


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_groups(path: str | Path) -> list[GroupConfig]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [GroupConfig.model_validate(item) for item in data]


def unique_preserve_order(items: Iterable[T]) -> list[T]:
    seen = set()
    result: list[T] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
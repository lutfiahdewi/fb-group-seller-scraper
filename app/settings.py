from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    headless: bool = _as_bool(os.getenv("HEADLESS"), False)
    scroll_rounds: int = int(os.getenv("SCROLL_ROUNDS", "5"))
    scroll_pause_seconds: float = float(os.getenv("SCROLL_PAUSE_SECONDS", "2.5"))
    post_limit_per_group: int = int(os.getenv("POST_LIMIT_PER_GROUP", "20"))
    storage_dir: str = os.getenv("STORAGE_DIR", "storage")
    playwright_user_data_dir: str = os.getenv("PLAYWRIGHT_USER_DATA_DIR", "storage/pw_fb_profile")


settings = Settings()
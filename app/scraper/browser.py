from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from playwright.sync_api import BrowserContext, sync_playwright

from app.settings import settings


@contextmanager
def browser_context() -> Iterator[BrowserContext]:
    user_data_dir = Path(settings.playwright_user_data_dir).resolve()
    user_data_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Using profile: {user_data_dir}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-default-browser-check",
                "--disable-dev-shm-usage",
            ],
            slow_mo=100,
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        try:
            yield context
        finally:
            context.close()
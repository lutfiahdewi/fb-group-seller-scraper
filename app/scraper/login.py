from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

def save_login_session() -> None:
    session_path = Path("storage/login_session.json")
    session_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # Launch Chrome with anti-bot measures
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-default-browser-check",
            ]
        )
        
        # 🌟 THE UPGRADE: Load existing session if it exists
        if session_path.exists():
            print(f"[INFO] Found existing session. Loading {session_path.name} to bypass strict checks...")
            context = browser.new_context(storage_state=str(session_path))
        else:
            print("[INFO] No existing session found. Starting fresh login...")
            context = browser.new_context()
        
        # Inject script to hide the webdriver flag
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()
        page.goto("https://www.facebook.com/", wait_until="domcontentloaded")

        print("\n" + "="*50)
        print("ACTION REQUIRED:")
        print("1. If you see your profile, just enter your password.")
        print("2. Wait until the Facebook home/feed is fully loaded.")
        print("3. Return to this terminal and press ENTER.")
        print("="*50 + "\n")

        input()

        # Save the freshly authenticated session, overwriting the old one
        page.screenshot(path="storage/login_debug.png", full_page=True)
        context.storage_state(path=str(session_path))

        print(f"[SUCCESS] Session refreshed and saved to: {session_path.resolve()}")
        browser.close()

if __name__ == "__main__":
    save_login_session()
from __future__ import annotations
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from app.pipeline import SellerPipeline
from app.settings import settings
from app.storage.csv_writer import SellerCsvWriter
from app.storage.raw_writer import RawWriter
from app.utils import load_groups


def main() -> None:
    # 1. Record the exact start time
    start_time = datetime.now()
    start_ts = time.time()
    
    print("\n" + "="*50)
    print(f"[START] Scraping session began at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")
    
    session_path = Path("storage/login_session.json").resolve()

    print(f"[INFO] Using session file: {session_path}")
    print(f"[INFO] Exists: {session_path.exists()}")

    if not session_path.exists():
        print("[ERROR] login_session.json not found. Run login script first.")
        return

    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)

    groups = load_groups("config/groups.json")
    raw_writer = RawWriter(settings.storage_dir)
    seller_writer = SellerCsvWriter(settings.storage_dir)
    pipeline = SellerPipeline(raw_writer=raw_writer, seller_writer=seller_writer)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",  # important
        )

        context = browser.new_context(
            storage_state=str(session_path)
        )

        page = context.new_page()

        # 🔍 Step 1: Check login state
        page.goto("https://www.facebook.com/", wait_until="load", timeout=90000)
        page.wait_for_timeout(5000)

        print("[INFO] URL:", page.url)
        print("[INFO] Title:", page.title())

        page.screenshot(path="storage/session_check.png", full_page=True)
        print("[INFO] Screenshot saved: storage/session_check.png")

        # 🛑 If login expired → fix manually
        if "login" in page.url or "checkpoint" in page.url:
            print("\n[WARNING] Session not valid. Please log in manually.")
            input("After login is complete, press ENTER... ")

            page.goto("https://www.facebook.com/", wait_until="load")
            page.wait_for_timeout(5000)

            # 🔥 Save updated session again
            context.storage_state(path=str(session_path))
            print("[INFO] Session refreshed.")

        # 🚀 Step 2: Run scraper
        summaries = []

        for group in groups:
            print(f"\n[INFO] Scraping group: {group.name}")

            summary = pipeline.run_group(page, group)
            summaries.append(summary)

            print(summary)

        # 2. Record the exact finish time and calculate duration
        end_time = datetime.now()
        end_ts = time.time()
        duration_seconds = end_ts - start_ts
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)

        print("\n" + "="*50)
        print(f"[FINISH] Scraping session ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[TIME] Total duration: {minutes} minutes, {seconds} seconds")
        print("="*50)
        
        print("\nRun complete💯:")
        for summary in summaries:
            print(
                f"- {summary['group']}: "
                f"raw_posts={summary['raw_posts']}, "
                f"selling={summary['selling_posts']}, "
                f"regex_success={summary['extracted_by_regex']}, "
                f"needs_ai={summary['queued_for_ai']}"
            )

        # Add this right at the end of the `with` block!
        print("\n" + "="*50)
        input("[PAUSED] Scraping finished. Press ENTER in this terminal to close the browser... ")
        print("="*50)
        browser.close()




if __name__ == "__main__":
    main()
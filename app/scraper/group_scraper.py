from __future__ import annotations

import re
import time
from typing import Optional

from playwright.sync_api import Locator, Page

from app.models import GroupConfig, RawPostRecord
from app.scraper.selectors import (
    GROUP_POST_CARD_SELECTORS,    
    AUTHOR_SELECTORS,
    TEXT_SELECTORS,
    POST_LINK_SELECTORS,
    TIMESTAMP_SELECTORS,
    SEE_MORE_TEXTS,
    POST_ID_PATTERNS,
)

from app.settings import settings
from app.utils import unique_preserve_order


def _first_text(card: Locator, selectors: list[str]) -> Optional[str]:
    # 1. Try the specific selectors first (for normal posts)
    for selector in selectors:
        loc = card.locator(selector).first
        try:
            if loc.count() > 0:
                value = loc.inner_text(timeout=1000).strip()
                if value:
                    return value
        except Exception:
            continue
            
    # 2. 🆕 FALLBACK FOR JUAL BELI POSTS
    # If no specific text box is found, grab the text of the entire card.
    # It will grab the Title, Price, and Description all at once.
    try:
        fallback_text = card.inner_text(timeout=1000).strip()
        if fallback_text:
            return fallback_text
    except Exception:
        pass

    return None

def _first_href(card: Locator, selectors: list[str]) -> Optional[str]:
    for selector in selectors:
        loc = card.locator(selector).first
        try:
            if loc.count() > 0:
                href = loc.get_attribute("href", timeout=1000)
                if href:
                    return href
        except Exception:
            continue
    return None


def _expand_post(card: Locator) -> None:
    for text in SEE_MORE_TEXTS:
        try:
            # Find the text, take only the FIRST instance, and check if it exists
            btn = card.get_by_text(text).first
            
            if btn.count() > 0:
                # force=True tells Playwright to click it even if Facebook 
                # says another element is covering it
                btn.click(timeout=3000, force=True)
                
                # Give Facebook's React framework a half-second to render the new text
                time.sleep(0.5)
                return  # Exit the function once we successfully click
                
        except Exception:
            # If it fails (e.g., element detached), just ignore and try the next text
            continue
                

def _extract_post_link(card: Locator) -> str | None:
    for selector in POST_LINK_SELECTORS:
        try:
            loc = card.locator(selector).first
            if loc.count() > 0:
                href = loc.get_attribute("href", timeout=1500)
                if href:
                    return href
        except Exception:
            continue

    return None


def scrape_group(page: Page, group: GroupConfig) -> list[RawPostRecord]:
    print(f"\n[DEBUG] Opening group: {group.name}")
    page.goto(group.url, wait_until="load", timeout=90000)
    time.sleep(6)

    print("[DEBUG] URL:", page.url)
    print("[DEBUG] Title:", page.title())

    records: list[RawPostRecord] = []
    seen_keys: set[str] = set()
    max_cards = settings.post_limit_per_group

    for round_idx in range(settings.scroll_rounds):
        print(f"\n[DEBUG] --- Scroll Round {round_idx+1} ---")
        
        # 1. FORCE PAGE FOCUS: Click the middle of the viewport so FB registers the keyboard
        page.mouse.click(10, 10) 
        time.sleep(0.5)

        # 2. SCROLL DOWN: Use PageDown instead of mouse wheel (it behaves more like a human)
        for _ in range(5):
            page.keyboard.press("PageDown")
            time.sleep(0.5)  # Tiny human-like pause between presses
            
        # 3. NETWORK PAUSE: Wait for Facebook's servers to actually inject the new posts into the HTML
        time.sleep(settings.scroll_pause_seconds)

        # 2. Get currently loaded cards in the DOM
        author_blocks = page.locator("[data-ad-rendering-role='profile_name']")
        total = author_blocks.count()
        print(f"[DEBUG] Found {total} author blocks in current DOM")

        round_added = 0

        # 3. Process ALL currently visible cards from index 0
        for i in range(total):
            author_block = author_blocks.nth(i)
            card = author_block.locator("xpath=ancestor::div[@aria-posinset or parent::div[@role='feed'] or contains(@class, 'x1yztbdb')][1]")
            
            if card.count() == 0:
                print("[DEBUG] FAILED: Could not find the Card boundary for this author.")
                continue
                
            # Using your actual function
            text = _first_text(card, TEXT_SELECTORS)
            if not text:
                print("[DEBUG] FAILED: Could not find Text for this post.")
                # Let's see what the card actually contains to help us write a new selector!
                # print(card.inner_text(timeout=500)[:100]) 
                continue
                
            # Using your actual timestamp/link extraction
            link = _extract_post_link(card) 
            if not link:
                print("[DEBUG] FAILED: Could not find the Link/Timestamp for this post.")
                continue
                
                
            print("[DEBUG] SUCCESS: Post extracted!")

            # Quick identification to avoid extracting the same post twice
            try:
                post_url = _first_href(card, POST_LINK_SELECTORS)
                post_id = _extract_post_id(post_url)
            except Exception:
                post_url = None
                post_id = None

            try:
                raw_text_quick = card.inner_text(timeout=1000).strip()
            except Exception:
                raw_text_quick = ""

            # Deduplication Key Strategy (ID is best, text is fallback)
            dedupe_key = post_id if post_id else raw_text_quick[:100]

            # If we've already extracted this post in a previous round, skip it
            if not dedupe_key or dedupe_key in seen_keys:
                continue

            seen_keys.add(dedupe_key)

            # ==========================================
            # EXTRACTION (While the post is actively in DOM)
            # ==========================================
            try:
                _expand_post(card)  # Clicks 'Lihat selengkapnya' etc.
                time.sleep(0.5)

                try:
                    raw_text = card.inner_text(timeout=2500).strip()
                except Exception:
                    raw_text = raw_text_quick

                post_text = _first_text(card, TEXT_SELECTORS) or raw_text
                if not post_text:
                    post_text = card.inner_text(timeout=1000)
                post_text = _clean_post_text(post_text)

                author_name, author_profile_url = _extract_author(card)
                timestamp_text = _extract_timestamp(card)

                if not author_name and not post_text and not post_url:
                    continue

                # Filter out pure junk posts
                cleaned_check = (post_text or "").strip()
                if cleaned_check == "Facebook" or cleaned_check.count("Facebook") > 20:
                    continue

                record = RawPostRecord(
                    source_name=group.name,
                    source_url=group.url,
                    post_id=post_id,
                    post_url=post_url,
                    author_name=author_name,
                    author_profile_url=author_profile_url,
                    post_text=post_text,
                    timestamp_text=timestamp_text,
                    extraction_quality="full" if author_name and post_text and post_url else "partial" if (author_name or post_text or post_url) else "minimal",
                )

                records.append(record)
                round_added += 1

                print(f"[DEBUG] Extracted: {author_name} | {len(post_text or '')} chars")

                if len(records) >= max_cards:
                    break

            except Exception as e:
                print(f"[DEBUG] Error extracting card {i}: {e}")

        print(f"[DEBUG] Round {round_idx+1} finished. Added {round_added} posts. Total: {len(records)}")

        if len(records) >= max_cards:
            print(f"[DEBUG] Reached limit of {max_cards} posts.")
            break

    print(f"\n[DEBUG] Returning {len(records)} unique raw records")
    return records


def _extract_author(card: Locator) -> tuple[str | None, str | None]:
    for selector in AUTHOR_SELECTORS:
        try:
            loc = card.locator(selector).first
            if loc.count() > 0:
                name = loc.inner_text(timeout=1500).strip()
                href = loc.get_attribute("href", timeout=1500)
                if name or href:
                    return name or None, href or None
        except Exception:
            continue

    return None, None

def _extract_post_id(post_url: str | None) -> str | None:
    if not post_url:
        return None

    for pattern in POST_ID_PATTERNS :
        match = re.search(pattern, post_url)
        if match:
            return match.group(1)

    return None

def _clean_post_text(text: str) -> str:
    if not text:
        return ""

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    # remove junk UI noise
    junk = {
        "Facebook",
        "Suka",
        "Komentari",
        "Bagikan",
        "Tulis komentar publik…",
        "Lihat asli",
        "Beri Peringkat Terjemahan Ini",
    }

    cleaned = []
    for line in lines:
        if line in junk:
            continue
        cleaned.append(line)

    return "\n".join(cleaned).strip()


def _extract_timestamp(card: Locator) -> str | None:
    for selector in TIMESTAMP_SELECTORS:
        try:
            locs = card.locator(selector)
            
            for i in range(locs.count()):
                loc = locs.nth(i)
                
                # Try Strategy A: The legacy aria-label
                label = loc.get_attribute("aria-label", timeout=500)
                if label and 1 < len(label) < 40:
                    return label.strip()
                
                # Try Strategy B: Bypassing the Scrambled CSS
                # inner_text() ignores hidden elements and returns only what the human sees
                text = loc.inner_text(timeout=500).strip()
                
                # Timestamps are usually short (e.g., "5 m", "2 jam", "Kemarin")
                if text and 1 <= len(text) < 40:
                    
                    # Safety check to ensure we didn't grab an interaction button
                    junk_words = ["Tulis", "Komentar", "Suka", "Kirim", "Bagikan"]
                    if any(junk in text for junk in junk_words):
                        continue
                        
                    return text

        except Exception:
            continue

    return None


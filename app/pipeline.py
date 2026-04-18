from __future__ import annotations

from playwright.sync_api import Page

from app.detector.selling_detector import is_selling_post
from app.extractor.phone_extractor import extract_phones
from app.models import GroupConfig, SellerCandidate
from app.scraper.group_scraper import scrape_group
from app.storage.csv_writer import SellerCsvWriter
from app.storage.raw_writer import RawWriter

class SellerPipeline:
    def __init__(self, raw_writer: RawWriter, seller_writer: SellerCsvWriter) -> None:
        self.raw_writer = raw_writer
        self.seller_writer = seller_writer

    def run_group(self, page: Page, group: GroupConfig) -> dict:
        print(f"\n[PIPELINE] Starting extraction for {group.name}")
        raw_records = scrape_group(page, group)
        self.raw_writer.write_many(raw_records)

        seller_candidates: list[SellerCandidate] = []
        selling_count = 0
        ai_queue_count = 0

        for record in raw_records:
            # TIER 1 GATEKEEPER: Is it a selling post?
            if not is_selling_post(record.post_text):
                continue
                
            selling_count += 1
            
            # TIER 1 EXTRACTION: Try Regex first
            phones = extract_phones(record.post_text)
            
            if phones:
                # If regex found numbers, we save them.
                # We use the FIRST phone number as the primary contact to avoid duplicate rows
                primary_phone = phones[0] 
                
                seller_candidates.append(
                    SellerCandidate(
                        source_name=record.source_name,
                        source_url=record.source_url,
                        post_id=record.post_id,
                        post_url=record.post_url,
                        author_name=record.author_name,
                        phone=primary_phone,
                        post_text=record.post_text,
                        timestamp_text=record.timestamp_text,
                        scraped_at=record.scraped_at,
                        extraction_method="regex"
                    )
                )
            else:
                # TIER 2 PREPARATION: It is selling, but Regex failed.
                # Send to AI Queue. For now, we save it with a blank phone and 'needs_ai' status.
                ai_queue_count += 1
                seller_candidates.append(
                    SellerCandidate(
                        source_name=record.source_name,
                        source_url=record.source_url,
                        post_id=record.post_id,
                        post_url=record.post_url,
                        author_name=record.author_name,
                        phone=None, 
                        post_text=record.post_text,
                        timestamp_text=record.timestamp_text,
                        scraped_at=record.scraped_at,
                        extraction_method="needs_ai"
                    )
                )

        self.seller_writer.write_many(seller_candidates)
        
        return {
            "group": group.name,
            "raw_posts": len(raw_records),
            "selling_posts": selling_count,
            "extracted_by_regex": selling_count - ai_queue_count,
            "queued_for_ai": ai_queue_count
        }
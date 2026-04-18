from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class GroupConfig(BaseModel):
    name: str
    url: str


class RawPostRecord(BaseModel):
    platform: str = "facebook"
    source_type: str = "group"
    source_name: str
    source_url: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    author_name: Optional[str] = None
    author_profile_url: Optional[str] = None
    post_text: str = ""
    timestamp_text: Optional[str] = None
    media_urls: List[str] = Field(default_factory=list)
    scraped_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    extraction_quality: str = "minimal"
    scraper_version: str = "mvp_v1"


class SellerCandidate(BaseModel):
    source_name: str
    source_url: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    author_name: Optional[str] = None
    phone: Optional[str] = None # Make this optional in case AI fails later
    post_text: str
    timestamp_text: Optional[str] = None
    scraped_at: str
    extraction_method: str = "regex" # <-- New tracking field
    
    # Add this validator to automatically flatten newlines!
    @field_validator('post_text')
    def flatten_newlines(cls, v):
        if v:
            # Replaces newlines and carriage returns with a space
            # and removes extra double-spaces
            import re
            clean_text = v.replace('\n', ' ').replace('\r', ' ')
            return re.sub(r'\s+', ' ', clean_text).strip()
        return v
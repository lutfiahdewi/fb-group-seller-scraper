from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from app.models import SellerCandidate
from app.utils import ensure_dir

class SellerCsvWriter:
    def __init__(self, base_dir: str) -> None:
        ensure_dir(base_dir)
        
        # Generate a clean timestamp: YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Append the timestamp to the filename
        self.path = Path(base_dir) / f"seller_candidates_{timestamp}.csv"

    def write_many(self, records: Iterable[SellerCandidate]) -> None:
        rows = [r.model_dump() for r in records]
        if not rows:
            return
            
        df = pd.DataFrame(rows)
        
        # This will now only deduplicate posts found across different 
        # groups during THIS specific run, since the file is new each time.
        if self.path.exists():
            existing = pd.read_csv(self.path)
            df = pd.concat([existing, df], ignore_index=True)
            df = df.drop_duplicates(subset=["phone", "post_id", "post_url"], keep="last")
            
        df.to_csv(self.path, index=False)
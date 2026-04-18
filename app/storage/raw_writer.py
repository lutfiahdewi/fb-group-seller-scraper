from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from app.models import RawPostRecord
from app.utils import ensure_dir


class RawWriter:
    def __init__(self, base_dir: str) -> None:
        ensure_dir(base_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = Path(base_dir) / f"raw_posts_{timestamp}.jsonl"

    def write_many(self, records: Iterable[RawPostRecord]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class NewsItem:
    source: str
    title: str
    url: str
    summary: str = ""
    published_at: Optional[datetime] = None
    categories: List[str] = field(default_factory=list)
    score: int = 0
    item_id: str = ""
    signature: str = ""
    title_fa: str = ""
    reason: str = ""

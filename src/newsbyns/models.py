from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class NewsItem:
    item_id: str
    title: str
    url: str
    source: str
    published_at: datetime
    summary: str = ""
    categories: List[str] = field(default_factory=list)
    score: int = 0
    reasons: List[str] = field(default_factory=list)
    is_breaking: bool = False

    def primary_category(self) -> str:
        for cat in ["military", "diplomatic", "economic"]:
            if cat in self.categories:
                return cat
        return "minor"

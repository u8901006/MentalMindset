from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from src.deduplication import normalize_title_text


def load_recent_report_titles(
    report_dir: Path,
    report_date: str,
    days: int = 7,
) -> set[str]:
    try:
        target = date.fromisoformat(report_date)
    except ValueError:
        return set()

    titles: set[str] = set()
    if days <= 0:
        return titles

    for json_path in report_dir.glob("*.json"):
        try:
            file_date = date.fromisoformat(json_path.stem)
        except ValueError:
            continue

        if file_date >= target:
            continue
        if (target - file_date).days > days:
            continue

        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        for item in data.get("items") or []:
            raw_title = str(item.get("title") or "")
            normalized = normalize_title_text(raw_title).lower()
            if normalized:
                titles.add(normalized)

    return titles

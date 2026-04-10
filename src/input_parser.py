from __future__ import annotations

import re
from pathlib import Path


_WHITESPACE_RE = re.compile(r"\s+")
_EMPHASIS_RE = re.compile(r"[*_`]")


def _normalize_whitespace(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value).strip()


def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_journal_names(path: str) -> list[str]:
    journals: list[str] = []

    for raw_line in _read_text(path).splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue

        value = line[2:].split("—", 1)[0]
        value = _EMPHASIS_RE.sub("", value)
        value = _normalize_whitespace(value)
        if value and value not in journals:
            journals.append(value)

    return journals


def load_seed_keywords(path: str) -> list[str]:
    keywords: list[str] = []

    for raw_line in _read_text(path).splitlines():
        line = raw_line.strip()

        if line.startswith("|") and line.count("|") >= 3 and "---" not in line:
            columns = [column.strip() for column in line.strip("|").split("|")]
            if len(columns) >= 2 and columns[1] != "建議英文搜尋關鍵字":
                for value in columns[1].split(","):
                    normalized = _normalize_whitespace(value)
                    if normalized and normalized not in keywords:
                        keywords.append(normalized)

    return keywords

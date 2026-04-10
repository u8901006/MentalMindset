from __future__ import annotations

import json
from socket import timeout as SocketTimeout
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


CROSSREF_WORKS_URL = "https://api.crossref.org/works"


def _normalize_title(value: Any) -> str:
    return " ".join(str(value or "").split()).casefold()


def merge_crossref_metadata(
    base: dict[str, Any], crossref: dict[str, Any] | None
) -> dict[str, Any]:
    merged = dict(base)

    if not crossref:
        return merged

    doi = crossref.get("DOI")
    url = crossref.get("URL")
    titles = crossref.get("title") or []

    base_title = _normalize_title(base.get("title"))
    if not base_title or base_title not in {
        _normalize_title(title) for title in titles
    }:
        return merged

    if doi:
        merged["doi"] = doi

    if url:
        merged["url"] = url

    if titles and not merged.get("title"):
        merged["title"] = titles[0]

    return merged


def fetch_crossref_metadata(
    title: str,
    *,
    timeout_seconds: int = 30,
    opener=urlopen,
) -> dict[str, Any] | None:
    url = f"{CROSSREF_WORKS_URL}?{urlencode({'query.title': title, 'rows': 1})}"

    with opener(url, timeout=timeout_seconds) as response:
        payload = json.load(response)

    items = payload.get("message", {}).get("items", [])
    if not items:
        return None

    return items[0]


def enrich_with_crossref(
    base: dict[str, Any],
    *,
    timeout_seconds: int = 30,
    opener=urlopen,
) -> dict[str, Any]:
    title = str(base.get("title", "")).strip()
    if not title:
        return dict(base)

    try:
        crossref = fetch_crossref_metadata(
            title,
            timeout_seconds=timeout_seconds,
            opener=opener,
        )
    except (SocketTimeout, TimeoutError, URLError, ValueError):
        return dict(base)

    return merge_crossref_metadata(base, crossref)

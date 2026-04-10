from __future__ import annotations

import json
from dataclasses import dataclass
from socket import timeout as SocketTimeout
from typing import Any, Callable
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
MAX_GET_QUERY_LENGTH = 2000

JsonOpener = Callable[..., Any]


@dataclass(frozen=True)
class PubMedArticle:
    pubmed_id: str
    title: str
    journal: str
    source: str
    pubdate: str
    authors: list[str]
    publication_types: list[str]
    abstract: str


def parse_pubmed_search_ids(payload: dict[str, Any]) -> list[str]:
    return list(payload.get("esearchresult", {}).get("idlist", []))


def parse_pubmed_article_summaries(payload: dict[str, Any]) -> list[PubMedArticle]:
    result = payload.get("result", {})
    records: list[PubMedArticle] = []

    for pubmed_id in result.get("uids", []):
        raw_record = result.get(pubmed_id, {})
        author_items = raw_record.get("authors") or []
        authors = [item.get("name", "") for item in author_items if item.get("name")]
        publication_types = [
            str(item) for item in (raw_record.get("pubtype") or []) if str(item).strip()
        ]
        journal = str(
            raw_record.get("fulljournalname") or raw_record.get("source") or ""
        )
        records.append(
            PubMedArticle(
                pubmed_id=str(raw_record.get("uid", pubmed_id)),
                title=str(raw_record.get("title", "")),
                journal=journal,
                source=str(raw_record.get("source", "")),
                pubdate=str(raw_record.get("pubdate", "")),
                authors=authors,
                publication_types=publication_types,
                abstract=str(raw_record.get("abstract") or ""),
            )
        )

    return records


def _get_json(
    base_url: str,
    params: dict[str, Any],
    *,
    timeout_seconds: int,
    retry_attempts: int,
    opener: JsonOpener = urlopen,
) -> dict[str, Any]:
    encoded_params = urlencode(params)
    request: str | Request
    if len(encoded_params) > MAX_GET_QUERY_LENGTH:
        request = Request(
            base_url,
            data=encoded_params.encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
    else:
        request = f"{base_url}?{encoded_params}"
    attempts = retry_attempts + 1

    for attempt in range(attempts):
        try:
            with opener(request, timeout=timeout_seconds) as response:
                return json.load(response)
        except (SocketTimeout, TimeoutError, URLError):
            if attempt == attempts - 1:
                raise

    raise RuntimeError("unreachable")


def search_pubmed(
    query: str,
    *,
    retmax: int = 20,
    timeout_seconds: int = 30,
    retry_attempts: int = 2,
    opener: JsonOpener = urlopen,
) -> list[str]:
    payload = _get_json(
        PUBMED_SEARCH_URL,
        {
            "db": "pubmed",
            "retmode": "json",
            "term": query,
            "retmax": retmax,
        },
        timeout_seconds=timeout_seconds,
        retry_attempts=retry_attempts,
        opener=opener,
    )
    return parse_pubmed_search_ids(payload)


def fetch_pubmed_records(
    identifiers: list[str],
    *,
    timeout_seconds: int = 30,
    retry_attempts: int = 2,
    opener: JsonOpener = urlopen,
) -> list[PubMedArticle]:
    if not identifiers:
        return []

    payload = _get_json(
        PUBMED_SUMMARY_URL,
        {
            "db": "pubmed",
            "retmode": "json",
            "id": ",".join(identifiers),
        },
        timeout_seconds=timeout_seconds,
        retry_attempts=retry_attempts,
        opener=opener,
    )
    return parse_pubmed_article_summaries(payload)

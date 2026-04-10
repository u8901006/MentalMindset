from __future__ import annotations

from typing import Any


def normalize_title_text(title: Any) -> str:
    return " ".join(str(title or "").split())


def _normalize_identifier(value: Any) -> str:
    return str(value or "").strip().lower()


def deduplicate_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduplicated: list[dict[str, Any]] = []
    seen_dois: set[str] = set()
    seen_pmids: set[str] = set()

    for paper in papers:
        normalized = dict(paper)
        normalized["title"] = normalize_title_text(normalized.get("title"))

        doi = _normalize_identifier(normalized.get("doi"))
        pmid = _normalize_identifier(normalized.get("pmid"))

        if doi:
            if doi in seen_dois:
                continue
            seen_dois.add(doi)
        elif pmid:
            if pmid in seen_pmids:
                continue

        if pmid:
            seen_pmids.add(pmid)

        if doi:
            normalized["doi"] = doi
        if pmid:
            normalized["pmid"] = pmid

        deduplicated.append(normalized)

    return deduplicated

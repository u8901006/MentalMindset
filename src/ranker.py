from __future__ import annotations

from typing import Any


REVIEW_TYPE_WEIGHTS = {
    "meta-analysis": 5,
    "systematic review": 4,
    "review": 3,
    "randomized controlled trial": 4,
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def score_paper(
    paper: dict[str, Any],
    curated_journals: set[str] | None = None,
) -> int:
    score = 0
    publication_types = paper.get("publication_types") or []
    normalized_types = [_normalize_text(value) for value in publication_types]
    score += max(
        (
            REVIEW_TYPE_WEIGHTS.get(publication_type, 0)
            for publication_type in normalized_types
        ),
        default=0,
    )

    normalized_journals = {
        _normalize_text(journal) for journal in (curated_journals or set())
    }
    journal = _normalize_text(paper.get("journal"))
    if journal and journal in normalized_journals:
        score += 3

    score += len(paper.get("matched_keywords") or [])

    return score


def rank_top_papers(
    papers: list[dict[str, Any]],
    curated_journals: set[str] | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    ranked = sorted(
        papers,
        key=lambda paper: (
            -score_paper(paper, curated_journals=curated_journals),
            _normalize_text(paper.get("title")),
        ),
    )

    return ranked[:limit]

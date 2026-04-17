from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Callable, Mapping

from src.crossref_client import enrich_with_crossref
from src.deduplication import deduplicate_papers, normalize_title_text
from src.history_dedup import load_recent_report_titles
from src.input_parser import load_journal_names, load_seed_keywords
from src.pubmed_client import fetch_pubmed_records, search_pubmed
from src.query_builder import build_pubmed_query
from src.ranker import rank_top_papers, score_paper
from src.report_generator import render_json_report, render_markdown_report
from src.summarizer import FallbackSummaryAdapter, SummaryAdapter


Paper = dict[str, Any]
SearchClient = Callable[[str], list[str]]
RecordsClient = Callable[[list[str]], list[Any]]
EnrichmentClient = Callable[[Paper], Paper]


def _to_paper(record: Any) -> Paper:
    if isinstance(record, dict):
        return dict(record)
    if is_dataclass(record):
        return asdict(record)
    if isinstance(record, Mapping):
        return dict(record)
    raise TypeError(f"Unsupported paper record type: {type(record)!r}")


def _match_keywords(paper: Paper, keywords: list[str]) -> list[str]:
    haystack = " ".join(
        [
            str(paper.get("title") or ""),
            str(paper.get("abstract") or ""),
        ]
    ).lower()
    matched: list[str] = []
    for keyword in keywords:
        normalized = str(keyword or "").strip()
        if normalized and normalized.lower() in haystack and normalized not in matched:
            matched.append(normalized)
    return matched


def select_top_papers(papers: list[Paper], max_selected: int = 10) -> list[Paper]:
    ranked = sorted(
        papers,
        key=lambda paper: (
            -int(paper.get("score") or 0),
            str(paper.get("title") or "").lower(),
        ),
    )
    return ranked[:max_selected]


def _filter_excluded_titles(
    papers: list[Paper], exclude_titles: set[str] | None
) -> list[Paper]:
    if not exclude_titles:
        return papers
    return [
        p
        for p in papers
        if normalize_title_text(p.get("title")).lower() not in exclude_titles
    ]


def run_daily_pipeline(
    report_date: str,
    journals: list[str],
    keywords: list[str],
    priority_keywords: list[str],
    lookback_days: int,
    *,
    search_client: SearchClient = search_pubmed,
    records_client: RecordsClient = fetch_pubmed_records,
    enrichment_client: EnrichmentClient = enrich_with_crossref,
    summary_adapter: SummaryAdapter | None = None,
    curated_journals: set[str] | None = None,
    max_selected: int = 10,
    exclude_titles: set[str] | None = None,
) -> dict[str, Any]:
    query = build_pubmed_query(journals, keywords, priority_keywords, lookback_days)
    identifiers = search_client(query)
    records = [_to_paper(record) for record in records_client(identifiers)]
    topic_keywords = keywords + priority_keywords

    enriched: list[Paper] = []
    for paper in records:
        enriched_paper = dict(enrichment_client(paper))
        enriched_paper.setdefault(
            "matched_keywords",
            _match_keywords(enriched_paper, topic_keywords),
        )
        enriched.append(enriched_paper)

    deduplicated = deduplicate_papers(enriched)
    filtered = _filter_excluded_titles(deduplicated, exclude_titles)
    ranked = rank_top_papers(
        filtered,
        curated_journals=curated_journals or set(journals),
        limit=max_selected,
    )

    adapter = summary_adapter or FallbackSummaryAdapter()
    scored = [
        {
            **paper,
            "score": score_paper(
                paper,
                curated_journals=curated_journals or set(journals),
            ),
            "summary": adapter.summarize(paper),
        }
        for paper in ranked
    ]
    selected = select_top_papers(scored, max_selected=max_selected)

    return {
        "query": query,
        "papers": selected,
        "markdown": render_markdown_report(report_date, selected),
        "json": render_json_report(report_date, selected),
    }


def main(
    report_date: str,
    journal_path: str,
    keyword_path: str,
    *,
    priority_keywords: list[str] | None = None,
    lookback_days: int = 7,
    search_client: SearchClient = search_pubmed,
    records_client: RecordsClient = fetch_pubmed_records,
    enrichment_client: EnrichmentClient = enrich_with_crossref,
    summary_adapter: SummaryAdapter | None = None,
    max_selected: int = 10,
    report_dir: str | None = None,
    history_days: int = 7,
) -> dict[str, Any]:
    journals = load_journal_names(journal_path)
    keywords = load_seed_keywords(keyword_path)
    exclude_titles: set[str] | None = None
    if report_dir:
        from pathlib import Path

        exclude_titles = load_recent_report_titles(
            Path(report_dir), report_date, days=history_days
        )
    return run_daily_pipeline(
        report_date=report_date,
        journals=journals,
        keywords=keywords,
        priority_keywords=priority_keywords or [],
        lookback_days=lookback_days,
        search_client=search_client,
        records_client=records_client,
        enrichment_client=enrichment_client,
        summary_adapter=summary_adapter,
        curated_journals=set(journals),
        max_selected=max_selected,
        exclude_titles=exclude_titles,
    )

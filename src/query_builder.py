from __future__ import annotations


def _format_term(value: str) -> str:
    if " " in value:
        return f'"{value}"'

    return value


def _format_terms(values: list[str], field: str | None = None) -> str:
    terms: list[str] = []

    for value in values:
        if field is None:
            terms.append(_format_term(value))
        else:
            terms.append(f'"{value}"[{field}]')

    return " OR ".join(terms)


def build_pubmed_query(
    journals: list[str],
    keywords: list[str],
    priority_keywords: list[str],
    lookback_days: int,
) -> str:
    topic_terms = keywords + priority_keywords
    parts = [
        f"({_format_terms(journals, 'Journal')})",
        f"({_format_terms(topic_terms)})",
        f'("last {lookback_days} day"[PDat] OR "last {lookback_days} days"[PDat])',
    ]

    return " AND ".join(parts)

import os
from dataclasses import dataclass
from typing import Mapping, Protocol


def _clean_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def build_fallback_summary(paper: Mapping[str, str]) -> str:
    title = _clean_text(paper.get("title")) or "Untitled paper"
    abstract = _clean_text(paper.get("abstract")) or "No abstract available."
    return f"{title}: {abstract}"


def build_summary_prompt(paper: Mapping[str, str]) -> dict[str, object]:
    source_data = {
        "title": _clean_text(paper.get("title")),
        "abstract": _clean_text(paper.get("abstract")),
    }
    return {
        "system": "Summarize the paper using only the supplied source data.",
        "paper": dict(source_data),
        "source_data": source_data,
        "user": (
            "Create a concise digest summary from this source data:\n"
            f"title: {source_data['title'] or 'Untitled paper'}\n"
            f"abstract: {source_data['abstract'] or 'No abstract available.'}"
        ),
    }


class SummaryAdapter(Protocol):
    def summarize(self, paper: Mapping[str, str]) -> str: ...


@dataclass(frozen=True)
class FallbackSummaryAdapter:
    def summarize(self, paper: Mapping[str, str]) -> str:
        return build_fallback_summary(paper)


@dataclass(frozen=True)
class AISummaryAdapter:
    provider: str
    api_key: str

    def summarize(self, paper: Mapping[str, str]) -> str:
        raise NotImplementedError(
            f"AI summarization is not implemented for provider '{self.provider}'."
        )


def get_summary_adapter() -> SummaryAdapter:
    provider = _clean_text(os.getenv("SUMMARY_PROVIDER"))
    api_key = _clean_text(os.getenv("SUMMARY_API_KEY"))

    if provider and api_key:
        return AISummaryAdapter(provider=provider, api_key=api_key)
    return FallbackSummaryAdapter()

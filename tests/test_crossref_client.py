import io
from urllib.error import URLError

from src.crossref_client import enrich_with_crossref, merge_crossref_metadata


class FakeResponse:
    def __init__(self, payload: str):
        self._payload = io.StringIO(payload)

    def __enter__(self):
        return self._payload

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeOpener:
    def __init__(self, outcomes):
        self._outcomes = list(outcomes)
        self.calls = []

    def __call__(self, url, *, timeout):
        self.calls.append({"url": url, "timeout": timeout})
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return FakeResponse(outcome)


def test_merge_crossref_metadata_prefers_crossref_doi_and_url():
    base = {"title": "Example", "doi": None, "url": None}
    crossref = {
        "title": ["Example"],
        "DOI": "10.1000/example",
        "URL": "https://doi.org/10.1000/example",
    }

    merged = merge_crossref_metadata(base, crossref)

    assert merged["doi"] == "10.1000/example"
    assert merged["url"] == "https://doi.org/10.1000/example"


def test_merge_crossref_metadata_preserves_base_when_crossref_incomplete():
    base = {
        "title": "Example",
        "doi": "10.1000/base",
        "url": "https://example.com/base",
    }
    crossref = {"DOI": None, "URL": None, "title": []}

    merged = merge_crossref_metadata(base, crossref)

    assert merged == base


def test_merge_crossref_metadata_preserves_base_when_title_mismatch():
    base = {
        "title": "Complex trauma psychotherapy review",
        "doi": "10.1000/base",
        "url": "https://example.com/base",
    }
    crossref = {
        "title": ["Different trial entirely"],
        "DOI": "10.1000/other",
        "URL": "https://doi.org/10.1000/other",
    }

    merged = merge_crossref_metadata(base, crossref)

    assert merged == base


def test_enrich_with_crossref_uses_injected_opener_and_merges_metadata():
    base = {"title": "Example", "doi": None, "url": None}
    opener = FakeOpener(
        [
            '{"message": {"items": [{"title": ["Example"], "DOI": "10.1000/example", "URL": "https://doi.org/10.1000/example"}]}}'
        ]
    )

    enriched = enrich_with_crossref(
        base,
        timeout_seconds=7,
        opener=opener,
    )

    assert enriched["doi"] == "10.1000/example"
    assert enriched["url"] == "https://doi.org/10.1000/example"
    assert opener.calls == [
        {
            "url": "https://api.crossref.org/works?query.title=Example&rows=1",
            "timeout": 7,
        }
    ]


def test_enrich_with_crossref_returns_base_when_fetch_fails():
    base = {
        "title": "Example",
        "doi": "10.1000/base",
        "url": "https://example.com/base",
    }
    opener = FakeOpener([URLError("temporary outage")])

    enriched = enrich_with_crossref(base, opener=opener)

    assert enriched == base


def test_enrich_with_crossref_rejects_mismatched_titles():
    base = {
        "title": "Complex trauma psychotherapy review",
        "doi": "10.1000/base",
        "url": "https://example.com/base",
    }
    opener = FakeOpener(
        [
            '{"message": {"items": [{"title": ["Another paper"], "DOI": "10.1000/other", "URL": "https://doi.org/10.1000/other"}]}}'
        ]
    )

    enriched = enrich_with_crossref(base, opener=opener)

    assert enriched == base

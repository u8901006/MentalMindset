import io
from socket import timeout as SocketTimeout
from urllib.error import URLError
from urllib.request import Request

import pytest

from src.pubmed_client import (
    PubMedArticle,
    fetch_pubmed_records,
    parse_pubmed_article_summaries,
    parse_pubmed_search_ids,
    search_pubmed,
)


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


class RequestCapturingOpener:
    def __init__(self, payload: str):
        self.payload = payload
        self.calls = []

    def __call__(self, request_or_url, *, timeout):
        if isinstance(request_or_url, Request):
            call = {
                "url": request_or_url.full_url,
                "timeout": timeout,
                "method": request_or_url.get_method(),
                "data": request_or_url.data,
            }
        else:
            call = {
                "url": request_or_url,
                "timeout": timeout,
                "method": "GET",
                "data": None,
            }

        self.calls.append(call)
        return FakeResponse(self.payload)


def test_parse_pubmed_search_ids_extracts_identifiers():
    payload = {"esearchresult": {"idlist": ["123", "456"]}}

    assert parse_pubmed_search_ids(payload) == ["123", "456"]


def test_parse_pubmed_article_summaries_returns_structured_records():
    payload = {
        "result": {
            "uids": ["123", "456"],
            "123": {
                "uid": "123",
                "title": "Trauma review",
                "source": "Journal A",
                "pubdate": "2024 Jan",
                "authors": [{"name": "Author One"}, {"name": "Author Two"}],
            },
            "456": {
                "uid": "456",
                "title": "EMDR outcomes",
                "source": "Journal B",
                "pubdate": "2024 Feb",
                "authors": None,
            },
        }
    }

    assert parse_pubmed_article_summaries(payload) == [
        PubMedArticle(
            pubmed_id="123",
            title="Trauma review",
            journal="Journal A",
            source="Journal A",
            pubdate="2024 Jan",
            authors=["Author One", "Author Two"],
            publication_types=[],
            abstract="",
        ),
        PubMedArticle(
            pubmed_id="456",
            title="EMDR outcomes",
            journal="Journal B",
            source="Journal B",
            pubdate="2024 Feb",
            authors=[],
            publication_types=[],
            abstract="",
        ),
    ]


def test_parse_pubmed_article_summaries_maps_pipeline_fields_from_pubmed_shape():
    payload = {
        "result": {
            "uids": ["123"],
            "123": {
                "uid": "123",
                "title": "Complex trauma psychotherapy review",
                "source": "Clin Psychol Rev",
                "fulljournalname": "Clinical Psychology Review",
                "pubdate": "2024 Jan",
                "authors": [{"name": "Author One"}],
                "pubtype": ["Systematic Review", "Meta-Analysis"],
            },
        }
    }

    assert parse_pubmed_article_summaries(payload) == [
        PubMedArticle(
            pubmed_id="123",
            title="Complex trauma psychotherapy review",
            journal="Clinical Psychology Review",
            source="Clin Psychol Rev",
            pubdate="2024 Jan",
            authors=["Author One"],
            publication_types=["Systematic Review", "Meta-Analysis"],
            abstract="",
        )
    ]


def test_search_pubmed_uses_injected_opener_and_returns_ids():
    opener = FakeOpener(['{"esearchresult": {"idlist": ["123", "456"]}}'])

    result = search_pubmed(
        "complex trauma",
        retmax=5,
        timeout_seconds=12,
        retry_attempts=0,
        opener=opener,
    )

    assert result == ["123", "456"]
    assert opener.calls == [
        {
            "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term=complex+trauma&retmax=5",
            "timeout": 12,
        }
    ]


def test_search_pubmed_uses_post_for_oversized_query_params():
    opener = RequestCapturingOpener('{"esearchresult": {"idlist": ["123"]}}')
    long_query = "trauma " * 800

    result = search_pubmed(
        long_query,
        timeout_seconds=12,
        retry_attempts=0,
        opener=opener,
    )

    assert result == ["123"]
    assert len(opener.calls) == 1
    assert opener.calls[0]["method"] == "POST"
    assert (
        opener.calls[0]["url"]
        == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    )
    assert opener.calls[0]["data"] is not None


def test_fetch_pubmed_records_uses_injected_opener_and_returns_articles():
    opener = FakeOpener(
        [
            '{"result": {"uids": ["123"], "123": {"uid": "123", "title": "Trauma review", "source": "Journal A", "pubdate": "2024 Jan", "authors": [{"name": "Author One"}]}}}'
        ]
    )

    result = fetch_pubmed_records(
        ["123"],
        timeout_seconds=9,
        retry_attempts=0,
        opener=opener,
    )

    assert result == [
        PubMedArticle(
            pubmed_id="123",
            title="Trauma review",
            journal="Journal A",
            source="Journal A",
            pubdate="2024 Jan",
            authors=["Author One"],
            publication_types=[],
            abstract="",
        )
    ]
    assert opener.calls == [
        {
            "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=123",
            "timeout": 9,
        }
    ]


def test_fetch_pubmed_records_returns_empty_without_calling_opener():
    opener = FakeOpener([])

    result = fetch_pubmed_records([], opener=opener)

    assert result == []
    assert opener.calls == []


def test_search_pubmed_retries_after_temporary_failures_then_succeeds():
    opener = FakeOpener(
        [
            URLError("temporary outage"),
            SocketTimeout("timed out"),
            '{"esearchresult": {"idlist": ["789"]}}',
        ]
    )

    result = search_pubmed(
        "ptsd",
        timeout_seconds=4,
        retry_attempts=2,
        opener=opener,
    )

    assert result == ["789"]
    assert len(opener.calls) == 3


def test_search_pubmed_raises_after_retry_exhaustion():
    opener = FakeOpener([URLError("down"), URLError("still down")])

    with pytest.raises(URLError):
        search_pubmed(
            "ptsd",
            timeout_seconds=4,
            retry_attempts=1,
            opener=opener,
        )

    assert len(opener.calls) == 2

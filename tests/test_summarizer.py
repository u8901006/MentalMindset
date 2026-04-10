import pytest

from src.summarizer import (
    AISummaryAdapter,
    FallbackSummaryAdapter,
    build_fallback_summary,
    build_summary_prompt,
    get_summary_adapter,
)


def test_build_fallback_summary_returns_basic_digest_text():
    paper = {"title": "Example study", "abstract": "Short abstract."}

    summary = build_fallback_summary(paper)

    assert "Example study" in summary


def test_build_fallback_summary_uses_defaults_for_missing_fields():
    summary = build_fallback_summary({})

    assert summary == "Untitled paper: No abstract available."


def test_build_summary_prompt_keeps_source_data_separate_from_rendered_text():
    prompt = build_summary_prompt(
        {"title": "  Example study  ", "abstract": " Short abstract. "}
    )

    assert (
        prompt["system"] == "Summarize the paper using only the supplied source data."
    )
    assert prompt["source_data"] == {
        "title": "Example study",
        "abstract": "Short abstract.",
    }
    assert prompt["source_data"] is not prompt["paper"]
    assert prompt["paper"] == prompt["source_data"]
    assert "Example study" in prompt["user"]
    assert "Short abstract." in prompt["user"]


def test_get_summary_adapter_returns_fallback_without_complete_ai_configuration(
    monkeypatch,
):
    monkeypatch.delenv("SUMMARY_PROVIDER", raising=False)
    monkeypatch.delenv("SUMMARY_API_KEY", raising=False)

    assert isinstance(get_summary_adapter(), FallbackSummaryAdapter)

    monkeypatch.setenv("SUMMARY_PROVIDER", "openai")
    monkeypatch.delenv("SUMMARY_API_KEY", raising=False)

    assert isinstance(get_summary_adapter(), FallbackSummaryAdapter)


def test_get_summary_adapter_returns_ai_adapter_and_raises_until_implemented(
    monkeypatch,
):
    monkeypatch.setenv("SUMMARY_PROVIDER", "openai")
    monkeypatch.setenv("SUMMARY_API_KEY", "test-key")

    adapter = get_summary_adapter()

    assert isinstance(adapter, AISummaryAdapter)
    with pytest.raises(NotImplementedError):
        adapter.summarize({"title": "Example study", "abstract": "Short abstract."})

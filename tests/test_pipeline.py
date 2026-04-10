from src.pipeline import run_daily_pipeline, select_top_papers
from src.pubmed_client import PubMedArticle


def test_select_top_papers_limits_output_count():
    papers = [{"title": f"Paper {i}", "score": i} for i in range(20)]

    selected = select_top_papers(papers, max_selected=5)

    assert len(selected) == 5


def test_run_daily_pipeline_returns_markdown_and_json_outputs():
    journals = ["Clinical Psychology Review"]
    keywords = ["complex trauma"]
    priority_keywords = ["PTSD"]

    def search_client(query: str) -> list[str]:
        assert "Clinical Psychology Review" in query
        return ["1"]

    def records_client(identifiers: list[str]) -> list[dict[str, object]]:
        assert identifiers == ["1"]
        return [
            {
                "pmid": "1",
                "title": "Paper A",
                "journal": "Clinical Psychology Review",
                "publication_types": ["Review"],
                "matched_keywords": ["complex trauma", "PTSD"],
                "abstract": "Findings about treatment outcomes.",
            }
        ]

    def enrichment_client(paper: dict[str, object]) -> dict[str, object]:
        return dict(paper, doi="10.1000/example")

    outputs = run_daily_pipeline(
        report_date="2026-04-10",
        journals=journals,
        keywords=keywords,
        priority_keywords=priority_keywords,
        lookback_days=7,
        search_client=search_client,
        records_client=records_client,
        enrichment_client=enrichment_client,
        curated_journals=set(journals),
    )

    assert "Paper A" in outputs["markdown"]
    assert outputs["json"]["items"] == [
        {
            "title": "Paper A",
            "journal": "Clinical Psychology Review",
        }
    ]


def test_run_daily_pipeline_accepts_real_pubmed_article_records():
    journals = ["Clinical Psychology Review"]

    def records_client(identifiers: list[str]) -> list[PubMedArticle]:
        assert identifiers == ["1"]
        return [
            PubMedArticle(
                pubmed_id="1",
                title="Paper A",
                journal="Clinical Psychology Review",
                source="Clin Psychol Rev",
                pubdate="2026 Apr",
                authors=["Author One"],
                publication_types=["Systematic Review"],
                abstract="complex trauma treatment outcomes",
            )
        ]

    outputs = run_daily_pipeline(
        report_date="2026-04-10",
        journals=journals,
        keywords=["complex trauma"],
        priority_keywords=["PTSD"],
        lookback_days=7,
        search_client=lambda query: ["1"],
        records_client=records_client,
        enrichment_client=lambda paper: paper,
        curated_journals=set(journals),
    )

    assert outputs["json"]["items"][0]["journal"] == "Clinical Psychology Review"
    assert "Unknown journal" not in outputs["markdown"]


def test_run_daily_pipeline_uses_fallback_summary_by_default_even_with_ai_env_vars(
    monkeypatch,
):
    journals = ["Clinical Psychology Review"]

    monkeypatch.setenv("SUMMARY_PROVIDER", "openai")
    monkeypatch.setenv("SUMMARY_API_KEY", "test-key")

    def search_client(query: str) -> list[str]:
        assert "Clinical Psychology Review" in query
        return ["1"]

    def records_client(identifiers: list[str]) -> list[dict[str, object]]:
        assert identifiers == ["1"]
        return [
            {
                "pmid": "1",
                "title": "Paper A",
                "journal": "Clinical Psychology Review",
                "publication_types": ["Review"],
                "abstract": "Findings about treatment outcomes.",
            }
        ]

    outputs = run_daily_pipeline(
        report_date="2026-04-10",
        journals=journals,
        keywords=["complex trauma"],
        priority_keywords=["PTSD"],
        lookback_days=7,
        search_client=search_client,
        records_client=records_client,
        enrichment_client=lambda paper: paper,
        curated_journals=set(journals),
    )

    assert outputs["papers"][0]["summary"] == (
        "Paper A: Findings about treatment outcomes."
    )

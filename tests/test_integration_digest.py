from src.pipeline import run_daily_pipeline
from src.pubmed_client import PubMedArticle
from src.report_generator import render_json_report, render_markdown_report


def test_json_report_handles_empty_selection():
    payload = render_json_report("2026-04-10", [])

    assert payload["sources"]["selected_count"] == 0
    assert payload["delivery"]["email"]["enabled"] is False


def test_pipeline_empty_results_still_produce_valid_markdown_and_json():
    outputs = run_daily_pipeline(
        report_date="2026-04-10",
        journals=["Clinical Psychology Review"],
        keywords=["complex trauma"],
        priority_keywords=["PTSD"],
        lookback_days=7,
        search_client=lambda query: [],
        records_client=lambda identifiers: [],
        enrichment_client=lambda paper: paper,
        curated_journals={"Clinical Psychology Review"},
    )

    assert outputs["markdown"] == render_markdown_report("2026-04-10", [])
    assert outputs["json"]["sources"]["selected_count"] == 0
    assert outputs["json"]["items"] == []
    assert outputs["json"]["preview"] == "No papers selected"


def test_pubmed_article_records_flow_through_pipeline_with_real_journal_name():
    outputs = run_daily_pipeline(
        report_date="2026-04-10",
        journals=["Clinical Psychology Review"],
        keywords=["complex trauma"],
        priority_keywords=["PTSD"],
        lookback_days=7,
        search_client=lambda query: ["123"],
        records_client=lambda identifiers: [
            PubMedArticle(
                pubmed_id="123",
                title="Complex trauma psychotherapy review",
                journal="Clinical Psychology Review",
                source="Clin Psychol Rev",
                pubdate="2024 Jan",
                authors=["Author One"],
                publication_types=["Review"],
                abstract="This review covers complex trauma and PTSD outcomes.",
            )
        ],
        enrichment_client=lambda paper: paper,
        curated_journals={"Clinical Psychology Review"},
    )

    assert outputs["json"]["items"] == [
        {
            "title": "Complex trauma psychotherapy review",
            "journal": "Clinical Psychology Review",
        }
    ]
    assert outputs["papers"][0]["score"] == 8

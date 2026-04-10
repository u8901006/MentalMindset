from pathlib import Path

import src.main as main_module
from src.main import build_report_paths


def test_build_report_paths_targets_markdown_and_json():
    md_path, json_path = build_report_paths(Path("reports"), "2026-04-10")

    assert md_path.name == "2026-04-10.md"
    assert json_path.name == "2026-04-10.json"


def test_main_writes_markdown_and_json_files(tmp_path, monkeypatch):
    outputs = {
        "markdown": "# Daily Report\n\n心理摘要",
        "json": {"subject": "每日研究", "items": [{"title": "心理摘要"}]},
    }

    def fake_run_pipeline(
        *,
        report_date: str,
        journal_path: str,
        keyword_path: str,
        lookback_days: int,
        max_selected: int,
        search_client,
        records_client,
        enrichment_client,
    ):
        assert report_date == "2026-04-10"
        assert Path(journal_path) == (
            Path(main_module.__file__).resolve().parents[1]
            / main_module.DEFAULT_JOURNAL_PATH
        )
        assert Path(keyword_path) == (
            Path(main_module.__file__).resolve().parents[1]
            / main_module.DEFAULT_KEYWORD_PATH
        )
        assert lookback_days == 1
        assert max_selected == 10
        return outputs

    monkeypatch.setattr(main_module, "run_pipeline", fake_run_pipeline)

    exit_code = main_module.main(["2026-04-10", "--output-dir", str(tmp_path)])

    markdown_path = tmp_path / "2026-04-10.md"
    json_path = tmp_path / "2026-04-10.json"

    assert exit_code == 0
    assert markdown_path.read_text(encoding="utf-8") == outputs["markdown"]
    assert '"每日研究"' in json_path.read_text(encoding="utf-8")
    assert '"心理摘要"' in json_path.read_text(encoding="utf-8")


def test_main_writes_daily_html_report(tmp_path, monkeypatch):
    outputs = {
        "markdown": "# Report",
        "json": {
            "subject": "Daily report",
            "items": [{"title": "Paper A", "journal": "J"}],
        },
    }

    captured: dict[str, object] = {}

    def fake_render_daily_report_html(
        report_date: str, payload: dict[str, object]
    ) -> str:
        captured["report_date"] = report_date
        captured["payload"] = payload
        return "<html><body>expected report</body></html>"

    monkeypatch.setattr(main_module, "run_pipeline", lambda **kwargs: outputs)
    monkeypatch.setattr(
        main_module,
        "render_daily_report_html",
        fake_render_daily_report_html,
    )

    exit_code = main_module.main(["2026-04-10", "--output-dir", str(tmp_path)])

    assert exit_code == 0
    assert captured == {
        "report_date": "2026-04-10",
        "payload": outputs["json"],
    }
    assert (tmp_path / "2026-04-10.html").read_text(encoding="utf-8") == (
        "<html><body>expected report</body></html>"
    )


def test_main_rebuilds_index_html(tmp_path, monkeypatch):
    outputs = {
        "markdown": "# Report",
        "json": {"subject": "Daily report", "items": []},
    }

    (tmp_path / "2026-04-08.html").write_text("older", encoding="utf-8")
    (tmp_path / "2026-04-09.html").write_text("old", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_render_index_html(reports: list[dict[str, str]]) -> str:
        captured["reports"] = reports
        return "<html><body>rebuilt index</body></html>"

    monkeypatch.setattr(main_module, "run_pipeline", lambda **kwargs: outputs)
    monkeypatch.setattr(
        main_module,
        "render_daily_report_html",
        lambda report_date, payload: "<html><body>daily report</body></html>",
    )
    monkeypatch.setattr(main_module, "render_index_html", fake_render_index_html)

    exit_code = main_module.main(["2026-04-10", "--output-dir", str(tmp_path)])

    html = (tmp_path.parent / "index.html").read_text(encoding="utf-8")

    assert exit_code == 0
    assert (tmp_path / "2026-04-10.html").read_text(encoding="utf-8") == (
        "<html><body>daily report</body></html>"
    )
    assert captured == {
        "reports": [
            {"date": "2026-04-10", "href": "reports/2026-04-10.html"},
            {"date": "2026-04-09", "href": "reports/2026-04-09.html"},
            {"date": "2026-04-08", "href": "reports/2026-04-08.html"},
        ]
    }
    assert html == "<html><body>rebuilt index</body></html>"


def test_main_uses_settings_to_configure_runtime_clients_and_limits(
    tmp_path, monkeypatch
):
    outputs = {"markdown": "# Daily Report", "json": {"items": []}}
    calls: dict[str, object] = {}

    class FakeSettings:
        enable_digest_logging = False
        lookback_days = 3
        max_selected_papers = 4
        request_timeout_seconds = 17
        retry_attempts = 5

    def fake_run_pipeline(
        *,
        report_date: str,
        journal_path: str,
        keyword_path: str,
        lookback_days: int,
        max_selected: int,
        search_client,
        records_client,
        enrichment_client,
    ):
        calls["report_date"] = report_date
        calls["journal_path"] = journal_path
        calls["keyword_path"] = keyword_path
        calls["lookback_days"] = lookback_days
        calls["max_selected"] = max_selected
        calls["search_result"] = search_client("query")
        calls["records_result"] = records_client(["1"])
        calls["enrichment_result"] = enrichment_client({"title": "Paper"})
        return outputs

    monkeypatch.setattr(main_module, "Settings", FakeSettings)
    monkeypatch.setattr(main_module, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(
        main_module,
        "search_pubmed",
        lambda query, *, timeout_seconds, retry_attempts: {
            "query": query,
            "timeout_seconds": timeout_seconds,
            "retry_attempts": retry_attempts,
        },
    )
    monkeypatch.setattr(
        main_module,
        "fetch_pubmed_records",
        lambda identifiers, *, timeout_seconds, retry_attempts: {
            "identifiers": identifiers,
            "timeout_seconds": timeout_seconds,
            "retry_attempts": retry_attempts,
        },
    )
    monkeypatch.setattr(
        main_module,
        "enrich_with_crossref",
        lambda paper, *, timeout_seconds: {
            "paper": paper,
            "timeout_seconds": timeout_seconds,
        },
    )

    exit_code = main_module.main(["2026-04-10", "--output-dir", str(tmp_path)])

    assert exit_code == 0
    assert calls == {
        "report_date": "2026-04-10",
        "journal_path": str(
            Path(main_module.__file__).resolve().parents[1]
            / main_module.DEFAULT_JOURNAL_PATH
        ),
        "keyword_path": str(
            Path(main_module.__file__).resolve().parents[1]
            / main_module.DEFAULT_KEYWORD_PATH
        ),
        "lookback_days": 3,
        "max_selected": 4,
        "search_result": {
            "query": "query",
            "timeout_seconds": 17,
            "retry_attempts": 5,
        },
        "records_result": {
            "identifiers": ["1"],
            "timeout_seconds": 17,
            "retry_attempts": 5,
        },
        "enrichment_result": {
            "paper": {"title": "Paper"},
            "timeout_seconds": 17,
        },
    }


def test_main_resolves_default_input_paths_from_non_root_cwd(tmp_path, monkeypatch):
    outputs = {"markdown": "# Daily Report", "json": {"items": []}}
    captured: dict[str, str] = {}

    class FakeSettings:
        enable_digest_logging = False
        lookback_days = 1
        max_selected_papers = 10
        request_timeout_seconds = 30
        retry_attempts = 2

    def fake_run_pipeline(**kwargs):
        captured["journal_path"] = kwargs["journal_path"]
        captured["keyword_path"] = kwargs["keyword_path"]
        return outputs

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main_module, "Settings", FakeSettings)
    monkeypatch.setattr(main_module, "run_pipeline", fake_run_pipeline)

    exit_code = main_module.main(["2026-04-10", "--output-dir", str(tmp_path)])

    assert exit_code == 0
    assert Path(captured["journal_path"]) == (
        Path(main_module.__file__).resolve().parents[1]
        / main_module.DEFAULT_JOURNAL_PATH
    )
    assert Path(captured["keyword_path"]) == (
        Path(main_module.__file__).resolve().parents[1]
        / main_module.DEFAULT_KEYWORD_PATH
    )

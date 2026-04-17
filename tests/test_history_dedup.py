from pathlib import Path

from src.history_dedup import load_recent_report_titles


def test_load_recent_report_titles_reads_items_from_recent_json(tmp_path):
    (tmp_path / "2026-04-08.json").write_text(
        '{"items": [{"title": "Paper A", "journal": "J"}]}', encoding="utf-8"
    )
    (tmp_path / "2026-04-09.json").write_text(
        '{"items": [{"title": "Paper B", "journal": "J"}]}', encoding="utf-8"
    )

    titles = load_recent_report_titles(tmp_path, "2026-04-10", days=7)

    assert "paper a" in titles
    assert "paper b" in titles


def test_load_recent_report_titles_excludes_current_date(tmp_path):
    (tmp_path / "2026-04-10.json").write_text(
        '{"items": [{"title": "Paper A", "journal": "J"}]}', encoding="utf-8"
    )

    titles = load_recent_report_titles(tmp_path, "2026-04-10", days=7)

    assert "paper a" not in titles


def test_load_recent_report_titles_excludes_older_than_window(tmp_path):
    (tmp_path / "2026-04-02.json").write_text(
        '{"items": [{"title": "Old Paper", "journal": "J"}]}', encoding="utf-8"
    )

    titles = load_recent_report_titles(tmp_path, "2026-04-10", days=7)

    assert "old paper" not in titles


def test_load_recent_report_titles_returns_empty_when_no_reports(tmp_path):
    titles = load_recent_report_titles(tmp_path, "2026-04-10", days=7)

    assert titles == set()


def test_load_recent_report_titles_skips_malformed_json(tmp_path):
    (tmp_path / "2026-04-09.json").write_text("not json", encoding="utf-8")
    (tmp_path / "2026-04-08.json").write_text(
        '{"items": [{"title": "Good Paper", "journal": "J"}]}', encoding="utf-8"
    )

    titles = load_recent_report_titles(tmp_path, "2026-04-10", days=7)

    assert "good paper" in titles


def test_load_recent_report_titles_skips_non_date_filenames(tmp_path):
    (tmp_path / "notes.json").write_text(
        '{"items": [{"title": "Note", "journal": "J"}]}', encoding="utf-8"
    )

    titles = load_recent_report_titles(tmp_path, "2026-04-10", days=7)

    assert "note" not in titles

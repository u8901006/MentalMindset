from pathlib import Path

from src.main import build_html_report_path, build_site_index_path


def test_html_output_paths_target_daily_report_and_site_index() -> None:
    assert build_html_report_path(Path("reports"), "2026-04-10") == Path(
        "reports/2026-04-10.html"
    )
    assert build_site_index_path(Path(".")) == Path("index.html")

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

from src.config import Settings
from src.crossref_client import enrich_with_crossref
from src.html_renderer import render_daily_report_html, render_index_html
from src.pubmed_client import fetch_pubmed_records, search_pubmed
from src.pipeline import main as run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOURNAL_PATH = "data/journals/clinical_psychotherapy_trauma_q1_q2.md"
DEFAULT_KEYWORD_PATH = "data/keywords/search_keywords_topics_therapy.md"


def build_report_paths(output_dir: Path, report_date: str) -> tuple[Path, Path]:
    return output_dir / f"{report_date}.md", output_dir / f"{report_date}.json"


def build_html_report_path(output_dir: Path, report_date: str) -> Path:
    return output_dir / f"{report_date}.html"


def build_site_index_path(site_dir: Path) -> Path:
    return site_dir / "index.html"


def rebuild_site_index(report_dir: Path, site_root: Path) -> None:
    reports = [
        {"date": path.stem, "href": f"reports/{path.name}"}
        for path in sorted(report_dir.glob("*.html"), reverse=True)
    ]
    build_site_index_path(site_root).write_text(
        render_index_html(reports),
        encoding="utf-8",
    )


def write_report_outputs(
    output_dir: Path,
    report_date: str,
    markdown: str,
    payload: dict[str, Any],
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path, json_path = build_report_paths(output_dir, report_date)
    markdown_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return markdown_path, json_path


def _resolve_default_input_path(path_value: str, default_relative_path: str) -> str:
    if Path(path_value) == Path(default_relative_path):
        return str((PROJECT_ROOT / default_relative_path).resolve())
    return path_value


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily research report.")
    parser.add_argument(
        "report_date",
        nargs="?",
        default=date.today().isoformat(),
        help="Report date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--journal-path",
        default=DEFAULT_JOURNAL_PATH,
        help="Path to the journal list markdown file.",
    )
    parser.add_argument(
        "--keyword-path",
        default=DEFAULT_KEYWORD_PATH,
        help="Path to the keyword list markdown file.",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory where generated reports are written.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    settings = Settings()
    journal_path = _resolve_default_input_path(
        args.journal_path,
        DEFAULT_JOURNAL_PATH,
    )
    keyword_path = _resolve_default_input_path(
        args.keyword_path,
        DEFAULT_KEYWORD_PATH,
    )
    outputs = run_pipeline(
        report_date=args.report_date,
        journal_path=journal_path,
        keyword_path=keyword_path,
        lookback_days=settings.lookback_days,
        max_selected=settings.max_selected_papers,
        report_dir=args.output_dir,
        search_client=lambda query: search_pubmed(
            query,
            timeout_seconds=settings.request_timeout_seconds,
            retry_attempts=settings.retry_attempts,
        ),
        records_client=lambda identifiers: fetch_pubmed_records(
            identifiers,
            timeout_seconds=settings.request_timeout_seconds,
            retry_attempts=settings.retry_attempts,
        ),
        enrichment_client=lambda paper: enrich_with_crossref(
            paper,
            timeout_seconds=settings.request_timeout_seconds,
        ),
    )
    if settings.enable_digest_logging:
        print(
            f"Generated report for {args.report_date} using {journal_path} and {keyword_path}"
        )
    write_report_outputs(
        Path(args.output_dir),
        args.report_date,
        outputs["markdown"],
        outputs["json"],
    )
    output_dir = Path(args.output_dir)
    html_output_path = build_html_report_path(output_dir, args.report_date)
    html_output_path.parent.mkdir(parents=True, exist_ok=True)
    html_output_path.write_text(
        render_daily_report_html(args.report_date, outputs["json"]),
        encoding="utf-8",
    )
    rebuild_site_index(output_dir, output_dir.parent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

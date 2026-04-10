from __future__ import annotations

from typing import Any


def _paper_to_item(paper: dict[str, Any]) -> dict[str, str]:
    return {
        "title": str(paper.get("title") or "Untitled"),
        "journal": str(paper.get("journal") or "Unknown journal"),
    }


def render_markdown_report(report_date: str, papers: list[dict[str, Any]]) -> str:
    lines = [f"# Daily Research Report - {report_date}", ""]
    for paper in papers:
        item = _paper_to_item(paper)
        lines.append(f"- {item['title']} ({item['journal']})")
    return "\n".join(lines)


def render_json_report(
    report_date: str, papers: list[dict[str, Any]]
) -> dict[str, Any]:
    items = [_paper_to_item(paper) for paper in papers]
    preview = items[0]["title"] if items else "No papers selected"
    journals = sorted({item["journal"] for item in items})

    return {
        "subject": f"Daily research report for {report_date}",
        "preview": preview,
        "sources": {
            "journals": journals,
            "selected_count": len(items),
        },
        "items": items,
        "delivery": {
            "email": {
                "enabled": False,
                "to": [],
            },
            "push": {
                "enabled": False,
            },
        },
    }

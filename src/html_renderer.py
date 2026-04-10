from __future__ import annotations

from html import escape
from typing import Any

STYLESHEET_TAG = '<link rel="stylesheet" href="assets/styles.css">'

_DAILY_STYLESHEET_TAG = '<link rel="stylesheet" href="../assets/styles.css">'

SITE_TITLE = "MentalMindset"
SITE_SUBTITLE = "心理研究日報"
SITE_TAGLINE = "每日自動更新"

_ARCHIVE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title} · {subtitle}</title>
{stylesheet}
</head>
<body>
<div class="container">
  <div class="logo">🧠</div>
  <h1>{title}</h1>
  <p class="subtitle">{subtitle} · {tagline}</p>
  <p class="count">共 {count} 期日報</p>
  <ul>{links}</ul>
  <footer>
    <p>Powered by PubMed + Crossref · <a href="https://github.com/u8901006/MentalMindset">GitHub</a></p>
  </footer>
</div>
</body>
</html>"""

_DAILY_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title} · {subtitle} · {date_display}</title>
<meta name="description" content="{date_display} {subtitle}，由 AI 自動彙整 PubMed 最新論文"/>
{stylesheet}
</head>
<body>
<div class="container">
  <header>
    <div class="logo">🧠</div>
    <div class="header-text">
      <h1>{title} · {subtitle}</h1>
      <p class="subtitle">{date_display} · {paper_count} 篇文獻</p>
    </div>
  </header>
  <ul>{papers}</ul>
  <footer>
    <span>資料來源：PubMed · Crossref</span>
    <span><a href="../index.html">返回首頁</a></span>
  </footer>
</div>
</body>
</html>"""


def _format_date_display(date_str: str) -> str:
    try:
        parts = date_str.split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        weekdays = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
        from datetime import date

        wd = weekdays[date(y, m, d).weekday()]
        return f"{y}年{m}月{d}日（{wd}）"
    except Exception:
        return date_str


def render_index_html(reports: list[dict[str, str]]) -> str:
    link_items = "".join(
        f'<li><a href="{escape(str(r.get("href") or ""))}">📅 {_format_date_display(escape(str(r.get("date") or "")))}</a></li>'
        for r in reports
    )
    return _ARCHIVE_TEMPLATE.format(
        title=SITE_TITLE,
        subtitle=SITE_SUBTITLE,
        tagline=SITE_TAGLINE,
        count=len(reports),
        links=link_items,
        stylesheet=STYLESHEET_TAG,
    )


def render_daily_report_html(report_date: str, payload: dict[str, Any]) -> str:
    safe_date = escape(report_date)
    date_display = _format_date_display(report_date)
    items = payload.get("items") or []
    paper_count = len(items)

    paper_items = "".join(
        f'<li><a href="{escape(str(item.get("doi_url") or "#"))}">'
        f"📄 {escape(str(item.get('title') or 'Untitled'))} — "
        f"{escape(str(item.get('journal') or ''))}</a></li>"
        for item in items
    )

    return _DAILY_TEMPLATE.format(
        title=SITE_TITLE,
        subtitle=SITE_SUBTITLE,
        date_display=date_display,
        paper_count=paper_count,
        papers=paper_items,
        stylesheet=_DAILY_STYLESHEET_TAG,
    )

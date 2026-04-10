from src.html_renderer import (
    SITE_SUBTITLE,
    SITE_TAGLINE,
    SITE_TITLE,
    render_daily_report_html,
    render_index_html,
)


def test_render_daily_report_html_includes_title_date_and_papers():
    payload = {
        "subject": "Daily research report for 2026-04-10",
        "items": [{"title": "Paper A", "journal": "Clinical Psychology Review"}],
    }

    html = render_daily_report_html("2026-04-10", payload)

    assert "Paper A" in html
    assert "Clinical Psychology Review" in html
    assert "2026年4月10日" in html
    assert "1 篇文獻" in html


def test_render_daily_report_html_escapes_payload_text():
    payload = {
        "subject": "Daily <report> & review",
        "items": [
            {
                "title": "Paper <A> & B",
                "journal": "Clinical > Psychology & Review",
            }
        ],
    }

    html = render_daily_report_html("2026-04-10", payload)

    assert "Paper &lt;A&gt; &amp; B" in html
    assert "Clinical &gt; Psychology &amp; Review" in html


def test_render_index_html_lists_report_links_and_total_count():
    reports = [{"date": "2026-04-10", "href": "reports/2026-04-10.html"}]

    html = render_index_html(reports)

    assert "共 1 期日報" in html
    assert "reports/2026-04-10.html" in html
    assert "2026年4月10日" in html


def test_render_index_html_escapes_date_and_href():
    reports = [
        {
            "date": '2026-04-10 <draft> & "review"',
            "href": 'reports/2026-04-10.html?topic=<stress>&quote="daily"',
        }
    ]

    html = render_index_html(reports)

    assert "reports/2026-04-10.html?topic=&lt;stress&gt;" in html


def test_rendered_html_links_shared_stylesheet():
    html = render_index_html([])

    assert "assets/styles.css" in html


def test_daily_report_links_stylesheet_with_relative_path():
    payload = {"items": []}

    html = render_daily_report_html("2026-04-10", payload)

    assert "../assets/styles.css" in html


def test_index_html_matches_reference_archive_language():
    html = render_index_html(
        [{"date": "2026-04-10", "href": "reports/2026-04-10.html"}]
    )

    assert SITE_TITLE in html
    assert SITE_SUBTITLE in html
    assert SITE_TAGLINE in html


def test_daily_report_html_contains_return_link():
    payload = {"items": []}

    html = render_daily_report_html("2026-04-10", payload)

    assert "返回首頁" in html
    assert "index.html" in html


def test_daily_report_html_shows_zero_papers_gracefully():
    payload = {"items": []}

    html = render_daily_report_html("2026-04-10", payload)

    assert "0 篇文獻" in html

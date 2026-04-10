from src.report_generator import render_json_report, render_markdown_report


def test_report_renderers_include_delivery_sections():
    papers = [{"title": "Example study", "journal": "Clinical Psychology Review"}]

    markdown = render_markdown_report("2026-04-10", papers)
    payload = render_json_report("2026-04-10", papers)

    assert "Example study" in markdown
    assert payload["subject"] == "Daily research report for 2026-04-10"
    assert payload["preview"] == "Example study"
    assert payload["sources"] == {
        "journals": ["Clinical Psychology Review"],
        "selected_count": 1,
    }
    assert payload["items"] == [
        {
            "title": "Example study",
            "journal": "Clinical Psychology Review",
        }
    ]
    assert payload["delivery"] == {
        "email": {"enabled": False, "to": []},
        "push": {"enabled": False},
    }

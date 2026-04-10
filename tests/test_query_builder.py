from src.query_builder import build_pubmed_query


def test_query_builder_includes_journals_topics_and_date_window():
    query = build_pubmed_query(
        journals=["Clinical Psychology Review"],
        keywords=["complex trauma", "EMDR"],
        priority_keywords=["PTSD"],
        lookback_days=1,
    )

    assert query == (
        '("Clinical Psychology Review"[Journal]) '
        'AND ("complex trauma" OR EMDR OR PTSD) '
        'AND ("last 1 day"[PDat] OR "last 1 days"[PDat])'
    )

from src.deduplication import deduplicate_papers, normalize_title_text


def test_deduplicate_papers_removes_duplicate_doi_entries():
    papers = [
        {"title": "A", "doi": "10.1/a", "pmid": "1"},
        {"title": "A duplicate", "doi": "10.1/a", "pmid": "2"},
    ]

    result = deduplicate_papers(papers)

    assert len(result) == 1


def test_deduplicate_papers_removes_duplicate_pmid_when_later_doi_missing():
    papers = [
        {"title": "A", "doi": "10.1/a", "pmid": "1"},
        {"title": "A later copy", "doi": None, "pmid": "1"},
    ]

    result = deduplicate_papers(papers)

    assert len(result) == 1


def test_deduplicate_papers_keeps_later_paper_with_new_doi_despite_matching_pmid():
    papers = [
        {"title": "A", "doi": "10.1/a", "pmid": "1"},
        {"title": "B", "doi": "10.1/b", "pmid": "1"},
    ]

    result = deduplicate_papers(papers)

    assert len(result) == 2
    assert [paper["doi"] for paper in result] == ["10.1/a", "10.1/b"]


def test_normalize_title_text_collapses_whitespace():
    assert normalize_title_text("  A\n   spaced\t title  ") == "A spaced title"

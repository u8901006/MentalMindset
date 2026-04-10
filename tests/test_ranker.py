from src.ranker import rank_top_papers, score_paper


def test_score_paper_prioritizes_review_types_and_curated_journals():
    paper = {
        "publication_types": ["Meta-Analysis"],
        "journal": "Clinical Psychology Review",
        "matched_keywords": ["complex trauma", "PTSD"],
    }

    score = score_paper(paper, curated_journals={"Clinical Psychology Review"})

    assert score == 10


def test_score_paper_uses_only_the_strongest_study_type_bonus():
    paper = {
        "publication_types": ["Review", "Meta-Analysis"],
        "journal": "Other Journal",
        "matched_keywords": ["complex trauma"],
    }

    score = score_paper(paper)

    assert score == 6


def test_rank_top_papers_uses_title_for_deterministic_tie_ordering():
    papers = [
        {
            "title": "beta",
            "publication_types": ["Review"],
            "journal": "Other Journal",
            "matched_keywords": ["complex trauma"],
        },
        {
            "title": "Alpha",
            "publication_types": ["Review"],
            "journal": "Other Journal",
            "matched_keywords": ["complex trauma"],
        },
    ]

    ranked = rank_top_papers(papers, limit=2)

    assert [paper["title"] for paper in ranked] == ["Alpha", "beta"]


def test_rank_top_papers_returns_top_n_items_from_larger_list():
    papers = [
        {
            "title": "Lower",
            "publication_types": ["Editorial"],
            "journal": "Other Journal",
            "matched_keywords": [],
        },
        {
            "title": "Highest",
            "publication_types": ["Randomized Controlled Trial"],
            "journal": "Clinical Psychology Review",
            "matched_keywords": ["complex trauma", "PTSD"],
        },
        {
            "title": "Middle",
            "publication_types": ["Systematic Review"],
            "journal": "Other Journal",
            "matched_keywords": ["complex trauma"],
        },
        {
            "title": "Second",
            "publication_types": ["Review"],
            "journal": "Clinical Psychology Review",
            "matched_keywords": ["complex trauma", "PTSD"],
        },
    ]

    ranked = rank_top_papers(
        papers,
        curated_journals={"Clinical Psychology Review"},
        limit=3,
    )

    assert [paper["title"] for paper in ranked] == ["Highest", "Second", "Middle"]

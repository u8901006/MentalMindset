from src.input_parser import load_journal_names, load_seed_keywords


def test_parsers_extract_curated_inputs():
    journals = load_journal_names(
        "data/journals/clinical_psychotherapy_trauma_q1_q2.md"
    )
    keywords = load_seed_keywords("data/keywords/search_keywords_topics_therapy.md")

    assert "Clinical Psychology Review" in journals
    assert "complex trauma" in keywords
    assert "EMDR" in keywords
    assert "cancer patients" not in keywords
    assert "adolescents" not in keywords
    assert "children" not in keywords

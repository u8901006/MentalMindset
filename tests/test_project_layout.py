from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_input_files_exist_in_data_directories():
    assert (
        PROJECT_ROOT / "data/journals/clinical_psychotherapy_trauma_q1_q2.md"
    ).exists()
    assert (PROJECT_ROOT / "data/keywords/search_keywords_topics_therapy.md").exists()


def test_input_files_exist_in_data_directories_from_non_root_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert (
        PROJECT_ROOT / "data/journals/clinical_psychotherapy_trauma_q1_q2.md"
    ).exists()
    assert (PROJECT_ROOT / "data/keywords/search_keywords_topics_therapy.md").exists()

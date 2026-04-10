from pathlib import Path


def test_daily_digest_workflow_exists():
    assert Path(".github/workflows/daily-digest.yml").exists()


def test_daily_digest_workflow_contract():
    workflow = Path(".github/workflows/daily-digest.yml").read_text(encoding="utf-8")

    assert "cron: '0 6 * * *'" in workflow
    assert "workflow_dispatch:" in workflow
    assert "permissions:" in workflow
    assert "contents: write" in workflow
    assert "run: pytest -v" in workflow
    assert "run: python -m src.main" in workflow
    assert "file_pattern: reports/**" in workflow

from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")


def test_daily_digest_workflow_exists():
    assert (WORKFLOWS_DIR / "daily-digest.yml").exists()


def test_daily_digest_workflow_contract():
    workflow = (WORKFLOWS_DIR / "daily-digest.yml").read_text(encoding="utf-8")

    assert "cron: '0 6 * * *'" in workflow
    assert "workflow_dispatch:" in workflow
    assert "permissions:" in workflow
    assert "contents: write" in workflow
    assert "run: pytest -v" in workflow
    assert "run: python -m src.main" in workflow
    assert "file_pattern:" in workflow
    assert "index.html" in workflow


def test_deploy_pages_workflow_exists():
    assert (WORKFLOWS_DIR / "deploy-pages.yml").exists()


def test_deploy_pages_workflow_contract():
    workflow = (WORKFLOWS_DIR / "deploy-pages.yml").read_text(encoding="utf-8")

    assert "deploy-pages@v4" in workflow
    assert "upload-pages-artifact@v3" in workflow
    assert "configure-pages@v5" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow
    assert "branches: [main]" in workflow

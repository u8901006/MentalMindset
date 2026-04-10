# daily-research

Scaffold for the daily psychology research digest project.

## Automation

GitHub Actions runs the daily digest workflow at 06:00 UTC each day and can also be started manually from the Actions tab. The workflow installs `pytest`, runs the test suite, generates the latest report with `python -m src.main`, and commits updated files in `reports/` when output changes.

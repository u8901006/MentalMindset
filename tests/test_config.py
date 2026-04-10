import pytest

from src.config import Settings


def test_settings_expose_expected_defaults():
    settings = Settings()

    assert settings.schedule_hour == 6
    assert settings.lookback_days == 1
    assert settings.max_selected_papers == 10


def test_settings_read_environment_overrides(monkeypatch):
    monkeypatch.setenv("SCHEDULE_HOUR", "8")
    monkeypatch.setenv("LOOKBACK_DAYS", "3")
    monkeypatch.setenv("MAX_SELECTED_PAPERS", "5")
    monkeypatch.setenv("REQUEST_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("RETRY_ATTEMPTS", "4")
    monkeypatch.setenv("ENABLE_DIGEST_LOGGING", "yes")

    settings = Settings()

    assert settings.schedule_hour == 8
    assert settings.lookback_days == 3
    assert settings.max_selected_papers == 5
    assert settings.request_timeout_seconds == 45
    assert settings.retry_attempts == 4
    assert settings.enable_digest_logging is True


def test_settings_parse_false_boolean_values(monkeypatch):
    monkeypatch.setenv("ENABLE_DIGEST_LOGGING", "false")

    settings = Settings()

    assert settings.enable_digest_logging is False


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("SCHEDULE_HOUR", "-1"),
        ("SCHEDULE_HOUR", "24"),
        ("LOOKBACK_DAYS", "0"),
        ("MAX_SELECTED_PAPERS", "0"),
        ("REQUEST_TIMEOUT_SECONDS", "0"),
        ("RETRY_ATTEMPTS", "-1"),
    ],
)
def test_settings_reject_out_of_range_numeric_values(monkeypatch, name, value):
    monkeypatch.setenv(name, value)

    with pytest.raises(ValueError):
        Settings()


def test_settings_keep_surface_minimal():
    settings = Settings()

    assert not hasattr(settings, "model_name")

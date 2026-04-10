import os
from dataclasses import dataclass, field


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None else int(value)


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _validate_range(
    name: str, value: int, *, minimum: int, maximum: int | None = None
) -> None:
    if value < minimum or (maximum is not None and value > maximum):
        if maximum is None:
            raise ValueError(f"{name} must be >= {minimum}")
        raise ValueError(f"{name} must be between {minimum} and {maximum}")


@dataclass(frozen=True)
class Settings:
    schedule_hour: int = field(default_factory=lambda: _get_int("SCHEDULE_HOUR", 6))
    lookback_days: int = field(default_factory=lambda: _get_int("LOOKBACK_DAYS", 1))
    max_selected_papers: int = field(
        default_factory=lambda: _get_int("MAX_SELECTED_PAPERS", 10)
    )
    request_timeout_seconds: int = field(
        default_factory=lambda: _get_int("REQUEST_TIMEOUT_SECONDS", 30)
    )
    retry_attempts: int = field(default_factory=lambda: _get_int("RETRY_ATTEMPTS", 2))
    enable_digest_logging: bool = field(
        default_factory=lambda: _get_bool("ENABLE_DIGEST_LOGGING", False)
    )

    def __post_init__(self) -> None:
        _validate_range("schedule_hour", self.schedule_hour, minimum=0, maximum=23)
        _validate_range("lookback_days", self.lookback_days, minimum=1)
        _validate_range("max_selected_papers", self.max_selected_papers, minimum=1)
        _validate_range(
            "request_timeout_seconds", self.request_timeout_seconds, minimum=1
        )
        _validate_range("retry_attempts", self.retry_attempts, minimum=0)

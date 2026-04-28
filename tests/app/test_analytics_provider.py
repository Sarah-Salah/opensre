from __future__ import annotations

import pytest

from app.analytics.provider import Analytics, _posthog_host, _posthog_project_api_key


@pytest.fixture(autouse=True)
def reset_analytics_singleton() -> None:
    import app.analytics.provider as provider

    provider._instance = None
    yield
    provider._instance = None


def test_posthog_project_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENSRE_POSTHOG_PROJECT_API_KEY", " phc_x ")
    assert _posthog_project_api_key() == "phc_x"


def test_posthog_project_api_key_empty_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENSRE_POSTHOG_PROJECT_API_KEY", raising=False)
    assert _posthog_project_api_key() == ""


def test_posthog_host_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENSRE_POSTHOG_HOST", raising=False)
    assert _posthog_host() == "https://us.i.posthog.com"


def test_posthog_host_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENSRE_POSTHOG_HOST", "https://eu.i.posthog.com")
    assert _posthog_host() == "https://eu.i.posthog.com"


def test_analytics_disabled_without_project_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENSRE_POSTHOG_PROJECT_API_KEY", raising=False)
    monkeypatch.delenv("OPENSRE_ANALYTICS_DISABLED", raising=False)
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)
    assert Analytics()._disabled is True


def test_analytics_disabled_when_opt_out_even_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENSRE_POSTHOG_PROJECT_API_KEY", "phc_testkey")
    monkeypatch.setenv("OPENSRE_ANALYTICS_DISABLED", "1")
    assert Analytics()._disabled is True


def test_analytics_enabled_with_project_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENSRE_POSTHOG_PROJECT_API_KEY", "phc_testkey")
    monkeypatch.delenv("OPENSRE_ANALYTICS_DISABLED", raising=False)
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)
    a = Analytics()
    assert not a._disabled
    assert a._posthog_api_key == "phc_testkey"

from pathlib import Path

import pytest
from pydantic import ValidationError

from templates_python.utils.settings import AppSettings, get_settings


def test_defaults() -> None:
  settings = get_settings()
  assert settings.log_level == 'INFO'
  assert settings.log_format == 'console'


@pytest.mark.parametrize('level', ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
def test_log_levels(monkeypatch: pytest.MonkeyPatch, level: str) -> None:
  monkeypatch.setenv('LOG_LEVEL', level.lower())
  assert get_settings().log_level == level


@pytest.mark.parametrize(
  ('name', 'value'), [('LOG_LEVEL', 'TRACE'), ('LOG_FORMAT', 'xml')]
)
def test_invalid_settings(
  monkeypatch: pytest.MonkeyPatch, name: str, value: str
) -> None:
  monkeypatch.setenv(name, value)
  with pytest.raises(ValidationError, match=name.lower()):
    get_settings()


def test_dotenv_and_environment_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
  Path('.env').write_text('LOG_LEVEL=DEBUG\nLOG_FORMAT=json\nOTHER_APP_KEY=unused\n')
  monkeypatch.setenv('LOG_LEVEL', 'ERROR')
  settings = get_settings()
  assert settings.log_level == 'ERROR'
  assert settings.log_format == 'json'


def test_explicit_values_override_environment(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.setenv('LOG_LEVEL', 'ERROR')
  assert AppSettings(log_level='DEBUG').log_level == 'DEBUG'


def test_settings_are_cached_until_cleared(monkeypatch: pytest.MonkeyPatch) -> None:
  first = get_settings()
  monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
  assert get_settings() is first
  assert first.log_level == 'INFO'
  get_settings.cache_clear()
  assert get_settings().log_level == 'DEBUG'


def test_settings_are_immutable() -> None:
  with pytest.raises(ValidationError, match='frozen'):
    get_settings().log_level = 'DEBUG'

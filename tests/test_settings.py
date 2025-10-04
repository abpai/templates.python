def test_settings_log_level(monkeypatch):  # type: ignore[arg-type]
  from utils.settings import get_settings

  get_settings.cache_clear()  # Clear LRU cache
  monkeypatch.setenv('LOG_LEVEL', 'DEBUG')  # type: ignore[attr-defined]

  settings = get_settings()
  assert settings.log_level == 'DEBUG'


def test_settings_log_format(monkeypatch):  # type: ignore[arg-type]
  from utils.settings import get_settings

  get_settings.cache_clear()  # Clear LRU cache
  monkeypatch.setenv('LOG_FORMAT', 'json')  # type: ignore[attr-defined]

  settings = get_settings()
  assert settings.log_format == 'json'

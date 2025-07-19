def test_settings_prefix_env(monkeypatch):  # type: ignore[arg-type]
  monkeypatch.setenv('OPENAI_API_KEY', 'test')  # type: ignore[attr-defined]
  from utils.settings import get_settings

  settings = get_settings()
  assert settings.openai_api_key == 'test'

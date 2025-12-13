import logging

import structlog


def test_configure_logging_console(monkeypatch):  # type: ignore[arg-type]
  from templates_python.utils.settings import configure_logging, get_settings

  get_settings.cache_clear()
  monkeypatch.setenv('LOG_FORMAT', 'console')  # type: ignore[attr-defined]
  monkeypatch.setenv('LOG_LEVEL', 'INFO')  # type: ignore[attr-defined]

  configure_logging()

  assert logging.root.handlers
  assert isinstance(
    logging.root.handlers[0].formatter, structlog.stdlib.ProcessorFormatter
  )


def test_configure_logging_json(monkeypatch):  # type: ignore[arg-type]
  from templates_python.utils.settings import configure_logging, get_settings

  get_settings.cache_clear()
  monkeypatch.setenv('LOG_FORMAT', 'json')  # type: ignore[attr-defined]
  monkeypatch.setenv('LOG_LEVEL', 'DEBUG')  # type: ignore[attr-defined]

  configure_logging()

  assert logging.getLogger().level == logging.DEBUG

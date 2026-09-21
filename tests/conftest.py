"""Isolate environment settings and process-wide logging between tests."""

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
import structlog

from templates_python.utils.settings import get_settings


@pytest.fixture(autouse=True)
def isolated_settings(
  monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[None]:
  """Keep developer .env files and cached settings out of test results."""
  monkeypatch.chdir(tmp_path)
  monkeypatch.delenv('LOG_LEVEL', raising=False)
  monkeypatch.delenv('LOG_FORMAT', raising=False)
  get_settings.cache_clear()
  yield
  get_settings.cache_clear()


@pytest.fixture(autouse=True)
def isolated_logging() -> Iterator[None]:
  """Restore logging without closing pytest's own capture handlers."""
  root = logging.getLogger()
  handlers, level = root.handlers[:], root.level
  config = structlog.get_config().copy()
  context = structlog.contextvars.get_contextvars()
  root.handlers = []
  structlog.contextvars.clear_contextvars()
  yield
  for handler in root.handlers[:]:
    root.removeHandler(handler)
    handler.close()
  root.handlers = handlers
  root.setLevel(level)
  structlog.configure(**config)
  structlog.contextvars.clear_contextvars()
  structlog.contextvars.bind_contextvars(**context)

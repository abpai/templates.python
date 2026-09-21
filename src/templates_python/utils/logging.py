"""Consistent logging for application and standard-library loggers."""

import logging
import sys
from typing import TextIO

import structlog

from .settings import AppSettings


def _formatter(
  settings: AppSettings,
  shared: list[structlog.types.Processor],
  stream: TextIO,
) -> structlog.stdlib.ProcessorFormatter:
  """Render JSON exceptions or readable console output without internal metadata."""
  processors: list[structlog.types.Processor] = [
    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
  ]
  if settings.log_format == 'json':
    processors.extend(
      [
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
      ]
    )
  else:
    processors.append(structlog.dev.ConsoleRenderer(colors=stream.isatty()))
  return structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=shared,
    processors=processors,
  )


def configure_logging(settings: AppSettings, *, stream: TextIO | None = None) -> None:
  """Own root logging configuration at application startup."""
  stream = stream if stream is not None else sys.stderr
  shared: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.ExtraAdder(),
    structlog.processors.TimeStamper(fmt='iso', utc=True),
  ]
  handler = logging.StreamHandler(stream)
  handler.setFormatter(_formatter(settings, shared, stream))
  logging.basicConfig(level=settings.log_level, handlers=[handler], force=True)
  structlog.configure(
    processors=[
      structlog.stdlib.filter_by_level,
      *shared,
      structlog.stdlib.PositionalArgumentsFormatter(),
      structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
  )

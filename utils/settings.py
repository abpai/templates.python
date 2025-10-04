"""Application settings and logging configuration."""

import logging
from functools import lru_cache

import structlog
from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
  """Environment-driven application settings."""

  # General logging level (DEBUG / INFO / WARNING / ERROR)
  log_level: str = Field('INFO', alias='LOG_LEVEL')

  # Logging format ('console' or 'json')
  log_format: str = Field('console', alias='LOG_FORMAT')

  model_config = {
    'env_file': '.env',
    'env_file_encoding': 'utf-8',
    'case_sensitive': False,
  }


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
  """Return cached application settings."""
  return AppSettings()  # type: ignore[arg-type]


def configure_logging(level: str | None = None) -> None:
  """Configure structlog + stdlib logging."""
  settings = get_settings()
  level = level or settings.log_level
  log_format = settings.log_format
  log_level = getattr(logging, level.upper(), logging.INFO)

  # These processors are shared by all logs
  shared_processors: list[structlog.types.Processor] = [
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt='iso'),
  ]

  # Configure the root logger and handlers
  logging.basicConfig(
    level=log_level, format='%(message)s', handlers=[logging.StreamHandler()]
  )

  # Determine the final renderer based on the format
  if log_format == 'json':
    final_processor = structlog.processors.JSONRenderer()
  else:
    final_processor = structlog.dev.ConsoleRenderer(colors=True)

  # Configure structlog to process all logs
  structlog.configure(
    processors=[
      *shared_processors,
      structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
  )

  # Create a formatter to apply our processor chain to all logs
  formatter = structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=shared_processors,
    processor=final_processor,
  )

  # Replace the default handler's formatter with our structlog formatter
  for handler in logging.root.handlers:
    handler.setFormatter(formatter)

  # Tame noisy library loggers when not in DEBUG mode
  if log_level > logging.DEBUG:
    for logger_name in ['httpx']:
      logging.getLogger(logger_name).setLevel(logging.WARNING)


# Provide a module-level settings instance for convenience
settings = get_settings()

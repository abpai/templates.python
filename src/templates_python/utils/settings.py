"""Validated application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
  """Immutable settings loaded from the environment and an optional .env file."""

  model_config = SettingsConfigDict(
    env_file='.env',
    env_file_encoding='utf-8',
    case_sensitive=False,
    extra='ignore',
    frozen=True,
  )

  log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
  log_format: Literal['console', 'json'] = 'console'

  @field_validator('log_level', mode='before')
  @classmethod
  def normalize_log_level(cls, value: object) -> object:
    """Accept conventional lowercase log levels without hiding invalid values."""
    return value.strip().upper() if isinstance(value, str) else value


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
  """Return settings cached for the lifetime of the application."""
  return AppSettings()

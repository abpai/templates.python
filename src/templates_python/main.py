"""Main application entry point."""

import structlog

from .utils.logging import configure_logging
from .utils.settings import get_settings


def main() -> None:
  """Run the main application logic."""
  settings = get_settings()
  configure_logging(settings)
  log = structlog.get_logger(__name__)
  log.info('Application started', log_level=settings.log_level)

  # Your application logic here
  log.info('Hello, World!')

  log.info('Application finished')


if __name__ == '__main__':
  main()

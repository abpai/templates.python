import json
import logging
from io import StringIO

import pytest
import structlog

from templates_python.utils.logging import configure_logging
from templates_python.utils.settings import AppSettings


@pytest.mark.parametrize('structured', [False, True])
def test_json_logs_include_context_and_fields(structured: bool) -> None:
  stream = StringIO()
  configure_logging(AppSettings(log_format='json'), stream=stream)
  structlog.contextvars.bind_contextvars(request_id='request-123')
  if structured:
    structlog.get_logger('example').info('Hello %s', 'world', count=2)
  else:
    logging.getLogger('example').info('Hello %s', 'world', extra={'count': 2})
  event = json.loads(stream.getvalue())
  assert event['event'] == 'Hello world'
  assert event['level'] == 'info'
  assert event['logger'] == 'example'
  assert event['request_id'] == 'request-123'
  assert event['count'] == 2
  assert 'timestamp' in event
  assert '_record' not in event
  assert '_from_structlog' not in event


@pytest.mark.parametrize('structured', [False, True])
def test_json_exceptions_are_serialized(structured: bool) -> None:
  stream = StringIO()
  configure_logging(AppSettings(log_format='json'), stream=stream)
  logger = (
    structlog.get_logger('example') if structured else logging.getLogger('example')
  )
  try:
    raise ValueError('example failure')
  except ValueError:
    logger.exception('Operation failed')
  event = json.loads(stream.getvalue())
  assert event['event'] == 'Operation failed'
  assert event['level'] == 'error'
  assert 'ValueError: example failure' in event['exception']
  assert 'Traceback' in event['exception']
  assert 'exc_info' not in event


@pytest.mark.parametrize('structured', [False, True])
def test_log_level_filters_messages(structured: bool) -> None:
  stream = StringIO()
  configure_logging(AppSettings(log_level='WARNING', log_format='json'), stream=stream)
  logger = (
    structlog.get_logger('example') if structured else logging.getLogger('example')
  )
  logger.debug('Hidden debug')
  logger.info('Hidden info')
  logger.warning('Visible warning')
  events = [json.loads(line) for line in stream.getvalue().splitlines()]
  assert [event['event'] for event in events] == ['Visible warning']


def test_console_logs_are_plain_when_redirected() -> None:
  stream = StringIO()
  configure_logging(AppSettings(), stream=stream)
  structlog.get_logger().info('Readable message')
  assert 'Readable message' in stream.getvalue()
  assert '\x1b[' not in stream.getvalue()


def test_reconfiguration_updates_level_without_duplicate_logs() -> None:
  stream = StringIO()
  configure_logging(AppSettings(log_level='ERROR'), stream=stream)
  configure_logging(AppSettings(log_level='DEBUG', log_format='json'), stream=stream)
  logging.getLogger('httpx').debug('Debug enabled')
  events = [json.loads(line) for line in stream.getvalue().splitlines()]
  assert [event['event'] for event in events] == ['Debug enabled']

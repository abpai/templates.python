import json
import os
import subprocess
import sys

import pytest

from templates_python.main import main


def test_main_logs_lifecycle(
  monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
  monkeypatch.setenv('LOG_FORMAT', 'json')
  main()
  captured = capsys.readouterr()
  assert captured.out == ''
  events = [json.loads(line)['event'] for line in captured.err.splitlines()]
  assert events == ['Application started', 'Hello, World!', 'Application finished']


def test_module_entry_point() -> None:
  result = subprocess.run(
    [sys.executable, '-m', 'templates_python'],
    env={**os.environ, 'LOG_FORMAT': 'json'},
    capture_output=True,
    text=True,
    check=True,
  )
  assert result.stdout == ''
  assert [json.loads(line)['event'] for line in result.stderr.splitlines()] == [
    'Application started',
    'Hello, World!',
    'Application finished',
  ]

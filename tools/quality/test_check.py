"""Exercise actual linters and baseline behavior without importing the application."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check

LIMITS = {'cyclomatic': 10, 'cognitive': 15}


def branchy_function(name: str = 'branchy', branches: int = 12) -> str:
  """Produce independent branches above the configured cyclomatic limit."""
  body = ''.join(
    f'  if value == {index}:\n    return {index}\n' for index in range(branches)
  )
  return f'def {name}(value: int) -> int:\n{body}  return -1\n'


class QualityPolicyTests(unittest.TestCase):
  """Keep policy regressions independent of the application runtime."""

  def setUp(self) -> None:
    self.directory = tempfile.TemporaryDirectory()
    self.addCleanup(self.directory.cleanup)
    self.root = Path(self.directory.name)
    self.source = self.root / 'sample.py'

  def measure(self, source: str) -> list[check.Complexity]:
    self.source.write_text(source, encoding='utf-8')
    return check.measured_complexity(self.root, [self.source], LIMITS)

  def test_simple_validation_passes(self) -> None:
    source = (
      'def validate(value: object) -> str:\n'
      '  if not isinstance(value, str):\n'
      '    raise ValueError("expected string")\n'
      '  return value\n'
    )
    self.assertEqual(self.measure(source), [])

  def test_new_complex_function_fails(self) -> None:
    measured = self.measure(branchy_function())
    self.assertTrue(check.new_or_worse(measured, {}))
    self.assertEqual(measured[0].score, 13)

  def test_existing_score_passes(self) -> None:
    measured = self.measure(branchy_function())
    allowances = {item.key: item.score for item in measured}
    self.assertEqual(check.new_or_worse(measured, allowances), [])

  def test_worse_body_with_unchanged_header_fails(self) -> None:
    measured = self.measure(branchy_function())
    allowances = {item.key: item.score for item in measured}
    worse = self.measure(branchy_function(branches=13))
    self.assertTrue(check.new_or_worse(worse, allowances))

  def test_improvement_passes(self) -> None:
    measured = self.measure(branchy_function())
    allowances = {item.key: item.score for item in measured}
    improved = self.measure(branchy_function(branches=11))
    self.assertEqual(check.new_or_worse(improved, allowances), [])

  def test_line_movement_preserves_identity(self) -> None:
    original = self.measure(branchy_function())
    moved = self.measure('\n\n' + branchy_function())
    self.assertEqual(original[0].key, moved[0].key)

  def test_renamed_function_requires_review(self) -> None:
    original = self.measure(branchy_function())
    renamed = self.measure(branchy_function(name='another'))
    self.assertTrue(check.new_or_worse(renamed, {original[0].key: original[0].score}))

  def test_complexity_noqa_cannot_bypass_limit(self) -> None:
    source = branchy_function().replace('-> int:', '-> int:  # noqa: C901')
    self.assertTrue(self.measure(source))

  def test_blanket_lint_suppression_fails(self) -> None:
    with self.assertRaises(ValueError):
      self.measure('value = 1  # noqa\n')

  def test_specific_application_lint_suppression_remains_allowed(self) -> None:
    self.assertEqual(self.measure('import os  # noqa: F401\n'), [])

  def test_cognitive_nesting_is_measured(self) -> None:
    source = 'def nested(value: int) -> None:\n'
    for depth in range(1, 7):
      source += '  ' * depth + f'if value > {depth}:\n'
    source += '  ' * 7 + 'print(value)\n'
    measured = self.measure(source)
    self.assertTrue(
      any(item.rule == 'cognitive' and item.score > 15 for item in measured)
    )

  def test_bad_syntax_fails_closed(self) -> None:
    with self.assertRaises(ValueError):
      self.measure('def broken(\n')

  def test_baseline_roundtrip(self) -> None:
    path = self.root / 'baseline.json'
    measured = self.measure(branchy_function())
    check.write_baseline(path, measured, LIMITS)
    self.assertEqual(
      check.read_baseline(path, LIMITS), {item.key: item.score for item in measured}
    )

  def test_missing_baseline_fails_closed(self) -> None:
    with self.assertRaises(FileNotFoundError):
      check.read_baseline(self.root / 'absent.json', LIMITS)

  def test_changed_limits_require_baseline_review(self) -> None:
    path = self.root / 'baseline.json'
    check.write_baseline(path, [], LIMITS)
    with self.assertRaises(ValueError):
      check.read_baseline(path, {'cyclomatic': 20, 'cognitive': 15})

  def test_new_untracked_file_is_in_scope(self) -> None:
    self.source.write_text('pass\n')
    self.assertEqual(check.python_files(self.root, ['.']), [self.source])

  def test_empty_scope_fails_closed(self) -> None:
    with self.assertRaises(ValueError):
      check.python_files(self.root, ['.'])

  def test_absent_advisory_path_is_skipped(self) -> None:
    (self.root / 'src').mkdir()
    config = {'paths': ['src'], 'advisory-paths': ['scratch']}
    self.assertEqual(check.scoped_paths(self.root, config, advisory=True), ['src'])
    (self.root / 'scratch').mkdir()
    self.assertEqual(
      check.scoped_paths(self.root, config, advisory=True), ['src', 'scratch']
    )
    self.assertEqual(check.scoped_paths(self.root, config, advisory=False), ['src'])

  def test_missing_tool_fails_closed(self) -> None:
    with self.assertRaises(FileNotFoundError):
      check.run_json(['missing-quality-tool-907'], self.root)

  def anti_findings(self, source: str) -> list[dict]:
    self.source.write_text(source)
    config = (check.ROOT / 'pyproject.toml').read_text()
    config = config.replace('baseline = "tools/quality/anti-slop-baseline.json"', '')
    (self.root / 'pyproject.toml').write_text(config)
    return check.run_json(
      [
        sys.executable,
        '-m',
        'anti_slop',
        '--config',
        str(self.root / 'pyproject.toml'),
        '--format',
        'json',
        '--jobs',
        '1',
        str(self.source),
      ],
      self.root,
    )

  def test_unexplained_suppression_fails(self) -> None:
    findings = self.anti_findings('result = call()  # type: ignore\n')
    self.assertTrue(any(item['rule'] == 'require-safety-comment' for item in findings))

  def test_justified_specific_suppression_passes(self) -> None:
    source = '# SAFETY: the generated SDK omits this documented method.\n'
    source += 'result = sdk.call()  # ty: ignore[unresolved-attribute]\n'
    self.assertEqual(self.anti_findings(source), [])

  def test_chained_casts_fail(self) -> None:
    source = 'from typing import cast\nvalue = cast(str, cast(object, raw))\n'
    self.assertTrue(
      any(item['rule'] == 'no-chained-casts' for item in self.anti_findings(source))
    )

  def test_widen_then_cast_fails(self) -> None:
    source = 'from typing import Any, cast\noriginal: str = "ok"\n'
    source += 'wide: Any = original\nvalue = cast(str, wide)\n'
    self.assertTrue(
      any(item['rule'] == 'no-widen-then-cast' for item in self.anti_findings(source))
    )

  def test_boundary_checks_and_external_effect_mocks_remain_allowed(self) -> None:
    source = 'from unittest.mock import patch\n'
    source += 'def validate(value: object) -> str:\n'
    source += '  if not isinstance(value, str):\n    raise ValueError("string")\n'
    source += '  return value\n'
    source += 'with patch("subprocess.run"):\n  pass\n'
    self.assertEqual(self.anti_findings(source), [])

  def test_anti_baseline_does_not_hide_a_new_suppression(self) -> None:
    config = (check.ROOT / 'pyproject.toml').read_text()
    config = config.replace('tools/quality/anti-slop-baseline.json', 'baseline.json')
    (self.root / 'pyproject.toml').write_text(config)
    self.source.write_text('old = call()  # type: ignore\n')
    command = [sys.executable, '-m', 'anti_slop', '--jobs', '1', str(self.source)]
    result = subprocess.run(
      [*command, '--generate-baseline'], cwd=self.root, capture_output=True
    )
    self.assertEqual(result.returncode, 0)
    self.source.write_text(
      'old = call()  # type: ignore\nnew = call()  # type: ignore\n'
    )
    result = subprocess.run(command, cwd=self.root, capture_output=True)
    self.assertEqual(result.returncode, 1)

  def test_anti_baseline_missing_fails_closed(self) -> None:
    config = (check.ROOT / 'pyproject.toml').read_text()
    (self.root / 'pyproject.toml').write_text(config)
    self.source.write_text('pass\n')
    result = subprocess.run(
      [sys.executable, '-m', 'anti_slop', str(self.source)],
      cwd=self.root,
      capture_output=True,
      env={**os.environ, 'NO_COLOR': '1'},
    )
    self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
  unittest.main()

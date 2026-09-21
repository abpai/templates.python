"""Run pinned quality tools with explicit, reviewable complexity allowances."""

import argparse
import ast
import json
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import complexipy

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'tools/quality/complexity-baseline.json'


@dataclass(frozen=True)
class Complexity:
  """A measured function that exceeds the project limit."""

  path: str
  symbol: str
  rule: str
  score: int
  line: int

  @property
  def key(self) -> str:
    return f'{self.rule}:{self.path}:{self.symbol}'


def python_files(root: Path, paths: list[str]) -> list[Path]:
  """Include new files while keeping virtual environments and caches out."""
  files = set()
  for name in paths:
    path = root / name
    if not path.exists():
      raise ValueError(f'Quality scope does not exist: {name}')
    candidates = [path] if path.is_file() else path.rglob('*.py')
    for candidate in candidates:
      parts = candidate.relative_to(root).parts
      if not any(part.startswith('.') or part == '__pycache__' for part in parts):
        files.add(candidate)
  if not files:
    raise ValueError('Quality scope contains no Python files')
  return sorted(files)


def scoped_paths(root: Path, config: dict, advisory: bool) -> list[str]:
  """Blocking paths must exist; advisory-only paths may be untracked and absent."""
  if not advisory:
    return config['paths']
  optional = config.get('advisory-paths', [])
  return config['paths'] + [name for name in optional if (root / name).exists()]


def run_json(command: list[str], root: Path) -> list[dict]:
  """Accept lint findings but reject tool errors and malformed output."""
  result = subprocess.run(command, cwd=root, capture_output=True, text=True)
  if result.returncode not in (0, 1):
    raise RuntimeError(result.stderr.strip() or result.stdout.strip())
  findings = json.loads(result.stdout)
  if not isinstance(findings, list):
    raise ValueError('Expected a JSON array of lint findings')
  return findings


def function_names(path: Path) -> dict[int, str]:
  """Identify functions by lexical name rather than their changing line numbers."""
  names = {}

  def visit(node: ast.AST, parents: tuple[str, ...]) -> None:
    for child in ast.iter_child_nodes(node):
      lineage = parents
      if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        lineage = (*parents, child.name)
        if not isinstance(child, ast.ClassDef):
          names[child.lineno] = '::'.join(lineage)
      visit(child, lineage)

  visit(ast.parse(path.read_text(encoding='utf-8')), ())
  return names


def ruff_findings(root: Path, files: list[Path], limit: int) -> list[dict]:
  """Run only the blocking additions; the existing linter remains separate."""
  return run_json(
    [
      'ruff',
      'check',
      '--isolated',
      '--no-cache',
      '--ignore-noqa',
      '--output-format',
      'json',
      '--select',
      'C901,PGH004',
      '--config',
      f'lint.mccabe.max-complexity={limit}',
      *[str(path) for path in files],
    ],
    root,
  )


def cyclomatic_complexity(
  root: Path, files: list[Path], limit: int
) -> list[Complexity]:
  """Convert Ruff's complexity diagnostics into stable function identities."""
  measured = []
  for finding in ruff_findings(root, files, limit):
    path = Path(finding['filename'])
    line = finding['location']['row']
    if finding['code'] != 'C901':
      raise ValueError(f'{path.relative_to(root)}:{line}: {finding["message"]}')
    score = int(finding['message'].rsplit('(', 1)[1].split()[0])
    measured.append(
      Complexity(
        str(path.relative_to(root)),
        function_names(path)[line],
        'C901',
        score,
        line,
      )
    )
  return measured


def measured_complexity(
  root: Path, files: list[Path], limits: dict
) -> list[Complexity]:
  """Measure full function bodies, including changed code on unchanged headers."""
  measured = cyclomatic_complexity(root, files, limits['cyclomatic'])
  for path in files:
    result = complexipy.file_complexity(str(path), no_ignore=True)
    for function in result.functions:
      if function.complexity > limits['cognitive']:
        measured.append(
          Complexity(
            str(path.relative_to(root)),
            function.name,
            'cognitive',
            function.complexity,
            function.line_start,
          )
        )
  return measured


def new_or_worse(
  measured: list[Complexity], allowances: dict[str, int]
) -> list[Complexity]:
  """Allow existing scores and improvements, but never a higher score."""
  return [item for item in measured if item.score > allowances.get(item.key, 0)]


def read_baseline(path: Path, limits: dict) -> dict[str, int]:
  """Reject missing or incompatible baselines instead of silently passing."""
  baseline = json.loads(path.read_text(encoding='utf-8'))
  if baseline['version'] != 1 or baseline['limits'] != limits:
    raise ValueError('Baseline version/limits changed; review the policy and baseline')
  allowances = baseline['allowances']
  if not isinstance(allowances, dict) or any(
    type(value) is not int or value < 1 for value in allowances.values()
  ):
    raise ValueError('Complexity allowances must be positive integer scores')
  return allowances


def write_baseline(path: Path, measured: list[Complexity], limits: dict) -> None:
  """Write a snapshot only when the caller explicitly requests a reviewed update."""
  snapshot = {
    'version': 1,
    'limits': limits,
    'allowances': dict(sorted((item.key, item.score) for item in measured)),
  }
  path.write_text(json.dumps(snapshot, indent=2) + '\n', encoding='utf-8')


def anti_slop(files: list[Path], update: bool) -> int:
  """Use the audited upstream policy with a separately reviewed findings baseline."""
  command = [
    sys.executable,
    '-m',
    'anti_slop',
    '--config',
    str(ROOT / 'pyproject.toml'),
  ]
  if update:
    command.append('--generate-baseline')
  return subprocess.run(
    [*command, '--jobs', '1', *map(str, files)], cwd=ROOT
  ).returncode


def advisory(files: list[Path]) -> int:
  """Report unsettled policy choices without turning them into blocking rules."""
  return subprocess.run(
    [
      'ruff',
      'check',
      '--isolated',
      '--no-cache',
      '--exit-zero',
      '--select',
      'ANN,PLR0911,PLR0912,PLR0913,PLR0915,PLR0917,BLE001,SIM,PERF',
      '--config',
      'lint.pylint.max-args=5',
      '--config',
      'lint.pylint.max-positional-args=4',
      '--config',
      'lint.pylint.max-statements=40',
      *map(str, files),
    ],
    cwd=ROOT,
  ).returncode


def check(measured: list[Complexity], limits: dict) -> int:
  """Report actionable scores and optional baseline tightening."""
  allowances = read_baseline(BASELINE, limits)
  failures = new_or_worse(measured, allowances)
  for item in failures:
    print(
      f'{item.path}:{item.line}: {item.rule} {item.symbol}: {item.score}'
      f' exceeds allowed {allowances.get(item.key, "new violation")}'
    )
  current = {item.key: item.score for item in measured}
  stale = sum(current.get(key, 0) < score for key, score in allowances.items())
  if stale:
    print(f'{stale} allowances can be tightened; review an explicit baseline update.')
  print(
    f'Complexity: {len(failures)} new/worse; {len(measured) - len(failures)} baselined.'
  )
  return bool(failures)


def main() -> int:
  """Run the same policy from Make, pre-commit, and CI."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--update-baseline', action='store_true')
  parser.add_argument('--advisory', action='store_true')
  options = parser.parse_args()
  config = tomllib.loads((ROOT / 'pyproject.toml').read_text())['tool']['quality']
  files = python_files(ROOT, scoped_paths(ROOT, config, options.advisory))
  if options.advisory:
    return advisory(files)
  limits = {'cyclomatic': config['cyclomatic'], 'cognitive': config['cognitive']}
  measured = measured_complexity(ROOT, files, limits)
  if options.update_baseline:
    write_baseline(BASELINE, measured, limits)
    print(
      'Baseline updated. Review every new or increased allowance before committing.'
    )
    return anti_slop(files, update=True)
  complexity_status = check(measured, limits)
  return max(complexity_status, anti_slop(files, update=False))


if __name__ == '__main__':
  try:
    raise SystemExit(main())
  except (OSError, ValueError, KeyError, RuntimeError, SyntaxError) as error:
    print(f'Quality check failed: {error}', file=sys.stderr)
    raise SystemExit(2) from error

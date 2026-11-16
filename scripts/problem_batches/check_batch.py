"""Checks one batch of problem upgrades before it is merged. Build-time only; never runs student code.

    python scripts/problem_batches/check_batch.py 1

For every problem in batch_<n>.py:
  * the Python reference reproduces every existing fixture,
  * every new adversarial case's expected output matches BOTH the repository's Java reference
    (run with the JDK's single-file launcher) and the Python reference,
  * there are exactly three hints, a substantive editorial, and two new cases not already present.
"""
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
n = sys.argv[1]
spec = importlib.util.spec_from_file_location(f'batch_{n}', ROOT / f'scripts/problem_batches/batch_{n}.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
content = json.loads((ROOT / 'backend/src/main/resources/content.json').read_text(encoding='utf-8'))
problems = {p['id'].removeprefix('problem-'): p for p in content['problems']}


def normalize(value):
    return re.sub(r'[ \t]+(?=\n|$)', '', value.replace('\r\n', '\n')).rstrip()


def run(cmd, source_input, cwd):
    done = subprocess.run(cmd, input=source_input, capture_output=True, text=True, timeout=30, cwd=cwd)
    if done.returncode:
        return None, done.stderr.strip()[-400:]
    return done.stdout, None


failures = 0
with tempfile.TemporaryDirectory(dir=ROOT / '.cache' if (ROOT / '.cache').is_dir() else None) as tmp:
    for slug, entry in batch.PROBLEMS.items():
        problem = problems.get(slug)
        issues = []
        if problem is None:
            print(f'{slug}: UNKNOWN PROBLEM')
            failures += 1
            continue
        py = Path(tmp) / f'{slug.replace("-", "_")}.py'
        py.write_text(entry['python'], encoding='utf-8')
        java_dir = Path(tmp) / slug
        java_dir.mkdir()
        (java_dir / 'Main.java').write_text(problem['reference'], encoding='utf-8')
        for i, case in enumerate(problem['tests']):
            out, err = run([sys.executable, str(py)], case['input'], tmp)
            if err or normalize(out) != normalize(case['output']):
                issues.append(f'python fails existing fixture {i}: input {case["input"]!r} expected {case["output"]!r} got {out!r} {err or ""}')
        authored = {normalize(source) for source, _ in entry.get('cases', [])}
        # once merged, this batch's own cases are the hidden tail of the fixtures; only older ones count
        merged = problem.get('references', {}).get('python') == entry['python']
        existing = {normalize(c['input']) for c in problem['tests'] if not (merged and normalize(c['input']) in authored)}
        cases = entry.get('cases', [])
        if len(cases) != 2:
            issues.append(f'needs exactly 2 new cases, has {len(cases)}')
        for source, expected in cases:
            source = source if source.endswith('\n') else source + '\n'
            if normalize(source) in existing:
                issues.append(f'case already exists: {source!r}')
            jout, jerr = run(['java', 'Main.java'], source, java_dir)
            pout, perr = run([sys.executable, str(py)], source, tmp)
            if jerr or normalize(jout) != normalize(expected):
                issues.append(f'java disagrees on {source!r}: expected {expected!r}, java gave {jout!r} {jerr or ""}')
            if perr or normalize(pout) != normalize(expected):
                issues.append(f'python disagrees on {source!r}: expected {expected!r}, python gave {pout!r} {perr or ""}')
        hints = entry.get('hints', [])
        if len(hints) != 3 or any(len(h) < 25 for h in hints):
            issues.append('needs exactly three substantive hints')
        if len(entry.get('editorial', '')) < 300:
            issues.append('editorial is too short (under 300 characters)')
        print(f'{slug}: {"OK" if not issues else "FAIL"}')
        for issue in issues:
            print('   -', issue)
        failures += bool(issues)
print(f'{len(batch.PROBLEMS)} problems, {failures} failing')
sys.exit(1 if failures else 0)

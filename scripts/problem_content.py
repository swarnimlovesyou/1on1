"""Python references, specific hints, editorials and adversarial cases for the problems outside the
eight reference journeys. Authored in scripts/problem_batches/batch_*.py and checked there with
check_batch.py (Python on every fixture; Java and Python agreeing on each new case)."""
import importlib.util
from pathlib import Path

BATCHES = Path(__file__).resolve().parent / 'problem_batches'


def load():
    entries = {}
    for path in sorted(BATCHES.glob('batch_*.py')):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for slug, entry in module.PROBLEMS.items():
            assert slug not in entries, f'{slug} is authored in two batches'
            entries[slug] = entry
    return entries


def enrich(problems):
    entries = load()
    for problem in problems:
        slug = problem['id'].removeprefix('problem-')
        entry = entries.pop(slug, None)
        if entry is None:
            continue
        assert not problem.get('referenceJourney'), f'{slug} already has a reference journey'
        problem['references'] = dict(java=problem['reference'], python=entry['python'])
        problem['hints'] = list(entry['hints'])
        problem['editorial'] = entry['editorial']
        for source, expected in entry['cases']:
            problem['tests'].append(dict(input=source.rstrip('\n') + '\n', output=expected.rstrip('\n') + '\n', public=False))
    assert not entries, f'batch entries for unknown problems: {sorted(entries)}'

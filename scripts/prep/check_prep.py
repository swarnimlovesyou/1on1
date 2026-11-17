"""Checks Prep guides before they are merged. Structure only: a separate fact-check pass reviews correctness.

    python scripts/prep/check_prep.py scripts/prep/cs_oop_batch.py
"""
import importlib.util
import sys
from pathlib import Path

TRACKS = ('aptitude', 'reasoning', 'puzzles', 'cs-fundamentals', 'system-design')
SUBJECTS = ('OOP', 'DBMS', 'Operating systems', 'Computer networks', 'SQL')


def _text(value):
    return isinstance(value, str) and value.strip() != ''


def validate(g):
    errors = []
    gid = g.get('id', '')
    if not (isinstance(gid, str) and gid.startswith('guide-' + str(g.get('track', '')) + '-')):
        errors.append(f'id must start with guide-<track>-: {gid!r}')
    if g.get('kind') != 'guide':
        errors.append('kind must be "guide"')
    if g.get('track') not in TRACKS:
        errors.append(f'track must be one of {TRACKS}')
    if g.get('track') == 'cs-fundamentals' and g.get('subject') not in SUBJECTS:
        errors.append(f'subject must be one of {SUBJECTS}')
    for key in ('title', 'summary'):
        if not _text(g.get(key)):
            errors.append(f'{key} is required')
    if not isinstance(g.get('order'), int):
        errors.append('order must be an integer')
    sections = g.get('sections') or []
    if not 3 <= len(sections) <= 5:
        errors.append(f'sections: need 3-5, have {len(sections)}')
    for i, s in enumerate(sections):
        if not (_text(s.get('title')) and _text(s.get('text'))):
            errors.append(f'sections[{i}] needs a title and text')
    points = g.get('keyPoints') or []
    if not 3 <= len(points) <= 6 or not all(_text(p) for p in points):
        errors.append(f'keyPoints: need 3-6 non-empty, have {len(points)}')
    puzzle = g.get('puzzle')
    challenges = g.get('challenges') or []
    expected = 0 if puzzle else 5
    if len(challenges) != expected:
        errors.append(f'challenges: need exactly {expected}, have {len(challenges)}')
    seen = set()
    for i, c in enumerate(challenges):
        where = f'challenges[{i}]'
        if c.get('id') in seen:
            errors.append(f'{where}: duplicate id {c.get("id")}')
        seen.add(c.get('id'))
        if not (isinstance(c.get('id'), str) and c['id'].startswith('challenge-')):
            errors.append(f'{where}: id must start with challenge-')
        if c.get('kind') != 'prediction':
            errors.append(f'{where}: kind must be prediction')
        options = c.get('options') or []
        if not 3 <= len(options) <= 4 or not all(_text(o) for o in options):
            errors.append(f'{where}: options need 3-4 non-empty choices')
        if not (isinstance(c.get('answer'), int) and 0 <= c['answer'] < len(options)):
            errors.append(f'{where}: answer must index an option')
        for key in ('title', 'prompt', 'explanation', 'hint'):
            if not _text(c.get(key)):
                errors.append(f'{where}: {key} is required')
    return errors


def load(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.GUIDES


def main(paths):
    failing = 0
    ids = set()
    for path in paths:
        for g in load(path):
            errors = validate(g)
            if g.get('id') in ids:
                errors.append('guide id used twice')
            ids.add(g.get('id'))
            print(f'{g.get("id")}: {"OK" if not errors else "FAIL"}')
            for e in errors:
                print('   -', e)
            failing += bool(errors)
    print(f'{len(ids)} guides, {failing} failing')
    return failing


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1:]) else 0)

"""Prep tracks and guides (aptitude, reasoning, puzzles, CS fundamentals, system design), authored in
scripts/prep/*_batch*.py and validated by scripts/prep/check_prep.py before they are written to content.json."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent / 'prep'
sys.path.insert(0, str(HERE))
from check_prep import load, validate  # noqa: E402

TRACKS = [
    dict(id='aptitude', order=1, title='Aptitude', summary='Formulas, shortcuts and unlimited practice for quantitative questions.'),
    dict(id='reasoning', order=2, title='Reasoning', summary='Series, codes, directions and syllogisms, with practice that never runs out.'),
    dict(id='puzzles', order=3, title='Puzzles', summary='Classic brainteasers with hints first and a full solution when you want it.'),
    dict(id='cs-fundamentals', order=4, title='CS fundamentals', summary='OOP, DBMS, operating systems, networks and SQL, each guide ending in a quiz.'),
    dict(id='system-design', order=5, title='System design', summary='Caching, load balancing, scaling and queues, plus a traffic playground.'),
]


def check_ids(guides, lessons):
    ids = [g['id'] for g in guides]
    assert len(ids) == len(set(ids)), 'a guide id is used twice'
    challenge_ids = [c['id'] for g in guides for c in g.get('challenges', [])]
    assert len(challenge_ids) == len(set(challenge_ids)), 'a challenge id is used twice'
    # The challenge engine searches lessons first, so a shared id would grade and count as a DSA lesson.
    lesson_ids = {c['id'] for l in lessons for c in l.get('challenges', [])}
    lesson_ids |= {f"challenge-{l['id']}-checkpoint" for l in lessons if l.get('checkpoint')}
    clash = sorted(set(challenge_ids) & lesson_ids)
    assert not clash, f'guide challenge ids already used by lessons: {clash}'


def enrich(content):
    guides = []
    for path in sorted(HERE.glob('*_batch*.py')):
        for g in load(path):
            errors = validate(g)
            assert not errors, f'{g.get("id")} in {path.name}: {errors}'
            guides.append(g)
    check_ids(guides, content.get('lessons', []))
    content['prepTracks'] = TRACKS
    content['guides'] = sorted(guides, key=lambda g: (g['track'], g.get('subject', ''), g['order']))

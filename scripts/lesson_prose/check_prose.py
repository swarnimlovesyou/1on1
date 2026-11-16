"""Checks one batch of lesson prose upgrades. Build-time only.

    python scripts/lesson_prose/check_prose.py 1 [trace-export.json]

For every lesson in batch_<n>.py:
  * the body, worked, invariant and trade-off sections are substantive and new (not a copy of the old body,
    the mental model, or the code section's worked example, which the page already shows),
  * every number in the worked example occurs in the lesson's own Java trace (input, states or result) or is a
    small count, so the walkthrough cannot drift from the animation,
  * each prerequisite concept has one short reason it is needed.
The trace export is the JSON produced for authoring (lesson fields plus trace steps).
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
n = sys.argv[1]
spec = importlib.util.spec_from_file_location(f'batch_{n}', ROOT / f'scripts/lesson_prose/batch_{n}.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
export = {e['id']: e for e in json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))} if len(sys.argv) > 2 else {}
content = json.loads((ROOT / 'backend/src/main/resources/content.json').read_text(encoding='utf-8'))
lessons = {l['id']: l for l in content['lessons']}
NUMBER = re.compile(r'(?<![\w.])-?\d+(?![\w])')


def numbers(value):
    return {int(x) for x in NUMBER.findall(json.dumps(value, ensure_ascii=False))}


failures = 0
for lesson_id, entry in batch.PROSE.items():
    issues = []
    lesson = lessons.get(lesson_id)
    if lesson is None:
        print(f'{lesson_id}: UNKNOWN LESSON')
        failures += 1
        continue
    teaching = lesson.get('teaching') or {}
    old = {lesson['body'].strip(), (teaching.get('mentalModel') or '').strip(), (teaching.get('workedExample') or '').strip()}
    if lesson['body'].strip() == entry.get('body', '').strip():
        old.discard(lesson['body'].strip())  # already merged into content.json
    body = entry.get('body', '').strip()
    if not 350 <= len(body) <= 900:
        issues.append(f'body has {len(body)} characters; write 350-900')
    if body in old:
        issues.append('body repeats existing text')
    for key in ('worked', 'invariant', 'tradeoff'):
        section = entry.get(key) or {}
        title, text = section.get('title', '').strip(), section.get('text', '').strip()
        if not 3 <= len(title) <= 60:
            issues.append(f'{key} needs a title of 3-60 characters')
        if not 250 <= len(text) <= 900:
            issues.append(f'{key} text has {len(text)} characters; write 250-900')
        if text in old:
            issues.append(f'{key} repeats existing text')
    if 'pitfall' in entry and not 80 <= len(entry['pitfall'].strip()) <= 600:
        issues.append('pitfall must be 80-600 characters')
    if lesson_id in export:
        e = export[lesson_id]
        known = numbers(e['experiment']) | numbers(e['traceSteps']) | numbers(e.get('traceResult')) | set(range(0, 11))
        stray = sorted(numbers((entry.get('worked') or {}).get('text', '')) - known)
        if stray:
            issues.append(f'worked example mentions numbers not in the trace: {stray}')
    expected = set(teaching.get('prerequisites', []))
    notes = entry.get('prerequisiteNotes', {})
    if set(notes) != expected:
        issues.append(f'prerequisiteNotes keys {sorted(notes)} must be exactly {sorted(expected)}')
    for key, reason in notes.items():
        if not 30 <= len(reason.strip()) <= 200:
            issues.append(f'prerequisite reason for {key} must be 30-200 characters')
    print(f'{lesson_id}: {"OK" if not issues else "FAIL"}')
    for issue in issues:
        print('   -', issue)
    failures += bool(issues)
print(f'{len(batch.PROSE)} lessons, {failures} failing')
sys.exit(1 if failures else 0)

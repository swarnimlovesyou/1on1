"""Builds the external question bank: metadata and links only, never problem statements.

    python scripts/import_questions.py

Sources:
  * Codeforces official API, problemset.problems (names, ratings, tags).
  * hxu296/leetcode-company-wise-problems-2022 (MIT, (c) 2022 Huan Xu): LeetCode titles, links, difficulty and
    community-reported company tags. LeetCode itself is not contacted.
Rerun by hand to refresh; the app only reads the generated file.
"""
import csv
import io
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'backend/src/main/resources/external-questions.json'
CF_URL = 'https://codeforces.com/api/problemset.problems'
DATASET = 'https://raw.githubusercontent.com/hxu296/leetcode-company-wise-problems-2022/main/data/'


def cf_difficulty(rating):
    if rating is None:
        return None
    return 'Easy' if rating < 1300 else 'Medium' if rating < 1900 else 'Hard'


def cf_record(p):
    return dict(
        id=f"cf-{p['contestId']}{p['index']}", source='Codeforces', title=p['name'],
        url=f"https://codeforces.com/problemset/problem/{p['contestId']}/{p['index']}",
        difficulty=cf_difficulty(p.get('rating')), tags=list(p.get('tags', [])), rating=p.get('rating'), companies={},
    )


def slug(link):
    return link.rstrip('/').rsplit('/', 1)[-1]


def lc_records(problems_csv, companies_csv):
    companies = {}
    rows = csv.reader(io.StringIO(companies_csv))
    next(rows)
    for row in rows:
        # some problem names hold unquoted commas, so read the link first and the company and count last
        # rows without a numeric count are malformed in the source; skip them rather than guess
        if len(row) >= 4 and row[-1].strip().isdigit():
            companies.setdefault(slug(row[0]), {})[row[-2].strip()] = int(row[-1])
        else:
            lc_records.skipped = getattr(lc_records, 'skipped', 0) + 1
    records = []
    for row in csv.DictReader(io.StringIO(problems_csv)):
        s = slug(row['link'])
        records.append(dict(
            id='lc-' + s, source='LeetCode', title=row['name'].strip(), url=row['link'].strip(),
            difficulty=row['difficulty'].strip() if row['difficulty'].strip() in ('Easy', 'Medium', 'Hard') else None,
            tags=[], rating=None, companies=companies.get(s, {}),
        ))
    return records


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': '1on1-question-import'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode('utf-8')


def main():
    cf = json.loads(fetch(CF_URL))
    assert cf['status'] == 'OK', cf.get('comment')
    records = [cf_record(p) for p in cf['result']['problems']]
    records += lc_records(fetch(DATASET + 'leetcode_problems.csv'), fetch(DATASET + 'leetcode_problems_and_companies.csv'))
    records.sort(key=lambda r: (r['source'], r['id']))
    OUT.write_text(json.dumps(records, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    counts = {}
    for r in records:
        counts[r['source']] = counts.get(r['source'], 0) + 1
    print(counts, f'{OUT.stat().st_size / 1e6:.1f} MB', 'skipped malformed company rows:', getattr(lc_records, 'skipped', 0))


if __name__ == '__main__':
    main()

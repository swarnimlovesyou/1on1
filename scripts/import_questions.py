"""Builds the external question bank: metadata and links only, never problem statements.

    python scripts/import_questions.py

Sources:
  * Codeforces official API, problemset.problems (names, ratings, tags).
  * hxu296/leetcode-company-wise-problems-2022 (MIT, (c) 2022 Huan Xu): LeetCode titles, links, difficulty and
    community-reported company tags (data as of May 2022). LeetCode itself is not contacted.
  * neetcode-gh/leetcode .problemSiteData.json (MIT, (c) 2022 neetcode-gh): pattern tags plus the Blind 75 and
    NeetCode 150 lists, written separately to sheets.json.
  * AtCoder Problems by kenkoooo (merged-problems and problem-models; fetched once, politely): ABC, ARC and AGC
    tasks that have a difficulty estimate, linked to atcoder.jp.
  * CSES problem set page: task titles, sections and links only.
Rerun by hand to refresh; the app only reads the generated files.
"""
import csv
import io
import json
import math
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'backend/src/main/resources/external-questions.json'
CF_URL = 'https://codeforces.com/api/problemset.problems'
DATASET = 'https://raw.githubusercontent.com/hxu296/leetcode-company-wise-problems-2022/main/data/'
SHEETS_OUT = ROOT / 'backend/src/main/resources/sheets.json'
NEET_URL = 'https://raw.githubusercontent.com/neetcode-gh/leetcode/main/.problemSiteData.json'
ATCODER_URL = 'https://kenkoooo.com/atcoder/resources/'
CSES_URL = 'https://cses.fi/problemset/'
NEET_CREDIT = 'List from neetcode-gh/leetcode (MIT licence, (c) 2022 neetcode-gh). Titles and links only.'


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


def lc_slug(link):
    return link.strip().strip('/').split('/')[-1]


def neet_item(p):
    s = lc_slug(p['link'])
    return dict(id='lc-' + s, title=p['problem'].strip(), difficulty=p['difficulty'], pattern=p['pattern'],
                url=f'https://leetcode.com/problems/{s}/')


def sheets(neet):
    return [
        dict(id='blind-75', title='Blind 75', credit=NEET_CREDIT,
             summary='A widely shared list of 75 core interview questions.',
             items=[neet_item(p) for p in neet if p.get('blind75')]),
        dict(id='neetcode-150', title='NeetCode 150', credit=NEET_CREDIT,
             summary='Blind 75 extended to 150 questions, grouped by pattern.',
             items=[neet_item(p) for p in neet if p.get('neetcode150')]),
    ]


def merge_neetcode(records, neet):
    """Adds NeetCode's pattern as a tag, and adds its questions the 2022 dataset lacks; company data is kept."""
    by_id = {r['id']: r for r in records}
    for p in neet:
        item = neet_item(p)
        record = by_id.get(item['id'])
        if record is None:
            record = dict(id=item['id'], source='LeetCode', title=item['title'], url=item['url'], difficulty=item['difficulty'],
                          tags=[], rating=None, companies={})
            records.append(record)
            by_id[item['id']] = record
        if item['pattern'] not in record['tags']:
            record['tags'].append(item['pattern'])
    return records


def atcoder_rating(difficulty):
    # AtCoder Problems clips low estimates the same way so they stay positive
    return difficulty if difficulty >= 400 else 400 / math.exp((400 - difficulty) / 400)


def atcoder_records(problems, models):
    records = []
    for p in problems:
        model = models.get(p['id']) or {}
        if not re.fullmatch(r'a[brg]c\d+', p['contest_id']) or 'difficulty' not in model:
            continue
        rating = round(atcoder_rating(model['difficulty']))
        records.append(dict(id='ac-' + p['id'], source='AtCoder', title=p['name'].strip(),
                            url=f"https://atcoder.jp/contests/{p['contest_id']}/tasks/{p['id']}",
                            difficulty='Easy' if rating < 800 else 'Medium' if rating < 1600 else 'Hard',
                            tags=[], rating=rating, companies={}))
    return records


def cses_records(html):
    records, section = [], None
    for match in re.finditer(r'<h2>([^<]+)</h2>|<a href="/problemset/task/(\d+)">([^<]+)</a>', html):
        if match.group(1):
            section = match.group(1).strip()
        else:
            records.append(dict(id='cses-' + match.group(2), source='CSES', title=match.group(3).strip(),
                                url='https://cses.fi/problemset/task/' + match.group(2), difficulty=None,
                                tags=[section] if section else [], rating=None, companies={}))
    return records


def check_floor(source, records, floor):
    # a changed page or API would otherwise replace a whole source with nothing on the next refresh
    assert len(records) >= floor, f'{source}: only {len(records)} records (expected at least {floor}); the source may have changed'
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
    neet = json.loads(fetch(NEET_URL))
    records = merge_neetcode(records, check_floor('NeetCode', neet, 400))
    SHEETS_OUT.write_text(json.dumps(sheets(neet), ensure_ascii=False, indent=1), encoding='utf-8')
    problems = json.loads(fetch(ATCODER_URL + 'merged-problems.json'))
    time.sleep(2)  # the AtCoder Problems API asks for more than a second between requests
    records += check_floor('AtCoder', atcoder_records(problems, json.loads(fetch(ATCODER_URL + 'problem-models.json'))), 2000)
    records += check_floor('CSES', cses_records(fetch(CSES_URL)), 300)
    records.sort(key=lambda r: (r['source'], r['id']))
    OUT.write_text(json.dumps(records, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    counts = {}
    for r in records:
        counts[r['source']] = counts.get(r['source'], 0) + 1
    print(counts, f'{OUT.stat().st_size / 1e6:.1f} MB', 'skipped malformed company rows:', getattr(lc_records, 'skipped', 0))


if __name__ == '__main__':
    main()

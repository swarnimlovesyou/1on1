import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_questions import atcoder_records, cf_difficulty, cf_record, check_floor, cses_records, lc_records, merge_neetcode, sheets  # noqa: E402

PROBLEMS = """name,link,difficulty,solution
Two Sum,https://leetcode.com/problems/two-sum/,Easy    ,x
LRU Cache,https://leetcode.com/problems/lru-cache/,Medium   ,y
Odd Row,https://leetcode.com/problems/odd-row/,Binary Search,z
"""
COMPANIES = """problem_link,problem_name,company_name,num_occur
https://leetcode.com/problems/two-sum/,Two Sum,Google,3
https://leetcode.com/problems/two-sum/,Two Sum,Amazon,1
https://leetcode.com/problems/lru-cache/,LRU Cache,Google,2
https://leetcode.com/problems/lru-cache/,Design, a cache,T-mobile,4
https://leetcode.com/problems/two-sum/,Two Sum,Cognizant,T-mobile
"""


class ImportTest(unittest.TestCase):
    def test_codeforces_rating_maps_to_difficulty(self):
        self.assertIsNone(cf_difficulty(None))
        self.assertEqual(cf_difficulty(800), "Easy")
        self.assertEqual(cf_difficulty(1299), "Easy")
        self.assertEqual(cf_difficulty(1300), "Medium")
        self.assertEqual(cf_difficulty(1899), "Medium")
        self.assertEqual(cf_difficulty(1900), "Hard")

    def test_codeforces_record_keeps_metadata_and_a_link(self):
        r = cf_record({"contestId": 1520, "index": "A", "name": "Do Not Be Distracted!", "rating": 800, "tags": ["brute force"]})
        self.assertEqual(r["id"], "cf-1520A")
        self.assertEqual(r["url"], "https://codeforces.com/problemset/problem/1520/A")
        self.assertEqual(r["difficulty"], "Easy")
        self.assertEqual(r["tags"], ["brute force"])
        self.assertEqual(r["companies"], {})
        self.assertEqual(r["source"], "Codeforces")

    def test_leetcode_records_join_companies_by_link(self):
        rows = {r["id"]: r for r in lc_records(PROBLEMS, COMPANIES)}
        self.assertEqual(set(rows), {"lc-two-sum", "lc-lru-cache", "lc-odd-row"})
        # a difficulty column holding anything else is malformed source data
        self.assertIsNone(rows["lc-odd-row"]["difficulty"])
        self.assertEqual(rows["lc-two-sum"]["difficulty"], "Easy")
        # a row with no count is malformed and skipped, never guessed
        self.assertEqual(rows["lc-two-sum"]["companies"], {"Google": 3, "Amazon": 1})
        self.assertEqual(rows["lc-lru-cache"]["url"], "https://leetcode.com/problems/lru-cache/")
        self.assertEqual(rows["lc-lru-cache"]["source"], "LeetCode")
        # an unquoted comma in a problem name must not shift the company and count columns
        self.assertEqual(rows["lc-lru-cache"]["companies"], {"Google": 2, "T-mobile": 4})


NEET = [
    dict(problem='Contains Duplicate', pattern='Arrays & Hashing', link='contains-duplicate/', difficulty='Easy', neetcode150=True, blind75=True),
    dict(problem='Two Sum', pattern='Arrays & Hashing', link='two-sum/', difficulty='Easy', neetcode150=True, blind75=True),
    dict(problem='Koko Eating Bananas', pattern='Binary Search', link='koko-eating-bananas/', difficulty='Medium', neetcode150=True),
    dict(problem='Extra One', pattern='Greedy', link='extra-one/', difficulty='Hard'),
]


class NeetCodeTest(unittest.TestCase):
    def test_sheets_list_blind_75_and_neetcode_150_in_source_order_with_pattern_and_bank_id(self):
        out = {s['id']: s for s in sheets(NEET)}
        self.assertEqual(['blind-75', 'neetcode-150'], sorted(out))
        self.assertEqual(['lc-contains-duplicate', 'lc-two-sum'], [i['id'] for i in out['blind-75']['items']])
        self.assertEqual(3, len(out['neetcode-150']['items']))
        self.assertEqual(dict(id='lc-koko-eating-bananas', title='Koko Eating Bananas', difficulty='Medium', pattern='Binary Search',
                              url='https://leetcode.com/problems/koko-eating-bananas/'), out['neetcode-150']['items'][2])
        self.assertIn('MIT', out['blind-75']['credit'])

    def test_neetcode_adds_missing_questions_and_pattern_tags_without_losing_company_data(self):
        bank = [dict(id='lc-two-sum', source='LeetCode', title='Two Sum', url='https://leetcode.com/problems/two-sum/',
                     difficulty='Easy', tags=[], rating=None, companies={'Google': 3})]
        merged = {r['id']: r for r in merge_neetcode(bank, NEET)}
        self.assertEqual({'Google': 3}, merged['lc-two-sum']['companies'])
        self.assertEqual(['Arrays & Hashing'], merged['lc-two-sum']['tags'])
        self.assertEqual(['Greedy'], merged['lc-extra-one']['tags'])
        self.assertEqual('LeetCode', merged['lc-extra-one']['source'])
        self.assertEqual(4, len(merged))


class AtCoderTest(unittest.TestCase):
    def test_standard_contests_with_a_difficulty_estimate_become_linked_records(self):
        problems = [
            dict(id='abc300_c', contest_id='abc300', name='Cross'),
            dict(id='arc150_d', contest_id='arc150', name='Hard'),
            dict(id='agc001_a', contest_id='agc001', name='Low'),
            dict(id='abc301_a', contest_id='abc301', name='No model'),
            dict(id='ahc001_a', contest_id='ahc001', name='Heuristic'),
            dict(id='joi2020_a', contest_id='joi2020', name='JOI'),
        ]
        models = {'abc300_c': dict(difficulty=950.4), 'arc150_d': dict(difficulty=2400), 'agc001_a': dict(difficulty=-400),
                  'ahc001_a': dict(difficulty=1000), 'joi2020_a': dict(difficulty=100)}
        out = {r['id']: r for r in atcoder_records(problems, models)}
        self.assertEqual({'ac-abc300_c', 'ac-arc150_d', 'ac-agc001_a'}, set(out))
        c = out['ac-abc300_c']
        self.assertEqual(('AtCoder', 'Cross', 'https://atcoder.jp/contests/abc300/tasks/abc300_c', 'Medium', 950),
                         (c['source'], c['title'], c['url'], c['difficulty'], c['rating']))
        self.assertEqual('Hard', out['ac-arc150_d']['difficulty'])
        self.assertEqual((54, 'Easy'), (out['ac-agc001_a']['rating'], out['ac-agc001_a']['difficulty']), '400 / e^2, clipped above zero')


class CsesTest(unittest.TestCase):
    def test_tasks_are_read_with_their_section_and_link_only(self):
        html = ('<h2>General</h2><ul><li><a href="/problemset/text/2433">Info</a></li></ul>'
                '<h2>Introductory Problems</h2><ul><li class="task"><a href="/problemset/task/1068">Weird Algorithm</a></li>'
                '<li class="task"><a href="/problemset/task/1083">Missing Number</a></li></ul>'
                '<h2>Sorting and Searching</h2><ul><li class="task"><a href="/problemset/task/1621">Distinct Numbers</a></li></ul>')
        out = cses_records(html)
        self.assertEqual(['cses-1068', 'cses-1083', 'cses-1621'], [r['id'] for r in out])
        self.assertEqual(dict(id='cses-1621', source='CSES', title='Distinct Numbers', url='https://cses.fi/problemset/task/1621',
                              difficulty=None, tags=['Sorting and Searching'], rating=None, companies={}), out[2])


class FloorTest(unittest.TestCase):
    def test_a_source_that_suddenly_shrinks_stops_the_import_instead_of_wiping_the_bank(self):
        with self.assertRaisesRegex(AssertionError, 'CSES'):
            check_floor('CSES', [], 300)
        check_floor('CSES', [{}] * 300, 300)


if __name__ == '__main__':
    unittest.main()

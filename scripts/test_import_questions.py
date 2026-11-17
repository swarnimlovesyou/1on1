import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_questions import cf_difficulty, cf_record, lc_records  # noqa: E402

PROBLEMS = """name,link,difficulty,solution
Two Sum,https://leetcode.com/problems/two-sum/,Easy    ,x
LRU Cache,https://leetcode.com/problems/lru-cache/,Medium   ,y
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
        self.assertEqual(set(rows), {"lc-two-sum", "lc-lru-cache"})
        self.assertEqual(rows["lc-two-sum"]["difficulty"], "Easy")
        # a row with no count is malformed and skipped, never guessed
        self.assertEqual(rows["lc-two-sum"]["companies"], {"Google": 3, "Amazon": 1})
        self.assertEqual(rows["lc-lru-cache"]["url"], "https://leetcode.com/problems/lru-cache/")
        self.assertEqual(rows["lc-lru-cache"]["source"], "LeetCode")
        # an unquoted comma in a problem name must not shift the company and count columns
        self.assertEqual(rows["lc-lru-cache"]["companies"], {"Google": 2, "T-mobile": 4})


if __name__ == "__main__":
    unittest.main()

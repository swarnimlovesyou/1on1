import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from prep_content import check_ids  # noqa: E402


def guide(*challenge_ids, gid='guide-cs-fundamentals-a'):
    return dict(id=gid, challenges=[dict(id=c) for c in challenge_ids])


class CheckIdsTest(unittest.TestCase):
    def test_a_guide_question_reusing_a_lesson_challenge_id_is_rejected(self):
        lessons = [dict(id='lesson-x', challenges=[dict(id='challenge-dup')])]
        with self.assertRaisesRegex(AssertionError, 'challenge-dup'):
            check_ids([guide('challenge-dup')], lessons)

    def test_a_guide_question_reusing_a_lesson_checkpoint_id_is_rejected(self):
        lessons = [dict(id='lesson-x', checkpoint=dict(question='q'))]
        with self.assertRaisesRegex(AssertionError, 'challenge-lesson-x-checkpoint'):
            check_ids([guide('challenge-lesson-x-checkpoint')], lessons)

    def test_distinct_ids_pass_and_duplicates_among_guides_fail(self):
        lessons = [dict(id='lesson-x', challenges=[dict(id='challenge-x1')])]
        check_ids([guide('challenge-g1'), guide('challenge-g2', gid='guide-cs-fundamentals-b')], lessons)
        with self.assertRaises(AssertionError):
            check_ids([guide('challenge-g1'), guide('challenge-g1', gid='guide-cs-fundamentals-b')], lessons)
        with self.assertRaises(AssertionError):
            check_ids([guide('challenge-g1'), guide('challenge-g2')], lessons)


if __name__ == '__main__':
    unittest.main()

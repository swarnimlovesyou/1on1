import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_prep import validate  # noqa: E402


def question(n):
    return dict(id=f'challenge-cs-oop-sample-q{n}', kind='prediction', title=f'Question {n}', prompt='Which is true?',
                options=['A', 'B', 'C'], answer=1, explanation='B holds because ...', hint='Think about B.')


GOOD = dict(
    id='guide-cs-fundamentals-oop-sample', kind='guide', track='cs-fundamentals', subject='OOP', title='Sample', order=1,
    summary='A sample guide.', sections=[dict(title=f'Part {i}', text='Some text. ' * 20) for i in range(3)],
    keyPoints=['One', 'Two', 'Three'], challenges=[question(n) for n in range(1, 6)],
)


class ValidateTest(unittest.TestCase):
    def errors_for(self, change):
        g = copy.deepcopy(GOOD)
        change(g)
        return ' '.join(validate(g))

    def test_a_complete_guide_is_valid(self):
        self.assertEqual(validate(GOOD), [])

    def test_quiz_must_have_five_questions(self):
        self.assertIn('challenges', self.errors_for(lambda g: g['challenges'].pop()))

    def test_answer_must_index_an_option(self):
        self.assertIn('answer', self.errors_for(lambda g: g['challenges'][0].update(answer=3)))

    def test_challenge_ids_are_unique(self):
        self.assertIn('duplicate', self.errors_for(lambda g: g['challenges'][1].update(id=g['challenges'][0]['id'])))

    def test_three_to_five_sections(self):
        self.assertIn('sections', self.errors_for(lambda g: g['sections'].pop()))

    def test_explanations_are_required(self):
        self.assertIn('explanation', self.errors_for(lambda g: g['challenges'][2].update(explanation='')))

    def test_subject_is_required_for_cs_fundamentals(self):
        self.assertIn('subject', self.errors_for(lambda g: g.update(subject='Biology')))


    def test_aptitude_and_reasoning_guides_name_a_drill_of_their_own_track(self):
        def make(track, drill):
            def change(g):
                g.update(id=f'guide-{track}-sample', track=track)
                g.pop('subject')
                if drill is not None:
                    g['drill'] = drill
            return change
        self.assertIn('drill', self.errors_for(make('aptitude', None)))
        self.assertIn('drill', self.errors_for(make('aptitude', 'calculus')))
        self.assertIn('drill', self.errors_for(make('reasoning', 'percentages')))
        self.assertEqual('', self.errors_for(make('aptitude', 'percentages')))
        self.assertEqual('', self.errors_for(make('reasoning', 'syllogisms')))

if __name__ == '__main__':
    unittest.main()

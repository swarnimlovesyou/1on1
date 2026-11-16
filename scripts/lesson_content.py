"""Fuller teaching prose for the core lessons that had only a one-line idea and a repeated worked example.
Authored in scripts/lesson_prose/batch_*.py and checked there with check_prose.py against each lesson's own
Java trace, so a worked example cannot drift from the animation."""
import importlib.util
from pathlib import Path

BATCHES = Path(__file__).resolve().parent / 'lesson_prose'


def load():
    entries = {}
    for path in sorted(BATCHES.glob('batch_*.py')):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for lesson_id, entry in module.PROSE.items():
            assert lesson_id not in entries, f'{lesson_id} is authored in two batches'
            entries[lesson_id] = entry
    return entries


# the reference journeys already have full prose; they only lacked reasons for their prerequisites
REFERENCE_PREREQUISITES = {
    'lesson-sliding-window': {
        'concept-arrays': 'A window is a run of adjacent indexes, so you need constant-time access by position.',
        'concept-prefix-sums': 'Both reuse a running total; the window adds one value and removes one instead of recomputing.',
    },
    'lesson-bst': {
        'concept-binary-search': 'Each comparison discards one side, the same halving idea applied to a linked structure.',
        'concept-binary-trees': 'Insertion and search walk left and right child links, and in-order traversal reads the keys back.',
    },
    'lesson-bfs': {
        'concept-queues': 'The FIFO queue is what makes nearer vertices finish before farther ones.',
        'concept-graphs': 'BFS walks adjacency lists, so you need to read a vertex\'s outgoing edges.',
    },
}


QUICKSORT_JAVA = '''static void quickSort(int[] a, int lo, int hi) {
        if (lo >= hi) return;
        int pivot = a[hi], boundary = lo;
        for (int i = lo; i < hi; i++) {
            if (a[i] <= pivot) {
                int t = a[i]; a[i] = a[boundary]; a[boundary] = t;
                boundary++;
            }
        }
        int t = a[hi]; a[hi] = a[boundary]; a[boundary] = t;
        quickSort(a, lo, boundary - 1);
        quickSort(a, boundary + 1, hi);
    }

    static int[] sorted(int[] a) {
        int[] copy = a.clone();
        quickSort(copy, 0, copy.length - 1);
        return copy;
    }'''

# The sorting concept's teaching block is about merging; Quicksort shared it and showed merge code.
LESSON_TEACHING = {
    'lesson-quick-sort': dict(
        title='Quicksort',
        mentalModel='Pick a pivot, move every value that is not larger to its left, and the pivot lands in its final sorted place. Each side is then sorted on its own.',
        invariant='During a partition, everything left of the boundary is at most the pivot and everything between the boundary and the scan is larger.',
        commonMistake='Forgetting to exclude the placed pivot from both recursive calls loops forever on equal values. A last-element pivot on already sorted input gives the O(n²) worst case.',
        workedExample='Sort [3,1,2] with pivot 2. Scanning 3 leaves it in place because it is larger. Scanning 1 swaps it to the boundary, giving [1,3,2]. Swapping the pivot into the boundary gives [1,2,3]; the sides [1] and [3] are already sorted.',
        objectives=['Partition a range around a pivot with one left-to-right scan.', 'Explain why a bad pivot sequence costs O(n²) while balanced splits cost O(n log n).'],
        complexity=dict(time='Average O(n log n); worst O(n²) when every pivot is the smallest or largest value', space='O(log n) average call stack; O(n) in the worst case', assumptions='Last-element pivot (Lomuto partition), sorting in place; not stable.'),
        java=dict(
            language='java', className='CurriculumExample', implementation=QUICKSORT_JAVA,
            source='import java.util.*;\nclass CurriculumExample {\n' + QUICKSORT_JAVA + '\n}',
            cases=[
                dict(expression='Arrays.toString(sorted(new int[]{3,1,2}))', expected='[1, 2, 3]'),
                dict(expression='Arrays.toString(sorted(new int[]{2,2,1,2}))', expected='[1, 2, 2, 2]'),
                dict(expression='Arrays.toString(sorted(new int[]{1,2,3,4}))', expected='[1, 2, 3, 4]'),
                dict(expression='Arrays.toString(sorted(new int[]{}))', expected='[]'),
            ],
            lineAnnotations=[
                dict(line=3, explanation='The last value of the range is the pivot; boundary marks where the next small value goes.'),
                dict(line=5, explanation='Values at most the pivot are swapped to the boundary, so the left part stays small.'),
                dict(line=10, explanation='Swapping the pivot to the boundary puts it in its final sorted position.'),
                dict(line=11, explanation='Both recursive calls exclude the placed pivot, so every call shrinks the range.'),
            ],
        ),
        visualization=dict(exampleInput='[3,1,2], pivot 2', expectedStates=['scan 3: larger, stays', 'scan 1: swap to boundary, [1,3,2]', 'place pivot, [1,2,3]', 'sides [1] and [3] are already sorted']),
    ),
}


def enrich(lessons):
    entries = load()
    for lesson in lessons:
        if lesson['id'] in LESSON_TEACHING:
            override = LESSON_TEACHING[lesson['id']]
            teaching = dict(lesson['teaching'])
            teaching.update({k: v for k, v in override.items() if k != 'visualization'})
            teaching['visualization'] = {**teaching['visualization'], **override['visualization']}
            lesson['teaching'] = teaching
        if lesson['id'] in REFERENCE_PREREQUISITES:
            lesson['prerequisiteNotes'] = REFERENCE_PREREQUISITES[lesson['id']]
        entry = entries.pop(lesson['id'], None)
        if entry is None:
            continue
        lesson['body'] = entry['body'].strip()
        lesson['blocks'] = [
            dict(id=key, kind='explanation', title=entry[key]['title'].strip(), text=entry[key]['text'].strip(), lines=[])
            for key in ('worked', 'invariant', 'tradeoff')
        ]
        if entry.get('pitfall'):
            lesson['pitfall'] = entry['pitfall'].strip()
        lesson['prerequisiteNotes'] = {k: v.strip() for k, v in entry.get('prerequisiteNotes', {}).items()}
    assert not entries, f'prose for unknown lessons: {sorted(entries)}'

"""Batch 1 upgrades: Python references, specific hints, editorials and adversarial cases."""

PROBLEMS = {
    'silent-sensors': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
print(sum(1 for value in values if value == 0))
''',
        hints=[
            'Only one property of each reading matters here: whether it is exactly zero. Its sign and size are irrelevant.',
            'Keep a single running counter. Each reading either adds one to it or leaves it unchanged.',
            'Scan the readings once and increment the counter on every value equal to 0. Negative numbers are not zero, and a line with no zeros must still print 0.',
        ],
        editorial=(
            'Walk through the readings once, keeping a counter of how many equal zero. The invariant is simple: '
            'after looking at the first i readings, the counter holds exactly the number of zeros among them, so '
            'after the last reading it holds the answer. Each reading is inspected once, so the time is O(n) and, '
            'apart from storing the input, the extra space is O(1). There is nothing to sort or remember. Edge '
            'cases: a sequence with no zeros at all prints 0 (not an empty line), a single reading of 0 prints 1, '
            'and a run where every reading is zero prints n. Negative readings are never zero, however close to it.'
        ),
        cases=[
            ('-10000 0 10000 0\n', '2\n'),
            ('0\n', '1\n'),
        ],
    ),
    'distinct-stations': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
print(len(set(values)))
''',
        hints=[
            'Duplicates should only be counted once, no matter how many times or where they appear.',
            'A hash set remembers which values you have already seen, and its size is the number of distinct values.',
            'Insert every reading into a set and print its size. Remember that 7 and -7 are different readings, and a line where all readings are equal has exactly one distinct value.',
        ],
        editorial=(
            'Insert every reading into a hash set and print the size of the set. A set stores each value at most '
            'once, so the invariant after processing i readings is that the set contains exactly the distinct values '
            'among them. Insertion is expected O(1), giving O(n) expected time and O(n) space. A slower but equally '
            'valid alternative is to sort the readings and count positions where a value differs from its '
            'predecessor, which costs O(n log n) time and no hashing. Edge cases: a single reading gives 1, '
            'all-equal readings give 1, and a value and its negation (for example 10000 and -10000) are counted '
            'separately.'
        ),
        cases=[
            ('-10000 10000 -10000 10000\n', '2\n'),
            ('7 7 7 7 7 -7\n', '2\n'),
        ],
    ),
    'zero-tail': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
non_zero = [value for value in values if value != 0]
result = non_zero + [0] * (len(values) - len(non_zero))
print(' '.join(map(str, result)))
''',
        hints=[
            'The non-zero readings must keep their original relative order; only the zeros move, and they all end up at the back.',
            'Use a write position: it marks where the next non-zero value should be placed in the array.',
            'Copy each non-zero value to the write position and advance it, then fill every remaining slot with 0. Make sure leading zeros and negative values are handled, since only exact zeros move.',
        ],
        editorial=(
            'Use two pointers: a read pointer that visits every reading and a write pointer that marks the next free '
            'slot for a non-zero value. Whenever the read pointer finds a non-zero value, copy it to the write slot '
            'and advance the write pointer. Afterwards, fill the rest of the array with zeros. The invariant is that '
            'the prefix before the write pointer holds exactly the non-zero values seen so far, in their original '
            'order, so the result is stable. This runs in O(n) time and O(1) extra space in place. Edge cases: an '
            'array with no zeros is unchanged, an all-zero array is unchanged, and leading zeros must all travel to '
            'the end while negative values stay put.'
        ),
        cases=[
            ('0 0 5 0 -3\n', '5 -3 0 0 0\n'),
            ('0 -10000 0 10000\n', '-10000 10000 0 0\n'),
        ],
    ),
    'profitable-stretch': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
current = best = values[0]
for value in values[1:]:
    # Either extend the stretch ending at the previous reading or start fresh here.
    current = max(value, current + value)
    best = max(best, current)
print(best)
''',
        hints=[
            'The stretch must be nonempty, so when every reading is negative the answer is the largest single reading, not 0.',
            'For each position, track the best sum of a stretch that ends exactly there.',
            'The best stretch ending at i is either the reading alone or the best stretch ending at i-1 plus the reading (Kadane). Keep the overall maximum, and start both values from the first reading rather than from 0.',
        ],
        editorial=(
            "This is Kadane's algorithm. Let current be the best sum of a stretch ending at the current position. "
            'For the next reading x, the best stretch ending there either starts fresh at x or extends the previous '
            'one, so current becomes max(x, current + x). Track the largest current ever seen. The invariant is '
            'that after position i, current is the optimum for stretches ending at i and best is the optimum for '
            'stretches ending anywhere up to i. It takes O(n) time and O(1) space, versus O(n squared) for trying '
            'every start and end with running sums. Edge cases: initialise from the first reading, not 0, so an '
            'all-negative input returns its largest value; a single reading is its own answer.'
        ),
        cases=[
            ('-3 -1 -2\n', '-1\n'),
            ('3 -2 5 -10000 4\n', '6\n'),
        ],
    ),
    'left-rotation': dict(
        python='''import sys

values = sys.stdin.read().split()
print(' '.join(values[1:] + values[:1]))
''',
        hints=[
            'Every reading shifts one place to the left, and the first reading wraps around to become the last.',
            'Index arithmetic modulo n describes the wrap: the output at position i comes from input position (i + 1) mod n.',
            'Print readings 2..n followed by reading 1. With a single reading the output equals the input, and duplicates are moved like any other value.',
        ],
        editorial=(
            'A left rotation by one moves the reading at position i to position i - 1 and sends the first reading '
            'to the end. Equivalently, output position i takes input position (i + 1) mod n. You can print the '
            'readings from index 1 to the end and then the reading at index 0, or rotate in place by saving the '
            'first value, shifting everything left by one, and writing the saved value into the last slot. Both '
            'run in O(n) time; the in-place version uses O(1) extra space. The invariant of the in-place shift is '
            'that after step i, slots 0..i-1 already hold their final values. Edge cases: a single reading is '
            'unchanged, and with two readings the rotation simply swaps them.'
        ),
        cases=[
            ('7 -3\n', '-3 7\n'),
            ('10000 0 0 -10000\n', '0 0 -10000 10000\n'),
        ],
    ),
    'zero-sum-stretches': dict(
        python='''import sys
from collections import defaultdict

values = [int(token) for token in sys.stdin.read().split()]
seen = defaultdict(int)
seen[0] = 1  # the empty prefix
prefix = total = 0
for value in values:
    prefix += value
    total += seen[prefix]
    seen[prefix] += 1
print(total)
''',
        hints=[
            'A stretch from i to j sums to zero exactly when the prefix sum before i equals the prefix sum through j.',
            'Keep a hash map from each prefix sum to how many times it has appeared so far, including the empty prefix with sum 0.',
            'For each new prefix sum, add the number of earlier equal prefix sums to the answer, then record it. Repeated zeros are the trap: three zeros alone form six zero-sum stretches.',
        ],
        editorial=(
            'Let P(k) be the sum of the first k readings, with P(0) = 0. The stretch from position i+1 to j sums to '
            'zero exactly when P(i) = P(j). So scan left to right, maintaining a hash map counting how often each '
            'prefix sum has occurred. At each step compute the new prefix sum, add its current count to the answer '
            '(each earlier equal prefix starts one zero-sum stretch ending here), then increment its count. Seeding '
            'the map with sum 0 once accounts for stretches that start at the first reading. Time is O(n) expected '
            'and space O(n), versus O(n squared) for checking every pair. Edge cases: alternating values like 5 -5 '
            '5 -5 produce overlapping stretches, and a run of k zeros contributes k(k+1)/2.'
        ),
        cases=[
            ('5 -5 5 -5\n', '4\n'),
            ('0\n', '1\n'),
        ],
    ),
    'lower-middle': dict(
        python='''import sys

values = sorted(int(token) for token in sys.stdin.read().split())
print(values[(len(values) - 1) // 2])
''',
        hints=[
            'For an even number of readings there are two middle values; this problem always wants the smaller one, at sorted index floor((n-1)/2).',
            'Once the readings are in sorted order, the answer is just the value at a fixed index.',
            'Sort (or use quickselect for expected linear time) and read index (n-1)//2. Duplicates and negative values are fine: ties do not change which value sits at that index.',
        ],
        editorial=(
            'Sort the readings and print the one at index floor((n-1)/2). For odd n this is the true middle; for '
            'even n it is the lower of the two middle values. Sorting is correct because the element at sorted '
            'index k is by definition the value with exactly k readings at or before it in order. This takes '
            'O(n log n) time and O(n) space. An alternative is randomized quickselect: partition around a random '
            'pivot and recurse only into the side that contains index k, which runs in expected O(n) time. Edge '
            'cases: a single reading is its own median, two readings return the smaller, and heavy duplicates '
            'such as -10000 -10000 10000 10000 return -10000.'
        ),
        cases=[
            ('3 1\n', '1\n'),
            ('10000 -10000 10000 -10000\n', '-10000\n'),
        ],
    ),
    'suffix-leaders': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
leaders = []
best_to_right = None
for value in reversed(values):
    if best_to_right is None or value > best_to_right:
        leaders.append(value)
        best_to_right = value
leaders.reverse()
print(' '.join(map(str, leaders)))
''',
        hints=[
            'Whether a reading is a leader depends only on the largest value to its right, so it is natural to scan from the right end.',
            'Keep the maximum of everything already scanned. A reading is a leader exactly when it beats that maximum.',
            'Scan right to left, collect readings strictly greater than the running maximum, update the maximum, and reverse the collection at the end. Equal values are not leaders, so in 3 3 3 1 only one 3 qualifies.',
        ],
        editorial=(
            'Scan from right to left while tracking the largest value seen so far. The last reading is always a '
            'leader. Every other reading is a leader exactly when it is strictly greater than the running maximum; '
            'when it is, record it and make it the new maximum. Because leaders are found in reverse order, reverse '
            'the list before printing. The invariant is that before visiting position i, the running maximum is the '
            'largest value strictly to the right of i. This takes O(n) time and O(n) space for the output, compared '
            'with O(n squared) for comparing each reading against everything to its right. Edge cases: strictly '
            'decreasing input makes every reading a leader, and ties are not leaders, so 0 0 0 prints a single 0.'
        ),
        cases=[
            ('3 3 3 1\n', '3 1\n'),
            ('-10000 -9999 -10000\n', '-9999 -10000\n'),
        ],
    ),
    'distinct-letters': dict(
        python='''import sys

text = sys.stdin.read().strip()
print(len(set(text)))
''',
        hints=[
            'Every character counts, including inner spaces and punctuation, and uppercase and lowercase letters are different characters.',
            'A set of characters records each character the first time it appears and ignores later repeats.',
            'Strip only the outer whitespace, add every remaining character to a set, and print its size. Spaces inside the text count as one distinct character no matter how many there are.',
        ],
        editorial=(
            'Remove leading and trailing whitespace, then insert every character of the line into a hash set and '
            'print the set size. The set holds each character at most once, so after processing a prefix it '
            'contains exactly the distinct characters of that prefix. Since the input is ASCII you can equally use '
            'a boolean array of 128 entries and count how many flip to true. Time is O(n); space is O(1) because '
            'the alphabet is bounded. Edge cases: case matters (A and a differ), inner spaces count once, outer '
            'spaces do not count at all, and a single character prints 1.'
        ),
        cases=[
            ('a b a b\n', '3\n'),
            ('  Zz zZ  \n', '3\n'),
        ],
    ),
    'longest-unique': dict(
        python='''import sys

text = sys.stdin.read().strip()
last_seen = {}
left = best = 0
for right, char in enumerate(text):
    # Jump the window start past the previous copy, but never move it backwards.
    if char in last_seen and last_seen[char] >= left:
        left = last_seen[char] + 1
    last_seen[char] = right
    best = max(best, right - left + 1)
print(best)
''',
        hints=[
            'A valid substring is a window with no repeated characters; when a repeat enters on the right, only the left edge needs to move.',
            'Remember the last index where each character appeared. That tells you exactly where the window must start to exclude the earlier copy.',
            'For each right end, set left to the larger of its current value and last-seen index plus one, then measure the window. Taking the larger value matters: in abba the old a must not pull left backwards.',
        ],
        editorial=(
            'Use a sliding window [left, right] that never contains a repeated character, plus a map from each '
            'character to the last index where it appeared. When extending right to a character whose last '
            'occurrence is inside the window, move left just past that occurrence; if the last occurrence is '
            'already left of the window, leave left alone. The invariant is that the window is always the longest '
            'duplicate-free substring ending at right, so the best window length seen is the answer. Each index is '
            'visited once, giving O(n) time and O(alphabet) space, versus O(n squared) or worse for checking every '
            'substring. Edge cases: abba (left must not move backwards), a string of one repeated character gives '
            '1, and spaces are ordinary characters.'
        ),
        cases=[
            ('abba\n', '2\n'),
            ('tmmzuxt\n', '5\n'),
        ],
    ),
    'factorial-lock': dict(
        python='''import sys

n = int(sys.stdin.read().strip())
result = 1
for i in range(2, n + 1):
    result *= i
print(result)
''',
        hints=[
            'n! is the product 1 x 2 x ... x n, and by definition 0! is 1.',
            'The recursive definition n! = n x (n-1)! with base case 0! = 1 translates directly into a loop or a recursive call.',
            'Start an accumulator at 1 and multiply by every integer from 2 to n. 15! is about 1.3 trillion, which overflows a 32-bit int, so use a 64-bit type in languages with fixed-width integers.',
        ],
        editorial=(
            'Factorial follows the recurrence n! = n x (n-1)! with base case 0! = 1. Either recurse with that '
            'definition or, equivalently, keep a running product starting at 1 and multiply in 2, 3, ..., n. The '
            'invariant of the loop is that after multiplying by i the accumulator equals i!. Both take O(n) '
            'multiplications; the loop uses O(1) space while recursion uses O(n) stack frames, which is harmless '
            'for n at most 15. Edge cases: n = 0 and n = 1 both print 1 because the loop body never runs, and 15! '
            '= 1307674368000 exceeds the 32-bit range, so a 64-bit integer is required in Java or C++.'
        ),
        cases=[
            ('4\n', '24\n'),
            ('14\n', '87178291200\n'),
        ],
    ),
    'balanced-tree-nodes': dict(
        python='''import sys

n = int(sys.stdin.read().strip())
print((1 << n) - 1)
''',
        hints=[
            'In a perfect binary tree every level is full, so level k (counting from 0) holds exactly 2^k nodes.',
            'Add up the levels: 1 + 2 + 4 + ... + 2^(n-1) is a geometric series with a closed form.',
            'The total is 2^n - 1, which a left shift computes directly. Check the boundaries: zero levels gives 0, and 30 levels gives 1073741823, close to the 32-bit limit.',
        ],
        editorial=(
            'A perfect binary tree with n levels has 1 node on the first level, 2 on the second, and 2^(k) on level '
            'k counting from zero. The total 1 + 2 + ... + 2^(n-1) is a geometric series equal to 2^n - 1, which '
            'you can see by induction: adding a new full level of 2^n nodes to a tree of 2^n - 1 nodes gives '
            '2^(n+1) - 1. Compute it with a left shift, (1 << n) - 1, in O(1) time and space; a recursive count '
            'of nodes(n) = 1 + 2 x nodes(n-1) is an O(n) alternative. Edge cases: n = 0 prints 0, n = 1 prints 1, '
            'and n = 30 prints 1073741823, which still fits in 32 bits but is safest computed with a 64-bit shift.'
        ),
        cases=[
            ('30\n', '1073741823\n'),
            ('4\n', '15\n'),
        ],
    ),
    'island-groups': dict(
        python='''import sys

numbers = [int(token) for token in sys.stdin.read().split()]
n = numbers[0]
parent = list(range(n))


def find(v):
    while parent[v] != v:
        parent[v] = parent[parent[v]]  # path halving keeps trees shallow
        v = parent[v]
    return v


components = n
for i in range(2, len(numbers), 2):
    root_u, root_v = find(numbers[i]), find(numbers[i + 1])
    if root_u != root_v:
        parent[root_u] = root_v
        components -= 1
print(components)
''',
        hints=[
            'Every vertex starts as its own group, and each edge can merge at most two groups into one. Isolated vertices still count.',
            'A disjoint-set union (union-find) tracks which group each vertex belongs to via a representative root.',
            'Start with n components; for each edge, find both roots and, only if they differ, union them and subtract one. Self loops and parallel edges join a vertex to its own group, so they must not decrease the count.',
        ],
        editorial=(
            'Start with n components, one per vertex, and process edges with a disjoint-set union. For edge u v, '
            'find the root of each endpoint; if the roots differ, link one under the other and decrease the '
            'component count, otherwise the edge is redundant. The invariant is that after each edge the count '
            'equals the number of distinct roots, which is the number of connected components of the edges seen '
            'so far. With path compression and union by size this is nearly O(n + m) time and O(n) space. A BFS or '
            'DFS over an adjacency list is an equally valid O(n + m) alternative. Edge cases: m = 0 gives n, self '
            'loops and parallel edges never merge anything, and vertices with no edges are components on their own.'
        ),
        cases=[
            ('5 3 1 1 3 3 3 3\n', '5\n'),
            ('6 4 0 5 5 0 2 4 4 2\n', '4\n'),
        ],
    ),
}

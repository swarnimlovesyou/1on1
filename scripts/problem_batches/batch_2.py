"""Batch 2 problem upgrades: Python reference, hints, editorial and two adversarial cases each."""

PROBLEMS = {
    'reverse-route': dict(
        python='''import sys

values = sys.stdin.read().split()
# Walk the list from the back to the front.
print(' '.join(reversed(values)))
''',
        hints=[
            'There is no leading count: every token on the input line is a reading, so read the whole input and split it on whitespace.',
            'The last reading must be printed first. A stack does exactly this: push in input order, pop in reverse order. Walking an array backwards is the same idea.',
            'Iterate the index from the last position down to 0 and join the values with single spaces. A single reading is its own reverse, and negative values must keep their minus sign.',
        ],
        editorial=(
            'Read every token, then output them from the last index down to the first. This is the stack idea in its '
            'simplest form: the first item in is the last item out. Correctness is direct, since position i of the '
            'output holds input position n-1-i, which is exactly the reversed order. The tokens never need to be '
            'parsed as numbers because reversing does not depend on their values, so printing them unchanged keeps '
            'signs such as -10000 intact. Time is O(n) for one pass and space is O(n) for the stored list (an '
            'in-place two-pointer swap would also work). Edge cases: a single reading prints itself, repeated values '
            'stay in their mirrored positions, and the output has no trailing separator.'
        ),
        cases=[
            ('-10000 10000\n', '10000 -10000\n'),
            ('7 7 -3 7\n', '7 -3 7 7\n'),
        ],
    ),
    'repeat-visits': dict(
        python='''import sys

values = list(map(int, sys.stdin.read().split()))
# Every reading that is not the first of its value is a repeat.
print(len(values) - len(set(values)))
''',
        hints=[
            'Only the first occurrence of each value is "new"; every later occurrence of that value counts once toward the answer.',
            'Keep a set of values already seen. A reading whose value is already in the set is a repeat visit.',
            'Equivalently, the answer is the total number of readings minus the number of distinct values. Check 4 4 4: three readings, one distinct value, answer 2, not 3 pairs.',
        ],
        editorial=(
            'Each distinct value contributes exactly one first occurrence, and every other reading is a repeat. So '
            'the answer is n minus the number of distinct values. Build a hash set of the readings and subtract its '
            'size from n. Equivalently, scan left to right with a set and add one whenever the value is already '
            'present; both views count every non-first occurrence exactly once. Time is O(n) expected with hashing '
            'and space is O(d) for d distinct values. A sorting baseline (sort, then count positions equal to their '
            'left neighbour) runs in O(n log n). Edge cases: a single reading or all-distinct input gives 0, and '
            'k copies of one value give k-1, not the number of equal pairs.'
        ),
        cases=[
            ('-10000 -10000 -10000 10000 10000\n', '3\n'),
            ('5 -5 5 -5 5\n', '3\n'),
        ],
    ),
    'ordered-check': dict(
        python='''import sys

values = list(map(int, sys.stdin.read().split()))
ordered = all(values[i - 1] <= values[i] for i in range(1, len(values)))
print('YES' if ordered else 'NO')
''',
        hints=[
            'Nondecreasing means equal neighbours are fine; only a strict drop breaks the order.',
            'You never need to compare non-adjacent readings: if every adjacent pair is in order, the whole sequence is in order.',
            'Scan i from 1 to n-1 and answer NO as soon as a[i] < a[i-1]. A single reading is trivially ordered, and a drop at the very last pair must still be caught.',
        ],
        editorial=(
            'Compare each reading with the one before it. If some a[i] is strictly smaller than a[i-1] the sequence '
            'is not nondecreasing, so print NO; if the scan finishes without a drop, print YES. This is correct '
            'because order is transitive: a[0] <= a[1] <= ... <= a[n-1] holds exactly when every adjacent pair holds, '
            'so checking n-1 neighbours is enough. Time is O(n) and space is O(1) beyond the input (you can stop at '
            'the first drop). Sorting a copy and comparing would also work but costs O(n log n). Edge cases: a '
            'single reading and all-equal readings are YES, and a violation at the final pair must not be missed.'
        ),
        cases=[
            ('-10000 10000\n', 'YES\n'),
            ('1 2 2 3 3 2\n', 'NO\n'),
        ],
    ),
    'nonadjacent-stops': dict(
        python='''import sys

values = list(map(int, sys.stdin.read().split()))
# best: best total using the readings seen so far; prev: best total one reading earlier.
prev, best = 0, 0
for x in values:
    prev, best = best, max(best, prev + x)
print(best)
''',
        hints=[
            'Choosing nothing is allowed, so the answer is never negative, and greedy picks (largest first, or every other value) can fail.',
            'For each prefix, track the best total that uses only that prefix. At each reading you either skip it, or take it and add the best total from two positions back.',
            'Keep two rolling numbers: best up to the previous reading and best up to the one before that. Start both at 0 so that an all-negative input yields 0.',
        ],
        editorial=(
            'Let best[i] be the maximum total using only the first i readings with no two chosen values adjacent. '
            'For reading i you either skip it, giving best[i-1], or take it, which forbids reading i-1 and gives '
            'best[i-2] + a[i]. So best[i] = max(best[i-1], best[i-2] + a[i]) with best[0] = best[-1] = 0. The '
            'base value 0 encodes the empty choice, which is why negatives are simply never taken. Only the last two '
            'values are needed, so keep two variables. Time O(n), space O(1). Trying every subset is O(2^n). Edge '
            'cases: all-negative input gives 0, zeros are harmless, and greedy choices such as 5 1 1 5 (answer 10) '
            'show why the recurrence is needed.'
        ),
        cases=[
            ('-3 -1 -7 -2\n', '0\n'),
            ('5 1 1 5\n', '10\n'),
        ],
    ),
    'equal-pairs': dict(
        python='''import sys

values = list(map(int, sys.stdin.read().split()))
seen = {}
total = 0
for x in values:
    # x pairs with every earlier copy of itself.
    total += seen.get(x, 0)
    seen[x] = seen.get(x, 0) + 1
print(total)
''',
        hints=[
            'A pair is only about equal values, so positions matter only through how many copies of each value exist.',
            'Scan left to right with a hash map from value to how many times it has appeared so far. The current reading forms a pair with each earlier copy.',
            'Add the stored count before incrementing it. A value that appears k times contributes k*(k-1)/2 pairs, so five equal readings give 10, not 5.',
        ],
        editorial=(
            'Walk the readings once while a hash map stores how many times each value has been seen. When reading '
            'x arrives, it forms a valid pair (i < j) with every earlier copy, so add count[x] to the total and then '
            'increment count[x]. Every pair is counted exactly once, at the moment its later element is processed. '
            'Summing per value gives 0 + 1 + ... + (k-1) = k(k-1)/2 for k copies. Time is O(n) expected and space '
            'O(d) for d distinct values; checking all pairs directly is O(n^2). Edge cases: a single reading or '
            'all-distinct input gives 0, and the total can reach about 500000 for 1000 equal readings, which fits easily.'
        ),
        cases=[
            ('7 7 7 7 7\n', '10\n'),
            ('-10000 10000 -10000 10000 -10000\n', '4\n'),
        ],
    ),
    'next-taller': dict(
        python='''import sys

values = list(map(int, sys.stdin.read().split()))
answer = [-1] * len(values)
stack = []  # indices still waiting for a larger value; their values never increase upward
for i, x in enumerate(values):
    while stack and values[stack[-1]] < x:
        answer[stack.pop()] = x
    stack.append(i)
print(' '.join(map(str, answer)))
''',
        hints=[
            'A brute-force scan to the right for each reading is O(n^2). Notice that once a larger value appears, it answers every smaller value still waiting before it.',
            'Keep a stack of indices that have not found their answer yet. Their values are nonincreasing from bottom to top.',
            'For each new reading, pop while the top value is strictly smaller and record the new reading as its answer, then push the new index. Equal values do not pop each other, and anything left at the end gets -1.',
        ],
        editorial=(
            'Use a monotonic stack of indices whose next strictly larger value is still unknown. When reading x '
            'arrives, every waiting index with a smaller value has x as its answer, because x is the first larger '
            'value seen to its right; pop those and record x. Then push the current index. Invariant: the stack '
            'values are nonincreasing from bottom to top, so the pops always come from the top. Each index is '
            'pushed and popped at most once, giving O(n) time and O(n) space, versus O(n^2) for scanning right from '
            'each position. Edge cases: equal readings are not strictly larger, so 5 5 4 6 gives 6 6 6 -1; '
            'indices still on the stack at the end print -1, including the last reading.'
        ),
        cases=[
            ('5 5 4 6\n', '6 6 6 -1\n'),
            ('-10000 -10000 10000 10000\n', '10000 10000 -1 -1\n'),
        ],
    ),
    'distinct-sorted': dict(
        python='''import sys

values = set(map(int, sys.stdin.read().split()))
print(' '.join(map(str, sorted(values))))
''',
        hints=[
            'Two separate jobs are hiding here: removing duplicates and putting the survivors in ascending order.',
            'A hash set removes duplicates in one pass; then sort what is left. Alternatively sort first and skip any value equal to its left neighbour.',
            'Parse the readings as integers before sorting, otherwise text order puts -2 after -10 and 10 before 9.',
        ],
        editorial=(
            'Insert every reading into a hash set, which keeps one copy of each value, then sort the set and print '
            'it. The output contains every value that appears (the set loses none) exactly once (the set keeps no '
            'duplicates) in ascending order (the sort). Time is O(n + d log d) for d distinct values and space is '
            'O(d). An equivalent approach sorts all n readings and prints a value only when it differs from the '
            'previous one, which is O(n log n). Edge cases: sort numerically, not as strings, so negatives such as '
            '-10000 come first; all-equal input prints a single value; a single reading prints itself.'
        ),
        cases=[
            ('10000 -10000 0 10000 -10000\n', '-10000 0 10000\n'),
            ('-3 -3 -3 -10 -2\n', '-10 -3 -2\n'),
        ],
    ),
    'mirror-word': dict(
        python='''import sys

text = sys.stdin.read().strip()
left, right = 0, len(text) - 1
is_palindrome = True
while left < right:
    if text[left] != text[right]:
        is_palindrome = False
        break
    left += 1
    right -= 1
print('YES' if is_palindrome else 'NO')
''',
        hints=[
            'Outer whitespace is ignored but everything inside the line counts: spaces, digits, punctuation and letter case are all compared exactly.',
            'A palindrome reads the same from both ends, so character i must equal character n-1-i for every i.',
            'Strip the line first, then move two pointers inward from both ends and stop at the first mismatch. Do not lowercase anything: Racecar is NO.',
        ],
        editorial=(
            'Strip the outer whitespace, then place one pointer at the start and one at the end. While they have not '
            'met, compare the two characters; any mismatch means NO, otherwise move both inward. If the pointers meet '
            'or cross, every mirrored pair matched, so the text is a palindrome and the answer is YES. The middle '
            'character of an odd-length text pairs with itself and never needs checking. Time O(n), extra space '
            'O(1); building the reversed string and comparing is also O(n) but uses O(n) extra space. Edge cases: '
            'a single character is YES, comparison is case-sensitive, and inner spaces are real characters.'
        ),
        cases=[
            ('Racecar\n', 'NO\n'),
            ('   ab ba   \n', 'YES\n'),
        ],
    ),
    'first-single': dict(
        python='''import sys
from collections import Counter

text = sys.stdin.read().strip()
counts = Counter(text)
# Second pass in original order finds the earliest character seen exactly once.
print(next((ch for ch in text if counts[ch] == 1), 'NONE'))
''',
        hints=[
            'You need the count of each character over the whole line before you can decide whether an early character is unique.',
            'Make two passes: first count every character, then walk the line again in order and stop at the first character whose count is 1.',
            'Characters are compared exactly, so a and A are different. If no count equals 1, print NONE.',
        ],
        editorial=(
            'Count the occurrences of every character in one pass using a hash map (or a 128-entry array for ASCII). '
            'Then scan the stripped line again from the left and print the first character whose count is 1. The '
            'second scan follows the original order, so the first hit is the earliest unique character; if the scan '
            'ends without a hit, print NONE. Time O(n) and space O(alphabet). The naive way, checking for each '
            'position whether the character occurs elsewhere, is O(n^2). Edge cases: comparison is case-sensitive '
            '(in aAa the answer is A), the unique character may be the last one, and a line where everything repeats '
            'prints NONE.'
        ),
        cases=[
            ('aAa\n', 'A\n'),
            ('xxyyzzw\n', 'w\n'),
        ],
    ),
    'palindrome-count': dict(
        python='''import sys

text = sys.stdin.read().strip()
n = len(text)
count = 0
# 2n-1 centres: even c is a single character, odd c is the gap between two.
for center in range(2 * n - 1):
    left = center // 2
    right = left + center % 2
    while left >= 0 and right < n and text[left] == text[right]:
        count += 1
        left -= 1
        right += 1
print(count)
''',
        hints=[
            'Every palindrome has a centre: either a single character (odd length) or the gap between two characters (even length).',
            'From each of the 2n-1 centres, expand outward while the two ends match. Every successful expansion is one more palindromic substring.',
            'Stop expanding at the first mismatch, because a larger window around the same centre cannot be a palindrome. Count equal text at different positions separately: aaaa has 10.',
        ],
        editorial=(
            'Expand around centres. There are 2n-1 centres: n single characters and n-1 gaps. For each, grow a window '
            'one step on each side while the end characters match, counting one palindrome per step. Each '
            'palindromic substring has exactly one centre and is reached by exactly one expansion, so nothing is '
            'counted twice or missed; the first mismatch ends that centre because any wider window contains it. '
            'Time is O(n^2) in the worst case (all-equal text) and space O(1). A DP table is[i][j] gives the same '
            'O(n^2) time with O(n^2) memory, and checking every substring is O(n^3). Edge cases: one character gives '
            '1, all-equal text gives n(n+1)/2, and spaces count as characters.'
        ),
        cases=[
            ('aaaa\n', '10\n'),
            ('ab\n', '2\n'),
        ],
    ),
    'subset-count': dict(
        python='''import sys

n = int(sys.stdin.read().strip())
# Each object is either in or out of a subset: two choices, n times.
print(2 ** n)
''',
        hints=[
            'Think about one object at a time: in any subset it is either included or left out.',
            'Those choices are independent, so the number of subsets doubles with every object you add: count(n) = 2 * count(n-1).',
            'The base case is count(0) = 1, because the empty set has exactly one subset, itself. The answer for n = 30 exceeds a 32-bit signed int only barely, so use a wide type in fixed-width languages.',
        ],
        editorial=(
            'Build a subset by deciding, for each of the n objects, whether to include it. Each decision has two '
            'outcomes and the decisions are independent, so there are 2 * 2 * ... * 2 = 2^n distinct subsets. The '
            'recursive view is count(n) = 2 * count(n-1) with count(0) = 1, since the empty collection has only '
            'the empty subset; every subset of n objects is a subset of the first n-1 with the last object added or '
            'not. A closed form or a bit shift computes it in O(1) time and space, while listing subsets would cost '
            'O(2^n). Edge cases: n = 0 prints 1, and n = 30 prints 1073741824, which needs a 64-bit type in Java.'
        ),
        cases=[
            ('30\n', '1073741824\n'),
            ('4\n', '16\n'),
        ],
    ),
    'heap-root': dict(
        python='''import sys
import heapq

values = list(map(int, sys.stdin.read().split()))
# heapq is a min heap, so store negated values to get max-heap behaviour.
heap = []
for x in values:
    heapq.heappush(heap, -x)
print(-heap[0])
''',
        hints=[
            'In a max heap every parent is at least as large as its children, so the root is the largest value present.',
            'Insert each reading with sift-up. The heap property guarantees that after all insertions the root holds the maximum.',
            'If your language only has a min heap, push negated values and negate the root when printing. With all-negative readings the root is the one closest to zero.',
        ],
        editorial=(
            'Push every reading into a max heap and print the root. The heap property says each parent is at least '
            'as large as its children, and by chaining that from any node up to the top, the root is at least as '
            'large as every element, so it is the maximum. Each insertion sifts the new value up in O(log n), for '
            'O(n log n) total; heapify can build the heap in O(n). Space is O(n). A single linear scan for the '
            'maximum gives the same answer in O(n) with O(1) space, which is a good check. Edge cases: duplicates of '
            'the maximum still print one value, all-negative input prints the largest (closest to zero) reading, '
            'and a single reading is the root.'
        ),
        cases=[
            ('-10000 -9999 -10000\n', '-9999\n'),
            ('10000 3 10000 -10000\n', '10000\n'),
        ],
    ),
    'incoming-links': dict(
        python='''import sys

numbers = list(map(int, sys.stdin.read().split()))
n, m = numbers[0], numbers[1]
indegree = [0] * n
for i in range(m):
    target = numbers[3 + 2 * i]  # edge i is (numbers[2+2i], numbers[3+2i])
    indegree[target] += 1
print(' '.join(map(str, indegree)))
''',
        hints=[
            'The indegree of a vertex is the number of edges that end at it; where the edge starts does not matter.',
            'Make an array of n zeros and add one to the entry of the target v for every edge u v. There is no need to build an adjacency list.',
            'Parallel edges each add one, and a self loop u u adds one to u. Vertices that no edge touches must still be printed as 0.',
        ],
        editorial=(
            'Keep a counter array of size n initialised to zero. For each of the m edges u v, increment the counter '
            'at v. After all edges, counter[v] equals the number of edges whose target is v, which is the definition '
            'of indegree, so print the array in vertex order. Each edge is processed once, so time is O(n + m) and '
            'space is O(n). Building an adjacency list and then counting would work too but is unnecessary. Edge '
            'cases: m = 0 prints n zeros, parallel edges count separately, a self loop counts toward its own vertex, '
            'and isolated vertices in a disconnected graph still appear as 0.'
        ),
        cases=[
            ('1 3 0 0 0 0 0 0\n', '3\n'),
            ('6 2 0 5 0 5\n', '0 0 0 0 0 2\n'),
        ],
    ),
}

"""Batch 4 problem upgrades: Python references, specific hints, editorials and adversarial cases."""

PROBLEMS = {
    'running-altitude': dict(
        python='''import sys

values = [int(x) for x in sys.stdin.read().split()]
running = 0
prefix = []
for x in values:
    running += x
    prefix.append(running)
print(" ".join(map(str, prefix)))
''',
        hints=[
            'Each output value depends only on the values up to and including the same position, so you can produce the answer while scanning left to right.',
            'Keep one running total. After adding the current value, that total is exactly the prefix sum for this position.',
            'Add first, then print, so the first output equals the first input. Negative values simply pull the total down; it can dip below zero and come back.',
        ],
        editorial=(
            'Scan the readings once while keeping a running total. When you reach position i, add a[i] to the total and '
            'output it. The invariant is that before processing position i the total equals a[0] + ... + a[i-1], so after '
            'adding a[i] it is precisely the prefix sum ending at i. A naive version recomputes each prefix from scratch '
            'in O(n^2); the running total makes it O(n) time and O(1) extra space beyond the output. Edge cases: a single '
            'value prints itself, all-negative input produces a strictly decreasing sequence, and zeros repeat the '
            'previous total. With at most 1000 values of magnitude 10000 the totals stay well within normal integer range.'
        ),
        cases=[
            ('-10000 -10000 -10000', '-10000 -20000 -30000'),
            ('5 -5 5 -5', '5 0 5 0'),
        ],
    ),
    'second-distinct': dict(
        python='''import sys

values = [int(x) for x in sys.stdin.read().split()]
distinct = sorted(set(values))
print("NONE" if len(distinct) < 2 else distinct[-2])
''',
        hints=[
            'The word distinct matters: if the maximum appears several times, its copies do not count as the second-largest.',
            'Remove duplicates first (a set does this), then the question becomes the second-largest element of the unique values.',
            'If only one unique value remains, print NONE. Otherwise sort the unique values, or track the top two in one pass, and print the runner-up.',
        ],
        editorial=(
            'Collapse the readings into a set of unique values. If fewer than two remain, print NONE; otherwise the answer '
            'is the second element from the top of the sorted unique values. This is correct because duplicates of the '
            'maximum must be skipped, and the set removes exactly those duplicates. Sorting costs O(n log n) time and O(n) '
            'space; a one-pass alternative keeps the largest and second-largest seen so far, updating the second only '
            'with values strictly smaller than the largest, for O(n) time and O(1) space. Edge cases: all equal values, '
            'a repeated maximum, and all-negative input where the answer is still the second-highest negative.'
        ),
        cases=[
            ('9 9 9 4 4', '4'),
            ('-10000 10000', '-10000'),
        ],
    ),
    'pair-energy': dict(
        python='''import sys

values = sorted(int(x) for x in sys.stdin.read().split())
if len(values) < 2:
    print(0)
else:
    # the best product uses either the two largest or the two most negative values
    print(max(values[0] * values[1], values[-1] * values[-2]))
''',
        hints=[
            'Two negative numbers multiply to a positive, so the two largest values are not always the best pair.',
            'Only four values can matter: the two largest and the two smallest. Sorting puts them at the ends.',
            'Compare the product of the two smallest with the product of the two largest and print the larger. With exactly one value print 0; with two values the answer can be negative.',
        ],
        editorial=(
            'Sort the readings. The maximum product of two different positions is either the product of the two largest '
            'values or the product of the two smallest values. Why: if the best pair contains a positive and a negative, '
            'the product is negative, and with only two values that is forced anyway; with three or more values, two '
            'same-sign extremes always do at least as well. Checking all pairs is O(n^2); sorting is O(n log n), and a '
            'single pass tracking the top two and bottom two is O(n) with O(1) space. Edge cases: a single value prints 0, '
            'two values of opposite sign give a negative answer, and two large negatives such as -10000 and -9999 beat '
            'the positives.'
        ),
        cases=[
            ('-10000 -9999 10000 1', '99990000'),
            ('-3 5', '-15'),
        ],
    ),
    'out-of-order': dict(
        python='''import sys


def sort_and_count(a):
    """Return (sorted copy of a, number of pairs i < j with a[i] > a[j])."""
    if len(a) <= 1:
        return a, 0
    mid = len(a) // 2
    left, left_count = sort_and_count(a[:mid])
    right, right_count = sort_and_count(a[mid:])
    merged = []
    count = left_count + right_count
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            # right[j] is smaller than every remaining left value
            count += len(left) - i
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, count


values = [int(x) for x in sys.stdin.read().split()]
print(sort_and_count(values)[1])
''',
        hints=[
            'Only strictly greater counts: equal values at positions i < j do not form an out-of-order pair.',
            'Merge sort can count these pairs. While merging two sorted halves, a value taken from the right half is smaller than every value still waiting in the left half.',
            'When the right value is strictly smaller, add the number of remaining left values to the count; on a tie take the left value first so equal pairs are never counted.',
        ],
        editorial=(
            'This is inversion counting. The direct approach checks every pair in O(n^2), which is fine for 1000 values '
            'but does not scale. Merge sort counts inversions in O(n log n): split the array, count inversions inside '
            'each half recursively, then count pairs that cross the halves while merging. Because both halves are sorted, '
            'whenever the right head is strictly smaller than the left head it is also smaller than all remaining left '
            'values, so all of them form inversions with it. Taking the left value on ties keeps equal pairs uncounted. '
            'Space is O(n) for the merge buffers. Edge cases: one value or sorted input gives 0, strictly decreasing '
            'input gives n(n-1)/2, and duplicates contribute nothing.'
        ),
        cases=[
            ('2 2 1 1', '4'),
            ('-10000 10000 -10000', '1'),
        ],
    ),
    'balance-position': dict(
        python='''import sys

values = [int(x) for x in sys.stdin.read().split()]
total = sum(values)
left = 0
answer = -1
for i, x in enumerate(values):
    if left == total - left - x:
        answer = i
        break
    left += x
print(answer)
''',
        hints=[
            'The element at the balance position belongs to neither side, and an empty side sums to 0.',
            'If you know the total and the sum strictly to the left, the right side is total minus left minus the current value.',
            'Scan left to right, test before adding the current value to the left sum, and stop at the first match. Negative values mean the sums are not monotonic, so you cannot binary search.',
        ],
        editorial=(
            'Compute the total once, then walk the array keeping left, the sum of elements strictly before index i. The '
            'right sum is total - left - a[i], so each index is checked in O(1). Print the first index where the two '
            'sides are equal, or -1 if none is. The invariant is that left is updated only after the check, so it never '
            'includes the current element. Recomputing both sides at every index would be O(n^2); this is O(n) time and '
            'O(1) space. Edge cases: a single value balances at index 0 because both sides are empty, several balanced '
            'indices must report the first, and negative values can make a later index balance after earlier ones fail.'
        ),
        cases=[
            ('1 -1 5', '2'),
            ('3 0 0 3', '1'),
        ],
    ),
    'trapped-rain': dict(
        python='''import sys

heights = [max(0, int(x)) for x in sys.stdin.read().split()]
left, right = 0, len(heights) - 1
left_max = right_max = 0
water = 0
while left <= right:
    # the lower side's best wall decides how much water sits above it
    if left_max <= right_max:
        left_max = max(left_max, heights[left])
        water += left_max - heights[left]
        left += 1
    else:
        right_max = max(right_max, heights[right])
        water += right_max - heights[right]
        right -= 1
print(water)
''',
        hints=[
            'Clamp negative heights to 0 first. Water above one column is limited by the tallest wall to its left and the tallest wall to its right.',
            'The water at column i is min(highest on the left including i, highest on the right including i) minus the height of i.',
            'Use two pointers: move inward from the side whose running maximum is smaller, because that maximum is the binding limit there. Edge columns and monotonic slopes hold no water.',
        ],
        editorial=(
            'After replacing negative heights with 0, the water above column i equals min(maxLeft(i), maxRight(i)) - h[i], '
            'where both maxima include i itself. Computing these by scanning for each column is O(n^2). Two pointers '
            'achieve O(n) time and O(1) space: keep the best wall seen from each end and always advance the side with the '
            'smaller best wall. The water on that side is fully determined, because the opposite side is already known to '
            'contain a wall at least as high. Prefix and suffix maximum arrays are an equally valid O(n) alternative. '
            'Edge cases: one column, strictly increasing or decreasing heights, a deep negative valley that becomes a '
            'zero-height pit, and a lower right wall that caps the level.'
        ),
        cases=[
            ('3 -10000 3', '3'),
            ('4 0 0 0 1', '3'),
        ],
    ),
    'longest-run': dict(
        python='''import sys

values = [int(x) for x in sys.stdin.read().split()]
best = run = 1
for i in range(1, len(values)):
    run = run + 1 if values[i] == values[i - 1] else 1
    best = max(best, run)
print(best)
''',
        hints=[
            'A run must be contiguous: equal values separated by something else start new runs.',
            'Track the length of the run that ends at the current position, compared only with the previous value.',
            'Reset the run to 1 when the value changes, update the best after every step so a run ending at the last position is counted, and start both at 1 for a single value.',
        ],
        editorial=(
            'Walk the readings once while tracking run, the length of the equal run ending at the current index, and best, '
            'the longest run seen so far. If a[i] equals a[i-1] the run grows by one; otherwise it restarts at 1. Updating '
            'best on every step guarantees that a run ending at the final element is not lost. The invariant is that run '
            'always describes the maximal equal block ending at i, so the maximum over all i is the answer. Time is O(n) '
            'and space O(1). Counting value frequencies instead would be wrong because equal values separated by others '
            'do not form one run. Edge cases: one value gives 1, all equal gives n, and the longest run at the end.'
        ),
        cases=[
            ('5 5 1 5 5', '2'),
            ('-7 -7 3 -7 -7 -7', '3'),
        ],
    ),
    'vowel-count': dict(
        python='''import sys

text = sys.stdin.read().strip().lower()
print(sum(1 for ch in text if ch in "aeiou"))
''',
        hints=[
            'Uppercase and lowercase vowels both count, and only a, e, i, o and u are vowels here; y is not.',
            'Lowercase the whole line once, then each character needs a single membership test against the five vowels.',
            'Count characters, not words, so digits, punctuation and spaces simply fail the test. Strip outer whitespace as the statement says it is not significant.',
        ],
        editorial=(
            'Lowercase the stripped line and count characters that belong to the set a, e, i, o, u. Lowercasing first means '
            'one membership test covers both cases, and every non-letter character (digits, spaces, punctuation) simply '
            'fails the test, so no special handling is needed. Each character is examined exactly once, giving O(n) time '
            'and O(1) extra space for a fixed five-letter vowel set. A slightly slower baseline compares each character '
            'against all ten upper and lower case vowels, which is still linear. Edge cases: text in all capitals, words '
            'with only y as a vowel sound such as rhythm, and lines made entirely of symbols.'
        ),
        cases=[
            ('AEIOU aeiou', '10'),
            ('rhythm by', '0'),
        ],
    ),
    'parenthesis-depth': dict(
        python='''import sys

text = sys.stdin.read().strip()
depth = best = 0
balanced = True
for ch in text:
    if ch == "(":
        depth += 1
        best = max(best, depth)
    elif ch == ")":
        depth -= 1
        if depth < 0:
            balanced = False  # a closer with no matching opener
            break
print(best if balanced and depth == 0 else -1)
''',
        hints=[
            'Only ( and ) matter; every other character is skipped. A string with no parentheses is balanced with depth 0.',
            'You do not need an explicit stack: one counter for the current depth is enough, plus the maximum it ever reached.',
            'Unbalanced has two forms: the depth drops below zero at some point (like a closer before its opener), or it ends above zero. Check both; a final count of zero alone is not enough.',
        ],
        editorial=(
            'Scan the characters with a counter for the current open depth. Each ( increments it and updates the best '
            'depth; each ) decrements it. If the counter ever goes negative, a closer has no matching opener, so the '
            'string is unbalanced and the answer is -1 immediately. After the scan, a non-zero counter means unmatched '
            'openers, which is also -1; otherwise print the best depth. A counter is enough because there is only one '
            'bracket type, so a stack would just store identical symbols. Time is O(n), space O(1). Edge cases: text with '
            'no parentheses prints 0, and a string like )( has a final count of zero but is still unbalanced.'
        ),
        cases=[
            (')(', '-1'),
            ('((a)', '-1'),
        ],
    ),
    'small-coins': dict(
        python='''import sys

n = int(sys.stdin.read().strip())
coins = (1, 3, 4)
fewest = [0] * (n + 1)
for amount in range(1, n + 1):
    fewest[amount] = min(fewest[amount - c] + 1 for c in coins if c <= amount)
print(fewest[n])
''',
        hints=[
            'Greedy fails here: taking the largest coin first turns 6 into 4 + 1 + 1, but 3 + 3 uses only two coins.',
            'Let fewest[a] be the minimum coins for amount a. The last coin used is 1, 3 or 4, so fewest[a] builds on a smaller amount.',
            'Fill fewest from 0 upward with fewest[0] = 0 and fewest[a] = 1 + the minimum of fewest[a - c] over coins c that fit. Since 1 is a coin every amount is reachable, and n = 0 needs zero coins.',
        ],
        editorial=(
            'Use bottom-up dynamic programming. fewest[0] is 0, and for each amount a from 1 to n, fewest[a] is one more '
            'than the smallest fewest[a - c] over coins c in {1, 3, 4} with c no larger than a. This is correct because '
            'an optimal purse for a ends with some coin c, and removing it leaves an optimal purse for a - c. The greedy '
            'rule of always taking the largest coin is a tempting baseline but is wrong for this coin set, for example 6 '
            'and 7. Time is O(n times the number of coins) and space O(n). Edge cases: n = 0 prints 0, and the coin 1 '
            'guarantees every amount has an answer.'
        ),
        cases=[
            ('6', '2'),
            ('30', '8'),
        ],
    ),
    'triangular-total': dict(
        python='''import sys

n = int(sys.stdin.read().strip())
print(n * (n + 1) // 2)
''',
        hints=[
            'You can add 1 + 2 + ... + n in a loop, but there is a closed formula that answers in constant time.',
            'Pair the first and last terms: 1 + n, 2 + (n - 1), and so on. Every pair sums to n + 1.',
            'There are n / 2 such pairs, giving n(n + 1) / 2. One of n and n + 1 is even, so integer division is exact, and n = 0 correctly gives 0.',
        ],
        editorial=(
            'The sum 1 + 2 + ... + n equals n(n + 1) / 2. Writing the sum forwards and backwards and adding term by term '
            'gives n copies of n + 1, which is twice the sum. Because n and n + 1 are consecutive, one of them is even, so '
            'the division is always exact and integer arithmetic is safe. A loop that adds each number is a correct O(n) '
            'baseline; the formula is O(1) time and space. Edge cases: n = 0 must print 0 (an empty sum), n = 1 prints 1, '
            'and the largest allowed n = 30 prints 465, far from any overflow concern.'
        ),
        cases=[
            ('30', '465'),
            ('4', '10'),
        ],
    ),
    'minimum-gap': dict(
        python='''import sys

values = sorted(int(x) for x in sys.stdin.read().split())
if len(values) < 2:
    print(0)
else:
    print(min(b - a for a, b in zip(values, values[1:])))
''',
        hints=[
            'Positions must be different, but their values may be equal, so duplicates give a gap of 0.',
            'After sorting, the closest pair of values is always adjacent in the sorted order.',
            'Sort, take the minimum difference between neighbours, and print 0 when there is only one value. The closest pair is often not adjacent in the original input.',
        ],
        editorial=(
            'Sort the readings and take the smallest difference between consecutive sorted values. This is correct because '
            'for any sorted a <= b <= c, the gap c - a is at least both b - a and c - b, so a non-adjacent pair can never '
            'beat the adjacent pairs inside it. Comparing every pair is O(n^2); sorting brings it to O(n log n) time with '
            'O(n) space for the sorted copy. Edge cases: one value prints 0 by definition, duplicates at any positions '
            'give 0, the extreme pair -10000 and 10000 gives 20000, and the closest values may be far apart in the input.'
        ),
        cases=[
            ('-10000 10000', '20000'),
            ('10 -3 7 1', '3'),
        ],
    ),
    'outgoing-links': dict(
        python='''import sys

numbers = [int(x) for x in sys.stdin.read().split()]
n = numbers[0]
outdegree = [0] * n
# edges start at index 2 and come in (u, v) pairs; only the source u matters
for u in numbers[2::2]:
    outdegree[u] += 1
print(" ".join(map(str, outdegree)))
''',
        hints=[
            'Outdegree counts edges leaving a vertex, so for each edge u v only u matters.',
            'One counter per vertex is enough: no adjacency list is needed to answer this question.',
            'Read n, skip m, then step through the edge pairs adding one to the source counter. Self loops count once for their vertex, parallel edges count every time, and isolated vertices print 0.',
        ],
        editorial=(
            'Create an array of n zeros. For each directed edge u v, increment the counter for u. Then print the counters '
            'in vertex order. This is correct because the outdegree of a vertex is by definition the number of edges whose '
            'source is that vertex, and every edge is visited once. Building a full adjacency list first and taking list '
            'sizes also works but uses more memory than needed. Time is O(n + m) and space O(n). Edge cases: m = 0 prints '
            'all zeros, a self loop u u counts once toward u, parallel edges are each counted, and vertices with no '
            'outgoing edges still appear in the output.'
        ),
        cases=[
            ('4 3 1 1 1 1 1 0', '0 3 0 0'),
            ('1 2 0 0 0 0', '2'),
        ],
    ),
}

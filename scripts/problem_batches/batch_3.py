PROBLEMS = {
    'ordered-parcels': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
values.sort()
print(' '.join(str(v) for v in values))
''',
        hints=[
            'There is no length prefix: every whitespace-separated token on the line is a value, and duplicates and negatives must all be kept.',
            'Nondecreasing order means equal values simply sit next to each other; you only need a comparison sort on whole integers, not on their text.',
            'Parse every token as an integer (so -10 sorts before -9 and 10 after 9), sort once, then print the values joined by single spaces.',
        ],
        editorial=(
            'Read every token, convert it to an integer and sort the list with the language\'s built-in sort, then print it '
            'separated by single spaces. The built-in sort is a comparison sort, so after it finishes every adjacent pair '
            'satisfies a[i] <= a[i+1], which is exactly the nondecreasing order requested. It runs in O(n log n) time and '
            'O(n) space. A hand-written insertion sort (O(n^2)) would also pass for n <= 1000, and because values lie in '
            '[-10000, 10000] a counting sort over 20001 buckets would run in linear time. Edge cases: a single value, many '
            'duplicates, and negative numbers, which must be compared numerically rather than as strings.'
        ),
        cases=[
            ('10000 -10000 0 -10000 10000\n', '-10000 -10000 0 10000 10000\n'),
            ('3 -1 3 -1 3\n', '-1 -1 3 3 3\n'),
        ],
    ),
    'first-peak': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
best = 0
for i in range(1, len(values)):
    if values[i] > values[best]:  # strict: a later tie never replaces the first maximum
        best = i
print(best)
''',
        hints=[
            'The answer is a position, not a value, and when the maximum appears several times only its first occurrence counts.',
            'Keep the index of the best value seen so far, starting at index 0, rather than starting from a guessed value such as 0 that breaks on all-negative input.',
            'Scan left to right and move the best index only when the new value is strictly greater; using greater-or-equal would return the last maximum instead.',
        ],
        editorial=(
            'Walk the array once, remembering the index of the largest value seen so far. Start with index 0 and replace it '
            'only when a later value is strictly larger. Invariant: after looking at positions 0..i, best is the smallest index '
            'holding the maximum of that prefix, because ties never move it. When the scan ends the prefix is the whole array. '
            'Time is O(n) and extra space is O(1). Sorting would lose the original positions, and calling max then index is '
            'also correct but makes two passes. Edge cases: a single value (answer 0), all values equal (answer 0), and '
            'all-negative input, which is why the scan seeds from the first element instead of from 0.'
        ),
        cases=[
            ('-7 -3 -3 -9\n', '1\n'),
            ('10000 -10000 10000\n', '0\n'),
        ],
    ),
    'adjacent-rise': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
best = 0  # no rise at all prints 0
for i in range(1, len(values)):
    best = max(best, values[i] - values[i - 1])
print(best)
''',
        hints=[
            'Only neighbouring readings matter: compare each value with the one immediately before it, never with values further back.',
            'Each pair gives a difference a[i] - a[i-1]; the answer is the largest of these, but falls and flat steps must not make the answer negative.',
            'Start the running best at 0, then take the maximum with every adjacent difference; a single reading or a never-rising sequence then naturally prints 0.',
        ],
        editorial=(
            'For every i from 1 to n-1 compute the step a[i] - a[i-1] and keep the largest one, starting from 0. Starting at 0 '
            'encodes the rule that a sequence with no positive increase prints 0: negative and zero steps can never beat it. '
            'Invariant: after processing step i, best is max(0, largest step among the first i steps). One pass gives O(n) '
            'time and O(1) space. Do not confuse this with the best buy-then-sell gap, which compares a value with the minimum '
            'of everything before it; here only consecutive readings count. Edge cases: one value (no steps, answer 0), a '
            'plateau of equal values, and the extreme jump from -10000 to 10000, which is 20000.'
        ),
        cases=[
            ('-10000 10000\n', '20000\n'),
            ('5 5 5 4\n', '0\n'),
        ],
    ),
    'rising-subsequence': dict(
        python='''import sys
from bisect import bisect_left

values = [int(token) for token in sys.stdin.read().split()]
# tails[k] = smallest possible last value of a strictly increasing subsequence of length k + 1
tails = []
for x in values:
    pos = bisect_left(tails, x)  # bisect_left so an equal value replaces, never extends
    if pos == len(tails):
        tails.append(x)
    else:
        tails[pos] = x
print(len(tails))
''',
        hints=[
            'A subsequence may skip elements but must keep their order, and strictly increasing means equal values can never follow each other.',
            'The quadratic idea: let best[i] be the longest strictly increasing subsequence that ends at position i, built from any earlier j with a smaller value.',
            'Faster: keep, for each length, the smallest possible tail value. For each new x, binary-search the first tail that is >= x and replace it, or append if none; searching for >= is what stops duplicates from extending a chain.',
        ],
        editorial=(
            'Maintain a list tails where tails[k] is the smallest value that can end a strictly increasing subsequence of length '
            'k+1. The list is always strictly increasing. For each value x, find the first tail >= x with binary search: if '
            'there is none, x extends the longest chain, otherwise x replaces that tail, because a smaller ending can only help '
            'later values. The answer is the length of tails. This takes O(n log n) time and O(n) space. The classic DP, where '
            'd[i] = 1 + max d[j] over j < i with a[j] < a[i], is O(n^2) and fine for n <= 1000. Edge cases: duplicates must not '
            'count twice (use >= in the search, not >), a decreasing input gives 1, and a single value gives 1.'
        ),
        cases=[
            ('1 2 2 3 3 4\n', '4\n'),
            ('0 8 4 12 2 10 6 14 1 9 5 13 3 11 7 15\n', '6\n'),
        ],
    ),
    'majority-reading': dict(
        python='''import sys
from collections import Counter

values = [int(token) for token in sys.stdin.read().split()]
counts = Counter(values)
answer = 'NONE'
for value, count in counts.items():
    if count > len(values) // 2:  # strictly more than half; exactly half is not a majority
        answer = value
print(answer)
''',
        hints=[
            'More than half is strict: in a list of 4 values a value seen exactly 2 times is not a majority, so the answer can be NONE.',
            'Count how many times each value occurs with a hash map; at most one value can exceed half the length.',
            'After counting, test count > n // 2 (integer division) for each value and print it, otherwise print NONE; a single value is always its own majority.',
        ],
        editorial=(
            'Count occurrences of every value in a hash map, then look for a value whose count is greater than n // 2. Two '
            'different values cannot both appear more than n/2 times, so if one passes the test it is the unique answer, and '
            'if none does the output is NONE. Counting takes O(n) expected time and O(k) space for k distinct values. The '
            'Boyer-Moore voting algorithm finds the only possible candidate in O(1) extra space, but it still needs a second '
            'pass to verify the candidate really exceeds half. Edge cases: n = 1 (the value is the majority), an even-length '
            'list split exactly in half (NONE), and negative values, which are ordinary keys.'
        ),
        cases=[
            ('7 7 3 3\n', 'NONE\n'),
            ('-2 5 -2 5 -2\n', '-2\n'),
        ],
    ),
    'record-span': dict(
        python='''import sys

values = [int(token) for token in sys.stdin.read().split()]
stack = []  # indices whose values are strictly decreasing from bottom to top
spans = []
for i, x in enumerate(values):
    while stack and values[stack[-1]] <= x:  # <= so equal values join the span
        stack.pop()
    previous_greater = stack[-1] if stack else -1
    spans.append(i - previous_greater)
    stack.append(i)
print(' '.join(str(s) for s in spans))
''',
        hints=[
            'The span at position i stops at the nearest earlier value that is strictly greater than a[i]; equal values are included in the span.',
            'Keep a stack of indices whose values are strictly decreasing; anything smaller or equal to the current value can never block a later span, so it can be thrown away.',
            'For each i, pop while the top value is <= a[i]; the span is i minus the remaining top index, or i + 1 if the stack is empty. Then push i.',
        ],
        editorial=(
            'This is the stock-span problem solved with a monotonic stack. For each index i, the span is i - p where p is the '
            'closest earlier index with a value strictly greater than a[i] (or -1 if there is none). Keep a stack of indices '
            'with strictly decreasing values. Before pushing i, pop every index whose value is <= a[i]: those values are '
            'covered by a[i] and can never be the blocker for anything later. Whatever is left on top is p. Each index is '
            'pushed and popped at most once, so the total time is O(n) with O(n) space, versus O(n^2) for scanning backwards '
            'from every position. Edge cases: equal values (they extend the span), a strictly decreasing input (all 1s), and a '
            'final maximum whose span is the whole array.'
        ),
        cases=[
            ('5 5 5 6 1\n', '1 2 3 4 1\n'),
            ('-1 -3 -2 -1 0\n', '1 1 2 4 5\n'),
        ],
    ),
    'frequency-peak': dict(
        python='''import sys
from collections import Counter

values = [int(token) for token in sys.stdin.read().split()]
counts = Counter(values)
# highest count first, then the smallest value among equal counts
answer = min(counts, key=lambda v: (-counts[v], v))
print(answer)
''',
        hints=[
            'Two rules decide the answer: the highest count wins, and among values with the same count the numerically smallest wins, which may be negative.',
            'Count every value with a hash map, then choose a winner by comparing (count, value) pairs instead of count alone.',
            'Either visit values in increasing order and replace the answer only on a strictly larger count, or pick the minimum by the key (negative count, value); both handle ties correctly.',
        ],
        editorial=(
            'First count how often each value occurs using a hash map. Then choose the value that maximises its count, breaking '
            'ties toward the smaller value. A clean way is to take the minimum over all distinct values of the pair (-count, '
            'value): a larger count gives a smaller first component, and equal counts fall back to comparing the values. The '
            'reference does the same by walking values in sorted order and updating only on a strictly greater count, so the '
            'first, smallest value with the top count is kept. Counting is O(n); choosing is O(k), or O(k log k) if you sort '
            'the k distinct keys. Edge cases: every value distinct (answer is the minimum), ties involving negative numbers, '
            'and a single value.'
        ),
        cases=[
            ('9 -4 9 -4 2\n', '-4\n'),
            ('10000 10000 -10000\n', '10000\n'),
        ],
    ),
    'reverse-message': dict(
        python='''import sys

text = sys.stdin.read().strip()  # outer whitespace is not significant
print(text[::-1])
''',
        hints=[
            'Reverse the characters of the whole line, not the order of the words: spaces and punctuation move like any other character.',
            'Leading and trailing whitespace is not significant, so strip it first; spaces inside the line stay and are reversed too.',
            'Walk from the last character to the first (or push every character on a stack and pop them all) and print the result; a palindrome comes back unchanged.',
        ],
        editorial=(
            'Strip the outer whitespace, then output the characters from last to first. A stack shows why this works: pushing '
            'characters in order and popping them returns them in reverse, because the last one in is the first one out. In '
            'Python a slice with step -1 does the same walk in one expression. Every character is touched once, so the time '
            'is O(n) and the reversed copy uses O(n) space; an in-place two-pointer swap on a character array uses O(1) extra '
            'space. Edge cases: a single character, a palindrome (unchanged), runs of internal spaces, which must be kept '
            'exactly, and surrounding spaces, which are removed before reversing.'
        ),
        cases=[
            ('  padded  text  \n', 'txet  deddap\n'),
            ('Ab!? 9\n', '9 ?!bA\n'),
        ],
    ),
    'remove-adjacent': dict(
        python='''import sys

text = sys.stdin.read().strip()
out = []
for ch in text:
    if not out or out[-1] != ch:  # keep a character only when it starts a new run
        out.append(ch)
print(''.join(out))
''',
        hints=[
            'Only consecutive repeats are merged: the same letter appearing again later after a different character is kept.',
            'You only ever need to compare the current character with the last character you kept, which is the top of a stack or the end of the output.',
            'Append a character when the output is empty or its last character differs; spaces and punctuation form runs too, and uppercase and lowercase letters are different characters.',
        ],
        editorial=(
            'Scan the stripped line once and build the output: append the current character if the output is empty or its '
            'last character is different, otherwise skip it. Invariant: the output never contains two equal neighbours, and '
            'every maximal run seen so far contributes exactly its first character, so after the scan each run is compressed '
            'to one character. The scan is O(n) time and the output uses O(n) space. Comparing with the previous input '
            'character instead of the last output character gives the same result here, since both equal the previous '
            'character. Edge cases: a line of one repeated character (one character out), runs of spaces (collapsed to one '
            'space), and case sensitivity, so a and A are not merged.'
        ),
        cases=[
            ('zzzzzz\n', 'z\n'),
            ('aA  Aa!!\n', 'aA Aa!\n'),
        ],
    ),
    'digit-total': dict(
        python='''import sys

text = sys.stdin.read().strip()
total = 0
for ch in text:
    if '0' <= ch <= '9':  # each digit counts on its own, so 42 adds 4 + 2
        total += ord(ch) - ord('0')
print(total)
''',
        hints=[
            'You add individual digit characters, not numbers: the text 42 contributes 4 + 2 = 6, not 42.',
            'Everything that is not one of the characters 0 to 9 is ignored, including minus signs, decimal points and letters.',
            'Scan each character, and when it lies between 0 and 9 add its value (character code minus the code of 0) to a running total; text with no digits prints 0.',
        ],
        editorial=(
            'Walk the characters once and keep a running total. For each character between 0 and 9 add its numeric value, '
            'which is its character code minus the code of 0; skip everything else. Invariant: after reading a prefix, total '
            'equals the sum of the digits in that prefix. This is O(n) time and O(1) space. The usual mistake is to parse '
            'whole numbers with a regular expression and add them, which turns 42 into 42 instead of 6, or to treat a minus '
            'sign as making the following digit negative; the statement only asks for decimal digits. Edge cases: no digits at '
            'all (print 0), a long run of 9s, and digits glued to signs or letters.'
        ),
        cases=[
            ('9999999999\n', '90\n'),
            ('-12.5e3 x0\n', '11\n'),
        ],
    ),
    'binary-ones': dict(
        python='''import sys

n = int(sys.stdin.read().strip())
count = 0
while n:
    n &= n - 1  # clears the lowest set bit
    count += 1
print(count)
''',
        hints=[
            'Count the 1s in the binary form of n, for example 10 is 1010 in binary and has two of them; 0 has none.',
            'You can test the lowest bit with n & 1 and shift right, but there is a neater trick that jumps straight from one set bit to the next.',
            'n & (n - 1) clears exactly the lowest set bit, so repeat it until n becomes 0 and count the steps; the loop runs once per 1 bit and not at all for 0.',
        ],
        editorial=(
            'Use Kernighan\'s trick. Subtracting 1 from n flips its lowest set bit to 0 and every zero below it to 1, so n & '
            '(n - 1) is n with that lowest set bit removed and everything else unchanged. Repeating until n is 0 removes one '
            'set bit per step, so the number of steps is the answer. The loop runs once per set bit, at most 5 times for n <= '
            '30, with O(1) space. The simpler baseline checks n & 1 and shifts right, which costs one step per bit position '
            'instead of per set bit. Edge cases: n = 0 (the loop never runs, print 0), powers of two (exactly 1), and 30, '
            'which is 11110 in binary with four set bits.'
        ),
        cases=[
            ('30\n', '4\n'),
            ('16\n', '1\n'),
        ],
    ),
    'consecutive-chain': dict(
        python='''import sys

values = set(int(token) for token in sys.stdin.read().split())
best = 0
for x in values:
    if x - 1 not in values:  # x starts a run, so count it once from here
        length = 1
        while x + length in values:
            length += 1
        best = max(best, length)
print(best)
''',
        hints=[
            'Order in the input does not matter and duplicates add nothing, so think of the values as a set and look for the longest block x, x+1, x+2, ...',
            'A run is easiest to measure from its smallest member: x starts a run exactly when x - 1 is not in the set.',
            'For every x whose predecessor is missing, count upward while x + length is present and keep the maximum; starting only at run starts keeps the whole scan linear.',
        ],
        editorial=(
            'Put all values in a hash set, which removes duplicates and gives O(1) membership checks. A value x is the start '
            'of a run exactly when x - 1 is not in the set. From each start, walk upward through x + 1, x + 2, ... while the '
            'values exist and record the length. Every value is visited by at most one upward walk, the one from its own run '
            'start, so the total work is O(n) expected time with O(n) space. Sorting and counting consecutive distinct '
            'neighbours is a simpler O(n log n) alternative. Edge cases: duplicates such as 1 1 2 2 still give 2, a single '
            'value gives 1, and runs that cross zero into negative numbers work the same way.'
        ),
        cases=[
            ('-10000 10000 -9999\n', '2\n'),
            ('3 3 2 2 1 1 5 -1 0\n', '5\n'),
        ],
    ),
    'dependency-order': dict(
        python='''import sys
import heapq

numbers = [int(token) for token in sys.stdin.read().split()]
n = numbers[0]
graph = [[] for _ in range(n)]
indegree = [0] * n
for i in range(2, len(numbers), 2):
    u, v = numbers[i], numbers[i + 1]
    graph[u].append(v)  # parallel edges are kept, so they are also removed one at a time
    indegree[v] += 1

ready = [v for v in range(n) if indegree[v] == 0]
heapq.heapify(ready)
order = []
while ready:
    u = heapq.heappop(ready)  # always take the smallest available vertex
    order.append(u)
    for v in graph[u]:
        indegree[v] -= 1
        if indegree[v] == 0:
            heapq.heappush(ready, v)

if len(order) != n:
    print('CYCLE')
else:
    print(' '.join(str(v) for v in order))
''',
        hints=[
            'A vertex may be printed only after everything that must come before it; if some vertices can never become free, there is a cycle and the answer is CYCLE.',
            'Track each vertex\'s in-degree, the number of unprinted prerequisites. Vertices with in-degree 0 are ready, and to be lexicographically smallest you must always print the smallest ready vertex.',
            'Run Kahn\'s algorithm with a min-heap: pop the smallest ready vertex, decrement its successors (once per parallel edge) and push any that reach 0. A self loop never reaches 0, so fewer than n printed vertices means CYCLE.',
        ],
        editorial=(
            'Use Kahn\'s algorithm with a min-priority queue. Count in-degrees, put every vertex with in-degree 0 in a min-heap, '
            'then repeatedly remove the smallest, append it to the order and decrement the in-degree of each successor, pushing '
            'those that reach 0. Greedy choice is safe: the smallest ready vertex can go first in some valid order, and putting '
            'any larger vertex first would make the sequence lexicographically bigger. If the order ends with fewer than n '
            'vertices, the rest lie on or behind a cycle, so print CYCLE. Time is O((n + m) log n) and space O(n + m). Edge '
            'cases: isolated vertices, parallel edges (each adds to the in-degree), and self loops, which always mean CYCLE.'
        ),
        cases=[
            ('4 1 3 0\n', '1 2 3 0\n'),
            ('2 1 1 1\n', 'CYCLE\n'),
        ],
    ),
}

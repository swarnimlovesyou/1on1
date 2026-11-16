"""Original curriculum authoring. No external question statements or solutions are imported."""
from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parents[1]
CONCEPTS = []


def concept(slug, title, prerequisites, lessons, objectives, model, example, invariant,
            mistake, complexity, implementation, cases, checkpoint, visual):
    code = textwrap.dedent(implementation).strip()
    CONCEPTS.append(dict(
        id='concept-' + slug, title=title, order=len(CONCEPTS)+1,
        prerequisites=['concept-' + x for x in prerequisites],
        lessonIds=['lesson-' + x for x in lessons], objectives=objectives,
        mentalModel=model, workedExample=example, invariant=invariant,
        commonMistake=mistake, complexity=complexity,
        java=dict(language='java', className='CurriculumExample',
                  implementation=code,
                  source='import java.util.*;\nclass CurriculumExample {\n' + code + '\n}',
                  cases=[dict(expression=e, expected=v) for e,v in cases]),
        checkpoint=dict(question=checkpoint[0], options=checkpoint[1], answer=checkpoint[2],
                        explanation=checkpoint[3]),
        visualization=dict(exampleInput=visual[0], expectedStates=visual[1],
                           manipulation=visual[2], limits=visual[3]),
        applications=[], contentStatus='authored', practiceStatus='planned-phase-2'))


concept('complexity', 'Time and Space Complexity', [], ['complexity'],
    ['Count repeated operations rather than guessing from syntax.', 'Separate input storage, auxiliary space and output size.'],
    'Treat a loop as a counter of work. Doubling the input doubles a full scan, roughly quadruples a square nested loop, and adds about one iteration to repeated halving.',
    'For n=8, a scan performs 8 visits, a square nested loop performs 64 visits, and repeated integer halving visits 8,4,2,1: 4 iterations. These counts describe the defined operations, not elapsed milliseconds.',
    'The operation counter increases once for each visit of the selected loop body.',
    'Two nested loops are not automatically quadratic: their bounds and dependencies determine the count. Big-O is a growth bound, not an exact runtime.',
    dict(time='O(n), O(n²), O(log n) for the three loops', space='O(1) auxiliary', assumptions='n >= 0; counting loop-body visits, excluding printing.'),
    '''static long[] counts(int n) {
        if (n < 0) throw new IllegalArgumentException("n must be nonnegative");
        long scan = 0, square = 0, halves = 0;
        for (int i = 0; i < n; i++) scan++;
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) square++;
        for (int x = n; x > 0; x /= 2) halves++;
        return new long[]{scan, square, halves};
    }''',
    [('Arrays.toString(counts(8))','[8, 64, 4]'), ('Arrays.toString(counts(0))','[0, 0, 0]'), ('Arrays.toString(counts(1))','[1, 1, 1]')],
    ('A square nested loop visits every pair for n=4. How many visits?', ['8','16','4'],1,'There are 4 choices for each of two indices: 4 × 4 = 16.'),
    ('n=8', ['scan: 8', 'square: 64', 'halving: 8 → 4 → 2 → 1'], 'Change n to 4 or 16 and predict the counters before comparing.', 'Nonnegative n; teaching counter only, not a runtime profiler.'))

concept('arrays', 'Arrays', ['complexity'], ['arrays'],
    ['Read and update by index.', 'Traverse an array while maintaining a running result.'],
    'An array is a numbered row of slots. Index i selects a position, not a value; duplicate values still occupy different slots.',
    'For [2,1,5], visit indices 0,1,2. The running total becomes 2,3,8. An empty row has total 0.',
    'Before index i, total equals the sum of a[0..i).',
    'The last valid index is length-1. Iterating with i <= length reads beyond the array. Integer sums may overflow; use long for the accumulator.',
    dict(time='O(n)', space='O(1) auxiliary', assumptions='Non-null int array; sum accumulated in long.'),
    '''static long sum(int[] a) {
        long total = 0;
        for (int i = 0; i < a.length; i++) total += a[i];
        return total;
    }''', [('sum(new int[]{2,1,5})','8'), ('sum(new int[]{})','0'), ('sum(new int[]{-2,-2})','-4')],
    ('After visiting indices 0 and 1 of [2,1,5], what is total?', ['2','3','8'],1,'Only the first two slots have been consumed: 2 + 1 = 3.'),
    ('[2,1,5]', ['i=0,total=2','i=1,total=3','i=2,total=8'], 'Edit a slot or repeat a value; predict which intermediate sums change.', 'Empty to 32 integers; values have stable slot identities.'))

concept('strings', 'Strings', ['arrays'], ['strings'],
    ['Traverse characters and distinguish positions from substrings.', 'Build a result without repeatedly copying an immutable string.'],
    'A string is an indexed sequence of text units. Reading does not mutate it; build changed text in a separate buffer.',
    'Read "cat" from indices 2,1,0 and append t,a,c to produce "tac". The original string remains "cat".',
    'After k iterations, the buffer contains the final k characters in reverse order.',
    'Java char indexes UTF-16 code units, not all user-perceived characters. This introductory example is restricted to ASCII; it is not a Unicode grapheme reverser.',
    dict(time='O(n)', space='O(n) output', assumptions='ASCII teaching input; StringBuilder avoids repeated string concatenation.'),
    '''static String reverse(String s) {
        StringBuilder out = new StringBuilder();
        for (int i = s.length() - 1; i >= 0; i--) out.append(s.charAt(i));
        return out.toString();
    }''', [('reverse("cat")','tac'), ('reverse("")',''), ('reverse("aab")','baa')],
    ('After reading index 2 of "cat", what is in the output buffer?', ['c','t','cat'],1,'The final character is t; append it first.'),
    ('"cat"', ['read 2: t','read 1: ta','read 0: tac'], 'Change the string and track source index separately from output length.', 'ASCII, 0–32 characters; Unicode expansion is separate.'))

concept('hashing', 'Hash Maps and Sets', ['arrays','strings'], ['hashing'],
    ['Use a set for exact membership and a map for key-associated state.', 'Check previously seen values before inserting the current one.'],
    'A set answers whether a value has appeared. A map additionally remembers a value such as the earlier index. Hashing locates a candidate bucket; equality still decides exact membership.',
    'For [2,1,2], insert 2, then 1. The last 2 is already present, so a duplicate exists. Two equal values at different positions count as repetition.',
    'Before reading position i, seen contains exactly the values at earlier positions.',
    'Hash lookup is expected constant time under normal assumptions, not a universal worst-case guarantee. A Bloom filter is not a replacement for an exact set.',
    dict(time='Expected O(n)', space='O(n) auxiliary', assumptions='Java HashSet exact integer membership; expected hashing behaviour.'),
    '''static boolean duplicate(int[] a) {
        Set<Integer> seen = new HashSet<>();
        for (int value : a) if (!seen.add(value)) return true;
        return false;
    }''', [('duplicate(new int[]{2,1,2})','true'), ('duplicate(new int[]{})','false'), ('duplicate(new int[]{-1,0,1})','false')],
    ('Before processing the final 2 in [2,1,2], which values are in seen?', ['{2}','{1,2}','{}'],1,'Both earlier values have been inserted; the set does not store duplicate entries.'),
    ('[2,1,2]', ['seen={2}','seen={1,2}','duplicate 2 found'], 'Repeat a value, change it to a new value, and compare membership checks.', '0–32 integers; show exact key equality, not invented hash addresses.'))

concept('sorting', 'Sorting and Merging', ['arrays'], ['merge-sort','quick-sort'],
    ['Merge two ordered sequences using two cursors.', 'Explain how merge sort uses this operation after recursive splitting.'],
    'Two sorted rows let you take the smaller front item each time. Once both fronts are ordered, the chosen value cannot be preceded by a smaller unconsumed value.',
    'Merge [1,4] and [2,3]: choose 1,2,3, then drain 4. Output [1,2,3,4] is ordered and contains every input occurrence.',
    'The output prefix is sorted and contains exactly the consumed input prefixes.',
    'A merge assumes both inputs are sorted. Do not quote O(n) merging as the complexity of sorting arbitrary input. Choosing the left equal key preserves cross-run stability.',
    dict(time='O(n+m) merge; O(n log n) merge sort', space='O(n+m) merge output', assumptions='Both merge inputs are nondecreasing; merge-sort child lesson covers splitting.'),
    '''static int[] merge(int[] a, int[] b) {
        int[] out = new int[a.length + b.length];
        int i = 0, j = 0, k = 0;
        while (i < a.length && j < b.length) out[k++] = a[i] <= b[j] ? a[i++] : b[j++];
        while (i < a.length) out[k++] = a[i++];
        while (j < b.length) out[k++] = b[j++];
        return out;
    }''', [('Arrays.toString(merge(new int[]{1,4},new int[]{2,3}))','[1, 2, 3, 4]'), ('Arrays.toString(merge(new int[]{},new int[]{1,1}))','[1, 1]'), ('Arrays.toString(merge(new int[]{},new int[]{}))','[]')],
    ('Merging [1,4] and [2,3], which value follows the first 1?', ['4','2','3'],1,'Compare the current fronts 4 and 2; choose 2.'),
    ('left=[1,4], right=[2,3]', ['out=[1]','out=[1,2]','out=[1,2,3]','out=[1,2,3,4]'], 'Use duplicate keys and empty runs; keep element identity through merging.', 'Sorted runs of up to 16 elements each; splitting and pivot sorting are separate child traces.'))

concept('prefix-sums', 'Prefix Sums', ['arrays'], ['prefix-sums'],
    ['Build an exclusive-prefix table.', 'Answer a half-open range sum using two stored values.'],
    'Store the sum before every boundary. The sum between two boundaries is the later prefix minus the earlier prefix.',
    'For [2,1,5], prefix=[0,2,3,8]. The range [1,3) sums to prefix[3]-prefix[1]=8-2=6.',
    'prefix[i] equals the sum of the first i values; prefix[0] is zero.',
    'Mixing inclusive and exclusive endpoints causes off-by-one errors. Prefix sums work with negative values; a positive-only shrinking window is a different technique.',
    dict(time='O(n) build; O(1) per range query', space='O(n) table', assumptions='0 <= left <= right <= n; long sums.'),
    '''static long[] prefix(int[] a) {
        long[] p = new long[a.length + 1];
        for (int i = 0; i < a.length; i++) p[i + 1] = p[i] + a[i];
        return p;
    }
    static long range(long[] p, int left, int right) {
        if (left < 0 || left > right || right >= p.length) throw new IllegalArgumentException();
        return p[right] - p[left];
    }''', [('Arrays.toString(prefix(new int[]{2,1,5}))','[0, 2, 3, 8]'), ('range(prefix(new int[]{2,1,5}),1,3)','6'), ('range(prefix(new int[]{}),0,0)','0'), ('range(prefix(new int[]{-2,3}),0,2)','1')],
    ('For prefix=[0,2,3,8], which expression gives a[1..3)?', ['8-3','8-2','3-2'],1,'Subtract the sum before boundary 1 from the sum before boundary 3.'),
    ('a=[2,1,5], range=[1,3)', ['p=[0]','p=[0,2]','p=[0,2,3]','p=[0,2,3,8]; query=6'], 'Move either query boundary and compare the highlighted original range.', '0–32 integers; half-open endpoints; long accumulation.'))

concept('two-pointers', 'Two Pointers', ['strings','sorting'], ['two-pointers'],
    ['Use ordering to discard impossible pairs.', 'Move one pointer with a reason rather than enumerating every pair.'],
    'Place a cursor at each end of a sorted row. If their sum is too small, moving the right cursor left cannot help; advance the left cursor instead.',
    'Sorted [1,2,3,4,6,7], target=9: 1+7=8, so advance left. Then 2+7=9. The answer exists at two distinct positions.',
    'Any pair not yet ruled out lies within the current cursor interval.',
    'The ordering argument fails for unsorted input. Sort first when permitted and count that cost; sorted positions are not original indices.',
    dict(time='O(n) search after sorting', space='O(1) search auxiliary', assumptions='Input is already sorted; long pair sum avoids int overflow.'),
    '''static boolean pair(int[] sorted, long target) {
        int left = 0, right = sorted.length - 1;
        while (left < right) {
            long sum = (long) sorted[left] + sorted[right];
            if (sum == target) return true;
            if (sum < target) left++; else right--;
        }
        return false;
    }''', [('pair(new int[]{1,2,3,4,6,7},9)','true'), ('pair(new int[]{4},8)','false'), ('pair(new int[]{2,2},4)','true'), ('pair(new int[]{},0)','false')],
    ('At values 1 and 7 with target 9, which cursor moves?', ['Left advances','Right retreats','Both move'],0,'The sum is too small. Only advancing the left value can increase it in a sorted interval.'),
    ('sorted=[1,2,3,4,6,7], target=9', ['left=0,right=5,sum=8','left=1,right=5,sum=9'], 'Change target or repeat a value; distinguish sorted positions from original indices.', 'Sorted integers; distinct positions; preparation cost shown separately.'))

concept('fixed-window', 'Fixed-Size Sliding Window', ['arrays','prefix-sums'], ['sliding-window'],
    ['Reuse a fixed-length contiguous sum.', 'Handle all-negative inputs and reject invalid window sizes.'],
    'A frame holds k adjacent values. Move it right by subtracting the outgoing value and adding the incoming one.',
    'For [2,1,5,1,3,2] and k=3, the full-window sums are 8,7,9,6. The largest is 9.',
    'The rolling sum equals the last min(k,right+1) values; compare with best only after a full window exists.',
    'Initializing best to zero breaks all-negative arrays. This fixed-size sum supports negative values; variable-size sum shrinking needs extra assumptions.',
    dict(time='O(n)', space='O(1) auxiliary', assumptions='1 <= k <= n; long accumulated sums.'),
    '''static long bestWindow(int[] a, int k) {
        if (k < 1 || k > a.length) throw new IllegalArgumentException();
        long sum = 0, best = Long.MIN_VALUE;
        for (int right = 0; right < a.length; right++) {
            sum += a[right];
            if (right >= k) sum -= a[right - k];
            if (right >= k - 1) best = Math.max(best, sum);
        }
        return best;
    }''', [('bestWindow(new int[]{2,1,5,1,3,2},3)','9'), ('bestWindow(new int[]{-4,-2,-3},2)','-5'), ('bestWindow(new int[]{7},1)','7')],
    ('A window sum of 8 loses 2 and gains 1. What is the next sum?', ['7','9','8'],0,'Reuse the previous total: 8 - 2 + 1 = 7.'),
    ('[2,1,5,1,3,2], k=3', ['[2,1,5]:8','[1,5,1]:7','[5,1,3]:9','[1,3,2]:6'], 'Edit input or k, then predict incoming/outgoing values.', '1–32 integers; 1 <= k <= n; existing interactive window trace.'))

concept('variable-window', 'Variable-Size Sliding Window', ['hashing','fixed-window'], ['variable-window'],
    ['Grow and shrink a contiguous range to restore a condition.', 'Separate a distinct-character condition from positive-sum conditions.'],
    'Stretch a frame while it remains valid. When a repeated character enters, remove characters from the left until the frame is valid again.',
    'For "abca", the frame grows through a,ab,abc. The next a forces the old a out, leaving bca. The best length stays 3.',
    'After shrinking, all characters in the current frame are distinct.',
    'Removing only once can leave a repeated character inside the frame. For minimum-length sum windows, positivity is what makes shrinking monotonic; arbitrary negatives break that proof.',
    dict(time='Expected O(n)', space='O(min(n, alphabet size))', assumptions='ASCII example; each character enters/leaves at most once.'),
    '''static int longestDistinct(String s) {
        Set<Character> window = new HashSet<>();
        int left = 0, best = 0;
        for (int right = 0; right < s.length(); right++) {
            char incoming = s.charAt(right);
            while (window.contains(incoming)) window.remove(s.charAt(left++));
            window.add(incoming);
            best = Math.max(best, right - left + 1);
        }
        return best;
    }''', [('longestDistinct("abca")','3'), ('longestDistinct("abba")','2'), ('longestDistinct("")','0'), ('longestDistinct("aaaa")','1')],
    ('When the second b arrives in "abba", is removing only the first a enough?', ['Yes','No'],1,'The old b remains, so shrink again until the duplicate is removed.'),
    ('"abca"', ['[a],best=1','[ab],best=2','[abc],best=3','remove a; [bca],best=3'], 'Use "abba" to expose a single-if shrinking bug.', 'ASCII 0–32 characters; no sum-window claims for negative numbers.'))

concept('binary-search', 'Binary Search', ['sorting'], ['binary-search'],
    ['Maintain an inclusive candidate interval.', 'Guarantee progress and distinguish exact search from insertion boundaries.'],
    'A comparison with the middle of an ordered row discards a whole impossible half.',
    'In [1,2,3,4,6,7], target 5: mid=2 gives 3, mid=4 gives 6, then mid=3 gives 4. The interval becomes empty and returns -1.',
    'If the target exists, some occurrence remains in [low,high].',
    'Using low=mid or high=mid in this inclusive version can stop progress. Exact-match search may return any duplicate occurrence; lower-bound search answers a different question.',
    dict(time='O(log n)', space='O(1) auxiliary', assumptions='Sorted nondecreasing array; mid uses low+(high-low)/2.'),
    '''static int search(int[] a, int target) {
        int low = 0, high = a.length - 1;
        while (low <= high) {
            int mid = low + (high - low) / 2;
            if (a[mid] == target) return mid;
            if (a[mid] < target) low = mid + 1; else high = mid - 1;
        }
        return -1;
    }''', [('search(new int[]{1,2,3,4,6,7},5)','-1'), ('search(new int[]{},1)','-1'), ('search(new int[]{2},2)','0'), ('search(new int[]{1,2,2},2)','1')],
    ('If a[mid] is smaller than target, what is the new low in this version?', ['mid','mid + 1','low + 1 always'],1,'mid has been ruled out, so advance past it.'),
    ('sorted=[1,2,3,4,6,7], target=5', ['low=0,high=5,mid=2','low=3,high=5,mid=4','low=3,high=3,mid=3','low=4,high=3: absent'], 'Try present, absent and duplicated values; show sorting as preparation.', '0–32 sorted values; current trace accepts nonempty teaching input.'))

concept('intervals', 'Intervals', ['sorting'], ['intervals'],
    ['Sort intervals by start and merge overlaps.', 'State whether touching endpoints count as overlap.'],
    'Lay closed segments on a number line. Sorted starts let you extend the latest output segment or begin a separate one.',
    'For [1,3],[2,6],[8,10], the second segment overlaps the first and extends its end to 6. Result: [1,6],[8,10].',
    'Output segments are disjoint and cover exactly the processed input intervals.',
    'For closed intervals [1,2] and [2,3], equality means overlap. Half-open intervals need a different convention. Never mutate caller intervals accidentally while merging.',
    dict(time='O(n log n)', space='O(n) copy/output', assumptions='Valid closed [start,end] pairs; endpoints may touch; caller input preserved.'),
    '''static int[][] mergeIntervals(int[][] input) {
        int[][] a = Arrays.stream(input).map(int[]::clone).toArray(int[][]::new);
        Arrays.sort(a, Comparator.comparingInt(x -> x[0]));
        List<int[]> out = new ArrayList<>();
        for (int[] next : a) {
            if (out.isEmpty() || out.get(out.size()-1)[1] < next[0]) out.add(next);
            else out.get(out.size()-1)[1] = Math.max(out.get(out.size()-1)[1], next[1]);
        }
        return out.toArray(int[][]::new);
    }''', [('Arrays.deepToString(mergeIntervals(new int[][]{{1,3},{2,6},{8,10}}))','[[1, 6], [8, 10]]'), ('Arrays.deepToString(mergeIntervals(new int[][]{{1,2},{2,3}}))','[[1, 3]]'), ('Arrays.deepToString(mergeIntervals(new int[][]{}))','[]')],
    ('With closed endpoints, do [1,2] and [2,3] merge?', ['Yes','No'],0,'Both contain 2, so the merged interval is [1,3].'),
    ('[1,3],[2,6],[8,10]', ['sort by start','extend [1,3] to [1,6]','append [8,10]'], 'Move endpoints and compare touching, nested and disjoint segments.', '0–16 valid closed intervals; distinguish endpoint convention.'))

concept('matrices', 'Matrices and Grid Coordinates', ['arrays'], ['matrices'],
    ['Distinguish row and column dimensions.', 'Map a cell (r,c) to (c,r) during transpose.'],
    'A rectangular matrix is a row of rows. Coordinates identify both a row and a column; a transpose swaps their roles.',
    'Transpose [[1,2,3],[4,5,6]] into [[1,4],[2,5],[3,6]]. The input is 2×3 and the output is 3×2.',
    'Every copied source cell a[r][c] appears at out[c][r].',
    'Using row count for both dimensions only works for square inputs. Reject ragged rows for this rectangular operation.',
    dict(time='O(rows × columns)', space='O(rows × columns) output', assumptions='Rectangular non-null rows; zero rows produce an empty matrix.'),
    '''static int[][] transpose(int[][] a) {
        int rows = a.length, cols = rows == 0 ? 0 : a[0].length;
        for (int[] row : a) if (row.length != cols) throw new IllegalArgumentException("ragged matrix");
        int[][] out = new int[cols][rows];
        for (int r = 0; r < rows; r++) for (int c = 0; c < cols; c++) out[c][r] = a[r][c];
        return out;
    }''', [('Arrays.deepToString(transpose(new int[][]{{1,2,3},{4,5,6}}))','[[1, 4], [2, 5], [3, 6]]'), ('Arrays.deepToString(transpose(new int[][]{}))','[]'), ('Arrays.deepToString(transpose(new int[][]{{7}}))','[[7]]')],
    ('Where does source cell (1,2) go during transpose?', ['(2,1)','(1,2)','(0,1)'],0,'Swap the row and column coordinates.'),
    ('[[1,2,3],[4,5,6]]', ['(0,0) → (0,0)','(0,1) → (1,0)','(1,2) → (2,1)'], 'Use a non-square grid and follow one cell into the output.', 'Rectangular grid up to 6×6; ragged input explicitly invalid.'))

NODE = '''static class Node {
    int value; Node next;
    Node(int value, Node next) { this.value = value; this.next = next; }
}
static Node list(int... a) {
    Node head = null;
    for (int i = a.length - 1; i >= 0; i--) head = new Node(a[i], head);
    return head;
}
static String values(Node head) {
    List<Integer> out = new ArrayList<>();
    for (Node p = head; p != null; p = p.next) out.add(p.value);
    return out.toString();
}'''

concept('linked-lists', 'Linked Lists', ['arrays'], ['linked-list'],
    ['Follow node references rather than adjacent indexes.', 'Reverse links without losing the unprocessed suffix.'],
    'Each node holds a value and a reference to the next node. Move arrows, not values, when reversing the chain.',
    'For 4→2→7→1→3→6, first save 2, point 4 to null, then continue from 2. The final head is 6 and the chain is 6→3→1→7→2→4.',
    'prev heads the reversed prefix; current heads the untouched suffix.',
    'Overwriting current.next before saving it loses access to the remaining nodes. Equal values still have distinct node identities.',
    dict(time='O(n)', space='O(1) auxiliary', assumptions='Acyclic singly linked list; null is an empty list.'),
    '''static Node reverseList(Node current) {
        Node prev = null;
        while (current != null) {
            Node next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        return prev;
    }
    ''' + NODE,
    [('values(reverseList(list(4,2,7,1,3,6)))','[6, 3, 1, 7, 2, 4]'), ('values(reverseList(null))','[]'), ('values(reverseList(list(2,1,2)))','[2, 1, 2]')],
    ('What must be saved before overwriting current.next?', ['The original next reference','Only the current value','The array length'],0,'Keep the unprocessed suffix reachable before changing the link.'),
    ('4→2→7→1→3→6', ['prev=null,current=4','4→null; current=2','2→4→null; current=7','head=6: 6→3→1→7→2→4'], 'Use duplicate values and track node IDs while reversing arrows.', 'Acyclic list; no cyclic-list claims; existing renderer needs arrow-state refinement.'))

concept('stacks', 'Stacks', ['arrays'], ['stack'],
    ['Use last-in, first-out operations.', 'Handle an empty structure before removing an element.'],
    'A stack is a pile with one accessible end. The last item placed on top is the first removed.',
    'Push 4,2,7,1,3,6. Pop returns 6,3,1,7,2,4. Values below the top retain their relative order.',
    'The top is the most recently pushed item that has not been popped.',
    'A queue removes from the opposite end. Check emptiness before pop; use a Deque rather than treating sorted order as stack order.',
    dict(time='O(n) for n pushes and pops; amortized O(1) per deque operation', space='O(n) structure', assumptions='ArrayDeque used as an implementation, not an assessed algorithm replacement.'),
    '''static List<Integer> popOrder(int[] a) {
        Deque<Integer> stack = new ArrayDeque<>();
        for (int value : a) stack.push(value);
        List<Integer> out = new ArrayList<>();
        while (!stack.isEmpty()) out.add(stack.pop());
        return out;
    }''', [('popOrder(new int[]{4,2,7,1,3,6})','[6, 3, 1, 7, 2, 4]'), ('popOrder(new int[]{})','[]'), ('popOrder(new int[]{2,2})','[2, 2]')],
    ('Push 4, then 2, then 7. Which value pops first?', ['4','2','7'],2,'The last pushed value, 7, is on top.'),
    ('push [4,2,7,1,3,6]', ['top=4','top=6 after pushes','pop 6,3,1,7,2,4'], 'Interleave pushes and pops; attempt a pop only after checking emptiness.', '0–32 values; top and empty state explicit.'))

concept('queues', 'Queues and Deques', ['arrays','stacks'], ['queue'],
    ['Use first-in, first-out processing.', 'Distinguish a queue discipline from a deque container.'],
    'Join at the back and leave from the front. A deque supports both ends, so the operations you choose determine FIFO or LIFO behavior.',
    'Enqueue 4,2,7,1,3,6 at the back. Removing from the front returns 4,2,7,1,3,6.',
    'The front is the earliest enqueued item that has not been removed.',
    'Using removeLast after addLast turns a deque into a stack. BFS depends on FIFO; substituting the wrong removal changes exploration order.',
    dict(time='O(n) total; amortized O(1) per deque operation', space='O(n) structure', assumptions='Explicit addLast/removeFirst; empty removal guarded.'),
    '''static List<Integer> queueOrder(int[] a) {
        Deque<Integer> queue = new ArrayDeque<>();
        for (int value : a) queue.addLast(value);
        List<Integer> out = new ArrayList<>();
        while (!queue.isEmpty()) out.add(queue.removeFirst());
        return out;
    }''', [('queueOrder(new int[]{4,2,7,1,3,6})','[4, 2, 7, 1, 3, 6]'), ('queueOrder(new int[]{})','[]'), ('queueOrder(new int[]{2,2})','[2, 2]')],
    ('After addLast(4), addLast(2), what does removeFirst return?', ['2','4'],1,'4 has waited longest at the front.'),
    ('enqueue [4,2,7,1,3,6]', ['front=4','back=6 after enqueues','dequeue 4,2,7,1,3,6'], 'Switch removal end and explain why the behavior becomes LIFO.', '0–32 values; show front/back and FIFO ordering.'))

concept('recursion', 'Recursion and the Call Stack', ['stacks'], ['recursion'],
    ['Define a base case and a smaller subproblem.', 'Distinguish a suspended frame from a returned value.'],
    'A function leaves a frame on the call stack while a smaller call runs. Returning resumes that exact frame with its own local state.',
    'factorial(5) waits for factorial(4), down to factorial(0)=1. Unwinding returns 1,2,6,24,120. Each multiplication happens after the smaller call returns.',
    'factorial(n) returns n times factorial(n-1), with factorial(0)=1.',
    'A missing base case or a call that does not reduce the problem can recurse indefinitely. The call stack consumes space even when no explicit array is allocated.',
    dict(time='O(n)', space='O(n) call stack', assumptions='0 <= n <= 10 for this bounded example; array-sum application uses the same base/reduction structure.'),
    '''static long factorial(int n) {
        if (n < 0 || n > 10) throw new IllegalArgumentException();
        if (n == 0) return 1;
        return n * factorial(n - 1);
    }
    static long sumFrom(int[] a, int i) {
        if (i == a.length) return 0;
        return a[i] + sumFrom(a, i + 1);
    }''', [('factorial(5)','120'), ('factorial(0)','1'), ('sumFrom(new int[]{2,1,5},0)','8'), ('sumFrom(new int[]{},0)','0')],
    ('What is still pending when factorial(5) calls factorial(4)?', ['Multiplication by 5','A second independent input array','Nothing'],0,'The caller frame must multiply the returned result by its own n=5.'),
    ('factorial(5)', ['call 5,4,3,2,1,0','base returns 1','unwind 1,2,6,24,120'], 'Change n and follow frame-local n separately from returned result.', 'n=0..10; show base frame and unwind; no arbitrary own-code tracing.'))

concept('backtracking', 'Backtracking', ['recursion'], ['backtracking'],
    ['Explore choices recursively and restore shared state.', 'Snapshot a result instead of keeping an alias to the mutable path.'],
    'Walk a decision tree with a reusable path. Choose an item, explore descendants, then undo that choice before trying the next branch.',
    'For [1,2], include-first traversal records [1,2], [1], [2], []. After recording [1,2], remove 2 before exploring the branch without it.',
    'On entering visit(i), path contains exactly the choices for indices below i.',
    'Missing the undo contaminates sibling branches. Storing path itself makes every result alias one mutable list. Duplicate input values require a separate deduplication policy.',
    dict(time='O(n × 2^n) including copied subsets', space='O(n) auxiliary; O(n × 2^n) output', assumptions='Distinct input values; bounded teaching subset size.'),
    '''static List<List<Integer>> subsets(int[] a) {
        List<List<Integer>> out = new ArrayList<>();
        visit(a, 0, new ArrayList<>(), out);
        return out;
    }
    static void visit(int[] a, int i, List<Integer> path, List<List<Integer>> out) {
        if (i == a.length) { out.add(new ArrayList<>(path)); return; }
        path.add(a[i]);
        visit(a, i + 1, path, out);
        path.remove(path.size() - 1);
        visit(a, i + 1, path, out);
    }''', [('subsets(new int[]{1,2})','[[1, 2], [1], [2], []]'), ('subsets(new int[]{})','[[]]'), ('subsets(new int[]{7})','[[7], []]')],
    ('Why copy path when recording a subset?', ['Later undo operations mutate path','Copying sorts it','Recursion requires sorted output'],0,'Each recorded subset must remain independent of later path changes.'),
    ('[1,2]', ['choose 1','choose 2: record [1,2]','undo 2: record [1]','undo 1: explore [2],[]'], 'Toggle an include/exclude branch and watch undo restore the parent state.', 'Distinct values; at most 5 items in existing trace; exponential output explicit.'))

TREE = '''static class Tree {
    int value; Tree left, right;
    Tree(int value, Tree left, Tree right) { this.value=value; this.left=left; this.right=right; }
}
static Tree sample() {
    return new Tree(4, new Tree(2,new Tree(1,null,null),new Tree(3,null,null)),new Tree(7,new Tree(6,null,null),null));
}'''

concept('binary-trees', 'Binary Trees and Traversal', ['linked-lists','recursion'], ['tree-traversal'],
    ['Distinguish a general binary tree from a BST.', 'Visit a tree in inorder or compute height from child results.'],
    'A binary tree node has up to two child references. Traversal chooses when to visit the node relative to those children; no ordering property is required.',
    'For root 4 with left subtree 2(1,3) and right subtree 7(6,null), inorder visits [1,2,3,4,6,7] and height is 3 nodes. This example is ordered, but arbitrary binary trees need not be.',
    'inorder(node) processes every node in left subtree, then node, then right subtree.',
    'Inorder output is sorted only for a valid BST. Define whether height counts nodes or edges; the empty tree has height 0 in this lesson.',
    dict(time='O(n)', space='O(h) call stack, plus O(n) output', assumptions='Acyclic tree; height counts nodes; existing interactive child demonstrates level order, not inorder.'),
    '''static List<Integer> inorder(Tree root) {
        List<Integer> out = new ArrayList<>(); walk(root, out); return out;
    }
    static void walk(Tree node, List<Integer> out) {
        if (node == null) return;
        walk(node.left, out); out.add(node.value); walk(node.right, out);
    }
    static int height(Tree node) {
        return node == null ? 0 : 1 + Math.max(height(node.left), height(node.right));
    }
    ''' + TREE,
    [('inorder(sample())','[1, 2, 3, 4, 6, 7]'), ('height(sample())','3'), ('inorder(null)','[]'), ('height(null)','0')],
    ('Does inorder traversal sort every binary tree?', ['Yes','Only if the tree satisfies the BST ordering property'],1,'Traversal follows links; it does not rearrange arbitrary node values.'),
    ('4 with children 2(1,3),7(6,null)', ['walk left:1,2,3','visit root:4','walk right:6,7'], 'Change a value without rewiring links to see why general inorder need not be sorted.', 'Small acyclic tree; inorder specification separate from the existing level-order renderer.'))

concept('bst', 'Binary Search Trees', ['binary-search','binary-trees'], ['bst'],
    ['Insert/search using subtree ordering.', 'Explain why an unbalanced BST may degrade to linear height.'],
    'Each node splits the remaining keys: every left key is smaller and every right key is larger. Follow that decision at each level.',
    'Insert [8,3,10,1,6,14,4,7,13]. Inorder becomes [1,3,4,6,7,8,10,13,14]; inserting 6 again leaves the tree unchanged.',
    'For every node, all left descendants are smaller and all right descendants are larger.',
    'Checking only immediate children does not validate a whole BST. Sorted insertion can produce a chain; O(log n) requires a height assumption.',
    dict(time='O(h) per insertion/search; worst O(n)', space='O(h) recursive stack; O(n) stored nodes', assumptions='Distinct keys; duplicates ignored; no balancing in this lesson.'),
    '''static Tree insert(Tree node, int value) {
        if (node == null) return new Tree(value,null,null);
        if (value < node.value) node.left = insert(node.left,value);
        else if (value > node.value) node.right = insert(node.right,value);
        return node;
    }
    static List<Integer> ordered(int... a) {
        Tree root=null; for (int value:a) root=insert(root,value);
        List<Integer> out=new ArrayList<>(); collect(root,out); return out;
    }
    static void collect(Tree n,List<Integer> out) {
        if(n==null)return; collect(n.left,out);out.add(n.value);collect(n.right,out);
    }
    ''' + TREE,
    [('ordered(8,3,10,1,6,14,4,7,13)','[1, 3, 4, 6, 7, 8, 10, 13, 14]'), ('ordered(2,2,1)','[1, 2]'), ('ordered()','[]')],
    ('After 8,3,10, where does 6 go?', ['Left of 3','Right of 3','Right of 10'],1,'6 is below 8 but above 3, so it becomes the right child of 3.'),
    ('insert [8,3,10,1,6,14,4,7,13]', ['root 8','3 left,10 right','6 right of 3','13 left of 14'], 'Insert sorted or repeated keys; follow comparisons and stable node IDs.', '1–32 input keys; equal keys ignored; no balancing guarantee.'))

concept('heaps', 'Heaps and Priority Queues', ['sorting','binary-trees'], ['heap'],
    ['Maintain parent/child heap order.', 'Distinguish the maximum at the root from a fully sorted array.'],
    'A complete tree fits in an array: parent of i is (i-1)/2. In a max-heap, a new value moves up until its parent is at least as large.',
    'Insert [4,2,7,1,3,6]. After 7 enters, it swaps with 4; the final heap is [7,3,6,1,2,4]. Only parent-child order is guaranteed.',
    'Every parent is at least as large as its children.',
    'A heap is not a sorted array, and Java PriorityQueue defaults to a min-heap. A top-k problem needs a deliberate choice of min/max orientation.',
    dict(time='O(log n) per insertion; O(n log n) repeated insertion', space='O(n) heap storage', assumptions='Custom max-heap insertion shown; bottom-up O(n) heap building is a later extension.'),
    '''static List<Integer> heap(int[] a) {
        List<Integer> h=new ArrayList<>();
        for(int value:a) {
            h.add(value); int i=h.size()-1;
            while(i>0) {
                int parent=(i-1)/2;
                if(h.get(parent)>=h.get(i)) break;
                Collections.swap(h,parent,i); i=parent;
            }
        }
        return h;
    }''', [('heap(new int[]{4,2,7,1,3,6})','[7, 3, 6, 1, 2, 4]'), ('heap(new int[]{})','[]'), ('heap(new int[]{2,2})','[2, 2]')],
    ('Is every sibling pair ordered in a max-heap?', ['Yes','No'],1,'The invariant constrains parents and children, not sibling order.'),
    ('insert [4,2,7,1,3,6]', ['[4]','[4,2]','[7,2,4]','[7,3,6,1,2,4]'], 'Insert a new maximum and observe every parent comparison/swap.', '0–32 values; existing trace records completed insertions, intermediate bubble swaps remain a renderer/trace gap.'))

GRAPH = '''static List<List<Integer>> adjacency(int n, int[][] edges) {
    if(n<0)throw new IllegalArgumentException();
    List<List<Integer>> graph=new ArrayList<>();
    for(int i=0;i<n;i++)graph.add(new ArrayList<>());
    for(int[] e:edges) {
        if(e.length!=2 || e[0]<0 || e[0]>=n || e[1]<0 || e[1]>=n)throw new IllegalArgumentException();
        graph.get(e[0]).add(e[1]);
    }
    return graph;
}'''

concept('graphs', 'Graph Representation', ['hashing','matrices'], ['graphs'],
    ['Build an adjacency list including isolated vertices.', 'Distinguish directed edges, undirected edges and edge weights.'],
    'A graph names vertices and stores their connections. An adjacency list gives every vertex a row of outgoing neighbours, including an empty row for an isolated vertex.',
    'For n=4 and directed edges 0→1,0→2,2→3, adjacency is [[1,2],[],[3],[]]. Making this undirected also requires the reverse connection for each edge.',
    'Every supplied directed edge u→v contributes v to exactly the outgoing row for u.',
    'Forgetting isolated vertices changes n. A matrix costs O(V²) storage, while a list stores O(V+E). Parallel edges and self loops require an explicit policy.',
    dict(time='O(V+E) build', space='O(V+E)', assumptions='Vertices 0..n-1; directed edges; preserve parallel edges and self loops.'),
    GRAPH,
    [('adjacency(4,new int[][]{{0,1},{0,2},{2,3}})','[[1, 2], [], [3], []]'), ('adjacency(2,new int[][]{})','[[], []]'), ('adjacency(1,new int[][]{{0,0},{0,0}})','[[0, 0]]'), ('adjacency(0,new int[][]{})','[]')],
    ('For an undirected edge between 0 and 1, which rows need entries?', ['Only row 0','Rows 0 and 1','No rows'],1,'Store 1 under 0 and 0 under 1, unless using a different explicitly documented representation.'),
    ('V=4; edges 0→1,0→2,2→3', ['create four empty rows','row 0=[1,2]','row 2=[3]; rows 1,3 stay empty'], 'Toggle directedness or add an isolated vertex, self loop or parallel edge.', '0–8 vertices and up to 16 edges; explicit graph-input renderer not yet implemented.'))

concept('bfs', 'Breadth-First Search', ['queues','graphs'], ['bfs'],
    ['Use FIFO to explore by edge-distance layers.', 'Mark discovery on enqueue so a vertex is queued once.'],
    'A queue holds the discovered frontier. Removing the oldest vertex finishes the nearer layer before later discoveries.',
    'For the teaching graph with edges i→i+1 and i→i+2 where valid, start from 0. Queue [0] becomes [1,2], then [2,3], then [3,4]. Distances are [0,1,1,2,2,3].',
    'When first enqueued, distance[v] is the minimum number of unweighted edges from the source.',
    'Visited-on-removal can enqueue the same vertex many times. BFS does not minimize arbitrary weighted costs; unreachable vertices retain -1.',
    dict(time='O(V+E) with adjacency lists', space='O(V) auxiliary', assumptions='Unweighted directed graph; valid source; neighbour order follows input.'),
    '''static int[] distances(List<List<Integer>> graph,int source) {
        int[] distance=new int[graph.size()]; Arrays.fill(distance,-1);
        Deque<Integer> queue=new ArrayDeque<>(); queue.addLast(source); distance[source]=0;
        while(!queue.isEmpty()) {
            int u=queue.removeFirst();
            for(int v:graph.get(u)) if(distance[v]==-1) {
                distance[v]=distance[u]+1; queue.addLast(v);
            }
        }
        return distance;
    }
    ''' + GRAPH,
    [('Arrays.toString(distances(adjacency(6,new int[][]{{0,1},{0,2},{1,2},{1,3},{2,3},{2,4},{3,4},{3,5},{4,5}}),0))','[0, 1, 1, 2, 2, 3]'), ('Arrays.toString(distances(adjacency(3,new int[][]{{0,0},{0,1},{0,1},{1,0}}),0))','[0, 1, -1]')],
    ('Why mark a vertex discovered when it enters the queue?', ['To prevent repeated enqueueing','To sort vertex IDs','To ignore all edges'],0,'Another parent can encounter it before it is removed; early discovery prevents duplicates.'),
    ('generated 6-vertex graph; source 0', ['queue=[0]','expand 0:queue=[1,2]','expand 1:queue=[2,3]','distance=[0,1,1,2,2,3]'], 'Compare queue and discovery state; change generated input length.', 'Current trace generates a directed graph and ignores displayed weights for BFS; explicit adjacency/grid input is future work.'))

concept('dfs', 'Depth-First Search', ['recursion','graphs'], ['dfs'],
    ['Explore a branch before returning to its parent.', 'Use a visited set to handle cycles and a forest to cover disconnected components.'],
    'Keep the current path on the call stack. Enter an unvisited neighbour, finish its descendants, then return to try the next neighbour.',
    'With neighbours in ascending order on the generated six-vertex graph, DFS enters 0,1,2,3,4,5 before unwinding. Changing neighbour order can produce a different valid DFS.',
    'Every active frame represents a discovered vertex whose outgoing neighbours are not yet fully explored.',
    'DFS does not guarantee shortest paths. Mark before descending to break cycles. Pre-marking every sibling before exploring one can produce a traversal that is not recursive DFS.',
    dict(time='O(V+E)', space='O(V) visited/call stack', assumptions='Small teaching graphs; outer loop covers disconnected components; recursion may overflow on deep real graphs.'),
    '''static List<Integer> dfs(List<List<Integer>> graph) {
        boolean[] seen=new boolean[graph.size()]; List<Integer> out=new ArrayList<>();
        for(int u=0;u<graph.size();u++) if(!seen[u]) explore(graph,u,seen,out);
        return out;
    }
    static void explore(List<List<Integer>> graph,int u,boolean[] seen,List<Integer> out) {
        seen[u]=true; out.add(u);
        for(int v:graph.get(u)) if(!seen[v]) explore(graph,v,seen,out);
    }
    ''' + GRAPH,
    [('dfs(adjacency(6,new int[][]{{0,1},{0,2},{1,2},{1,3},{2,3},{2,4},{3,4},{3,5},{4,5}}))','[0, 1, 2, 3, 4, 5]'), ('dfs(adjacency(4,new int[][]{{0,1},{1,0},{2,2}}))','[0, 1, 2, 3]'), ('dfs(adjacency(0,new int[][]{}))','[]')],
    ('Does finding a vertex first with DFS prove the shortest route?', ['Yes','No'],1,'DFS follows a branch without maintaining distance layers.'),
    ('generated 6-vertex graph, ascending neighbours', ['enter 0','descend 1,2,3,4,5','exit 5,4,3,2,1,0'], 'Step through entry and return; compare recursive path with BFS frontier.', 'Up to 8 generated vertices; trace visits source component, full-code forest also handles disconnected graphs.'))

concept('dynamic-programming', 'Dynamic Programming: Memoization and Tabulation', ['prefix-sums','recursion'], ['memoization','tabulation'],
    ['Define state, base cases and dependencies before coding.', 'Compare top-down caching with bottom-up evaluation and transfer to a new recurrence.'],
    'A dependency graph can revisit the same smaller question. Memoization caches answers when requested; tabulation chooses an order with dependencies already available.',
    'F(0)=0,F(1)=1. For n=7, both versions return 13 from table [0,1,1,2,3,5,8,13]. Staircase counts and House Robber reuse state thinking but have different meanings and base cases.',
    'A cached state is final; a bottom-up state reads only final earlier dependencies.',
    'Using zero to mean both uncomputed and a valid answer is ambiguous. Memorizing Fibonacci code does not define a state for House Robber; derive take/skip decisions for the prefix instead.',
    dict(time='O(n) per Fibonacci version', space='O(n) table; top-down also O(n) call stack', assumptions='n=0..16; examples keep table for visibility; final-value rolling storage can use O(1).'),
    '''static int fibMemo(int n) {
        Integer[] memo=new Integer[n+1]; return solve(n,memo);
    }
    static int solve(int n,Integer[] memo) {
        if(n<2)return n;
        if(memo[n]==null)memo[n]=solve(n-1,memo)+solve(n-2,memo);
        return memo[n];
    }
    static int fibTable(int n) {
        int[] dp=new int[n+1]; if(n>0)dp[1]=1;
        for(int i=2;i<=n;i++)dp[i]=dp[i-1]+dp[i-2];
        return dp[n];
    }''', [('fibMemo(7)','13'), ('fibTable(7)','13'), ('fibMemo(0)','0'), ('fibTable(1)','1'), ('fibMemo(16)==fibTable(16)','true')],
    ('If F(4)=3 and F(5)=5, what is F(6)?', ['5','8','13'],1,'The recurrence reads both earlier states: 3+5=8.'),
    ('F(7), base F(0)=0,F(1)=1', ['base [0,1]','write 1,2,3,5,8,13','both methods return 13'], 'Change n, compare repeated calls with cache hits and bottom-up writes.', 'n=0..16; do not imply Fibonacci is the complete DP curriculum; practice derives two distinct state models.'))

QUESTIONS = {}


def question(number, title, slug, tags, hint1, hint2, outline):
    key = 'leetcode-' + str(number)
    QUESTIONS[key] = dict(id=key, kind='external-reference', platform='leetcode',
        platformId=str(number), title=title, canonicalUrl='https://leetcode.com/problems/' + slug + '/',
        conceptTags=['concept-' + x for x in tags],
        progressiveHints=[hint1, hint2, outline], approachOutline=outline,
        provenance=dict(sourceIds=['leetcode-canonical','company-csv','handbook','grind75'],
            selectionBasis='Manual pedagogical selection informed by topic coverage; not a claim of membership in every source list.',
            companyLikelihood=None), implementationStatus='planned-phase-2', access='Check availability at the canonical platform')
    return key


# Short original hints explain approaches; no third-party statements/editorials are copied.
question(1480,'Running Sum of 1D Array','running-sum-of-1d-array',['arrays','prefix-sums'],
    'Write the total after each position.', 'The next total reuses the previous one.', 'Scan left to right, add the current value, and record the running total.')
question(121,'Best Time to Buy and Sell Stock','best-time-to-buy-and-sell-stock',['arrays'],
    'A sale must come after its purchase.', 'Remember the lowest earlier price.', 'Track the minimum price seen and the best later-price difference; retain zero if no profitable trade exists.')
question(14,'Longest Common Prefix','longest-common-prefix',['strings','arrays'],
    'Compare the same position across strings.', 'Stop at a mismatch or the shortest length.', 'Scan characters of the first string while every other string matches; return the matched prefix.')
question(28,'Find the Index of the First Occurrence in a String','find-the-index-of-the-first-occurrence-in-a-string',['strings'],
    'Try each possible starting position.', 'A mismatch rules out that start, not every later start.', 'Use a bounded nested comparison as the introductory solution; separate this baseline from later KMP optimization.')
question(217,'Contains Duplicate','contains-duplicate',['hashing','arrays'],
    'What must you remember from earlier positions?', 'A set stores membership without storing counts.', 'Scan once and return when insertion finds an already present value; otherwise no duplicate exists.')
question(1,'Two Sum','two-sum',['hashing','arrays'],
    'For a value x, which partner completes the target?', 'Look for target-x among earlier positions.', 'Check a value-to-index map before inserting the current index, so an element cannot pair with itself.')
question(88,'Merge Sorted Array','merge-sorted-array',['sorting','two-pointers','arrays'],
    'Writing at the front can overwrite unread values.', 'The spare slots are at the back.', 'Compare the largest remaining values and fill the destination backwards, then copy any remaining second-array values.')
question(912,'Sort an Array','sort-an-array',['sorting','recursion'],
    'Separate ordering into smaller ordered pieces.', 'Merge two sorted halves with two cursors.', 'Implement merge sort with a reusable temporary buffer; prove the merge invariant and include the O(n log n) total work.')
question(303,'Range Sum Query - Immutable','range-sum-query-immutable',['prefix-sums','arrays'],
    'Repeated queries should reuse preprocessing.', 'Store a zero before the first value.', 'Build exclusive prefixes and convert the problem’s inclusive right endpoint to prefix[right+1]-prefix[left].')
question(560,'Subarray Sum Equals K','subarray-sum-equals-k',['prefix-sums','hashing'],
    'Write a subarray sum as a difference of prefixes.', 'Count earlier prefixes equal to currentPrefix-k.', 'Seed prefix frequency zero with one occurrence; query before incrementing the current prefix frequency. This handles negative values.')
question(125,'Valid Palindrome','valid-palindrome',['strings','two-pointers'],
    'Only relevant characters need comparison.', 'Skip non-alphanumeric characters at either end.', 'Move opposing cursors inward, compare normalized characters and stop at the first mismatch under the statement’s character rules.')
question(167,'Two Sum II - Input Array Is Sorted','two-sum-ii-input-array-is-sorted',['two-pointers','sorting'],
    'Use the ordering instead of trying every pair.', 'A small sum needs a larger left value.', 'Compare endpoint sums and move exactly the cursor justified by the comparison; convert indices to the required output convention.')
question(643,'Maximum Average Subarray I','maximum-average-subarray-i',['fixed-window','arrays'],
    'Every candidate contains the same number of values.', 'Maximizing average is equivalent to maximizing its fixed-size sum.', 'Maintain the k-value sum and best sum, then divide by k using floating-point arithmetic.')
question(3,'Longest Substring Without Repeating Characters','longest-substring-without-repeating-characters',['variable-window','hashing','strings'],
    'A valid frame contains each character at most once.', 'Shrink until the incoming character is absent.', 'Maintain a set or latest-position map and update the longest valid contiguous length after restoring the invariant.')
question(209,'Minimum Size Subarray Sum','minimum-size-subarray-sum',['variable-window','arrays'],
    'The positivity constraint makes sums grow when extending.', 'Once valid, shrink while the target remains satisfied.', 'Extend right and repeatedly remove left values while sum>=target, recording minimum length; return the stated no-solution result.')
question(704,'Binary Search','binary-search',['binary-search','sorting'],
    'Which half can contain the target?', 'Every comparison must shrink the interval.', 'Use inclusive low/high boundaries and mid±1 updates; return an index on equality or -1 when the interval empties.')
question(35,'Search Insert Position','search-insert-position',['binary-search','sorting'],
    'Find the first position whose value is at least target.', 'Keep a boundary even when equality is not found.', 'Use a lower-bound search over [low,high); the final boundary is the insertion position and may equal the length.')
question(56,'Merge Intervals','merge-intervals',['intervals','sorting'],
    'Unordered starts obscure which segment comes next.', 'After sorting, only the latest merged interval can overlap.', 'Sort by start, extend the current end for overlaps and append a new segment for disjoint intervals; state endpoint rules.')
question(57,'Insert Interval','insert-interval',['intervals','arrays'],
    'The input is already sorted and disjoint.', 'There are before, overlapping and after regions.', 'Copy intervals strictly before the new one, merge the overlapping range, then append the untouched suffix.')
question(867,'Transpose Matrix','transpose-matrix',['matrices','arrays'],
    'A source row becomes a destination column.', 'The output dimensions must swap.', 'Allocate columns×rows output and copy input[r][c] to output[c][r]; test a rectangular example.')
question(54,'Spiral Matrix','spiral-matrix',['matrices','arrays'],
    'Track the unvisited rectangular boundaries.', 'Each side traversal consumes one boundary.', 'Walk top, right, bottom and left while shrinking bounds; recheck bounds before the final two sides to avoid duplicates.')
question(206,'Reverse Linked List','reverse-linked-list',['linked-lists','recursion'],
    'Preserve access to the suffix before changing an arrow.', 'Track previous, current and saved next.', 'Iteratively reverse one link at a time; later revisit recursively by reversing the suffix and reconnecting the former head.')
question(21,'Merge Two Sorted Lists','merge-two-sorted-lists',['linked-lists','sorting'],
    'The smaller head can be chosen permanently.', 'A dummy head simplifies the first append.', 'Advance the chosen list and tail, then attach the remaining suffix; maintain sorted output and do not create cycles.')
question(20,'Valid Parentheses','valid-parentheses',['stacks','strings'],
    'The latest unmatched opening must close first.', 'An unexpected closing bracket can fail immediately.', 'Push opening brackets; each closing bracket must match the current top. Accept only when the stack is empty at the end.')
question(155,'Min Stack','min-stack',['stacks'],
    'The minimum must recover after a pop.', 'Store the minimum at each depth, not just one global minimum.', 'Keep a parallel minimum stack or value/minimum pair so push, pop, top and minimum have constant-time state updates.')
question(933,'Number of Recent Calls','number-of-recent-calls',['queues'],
    'Calls older than the time window can be discarded.', 'Increasing timestamps put expired entries at the front.', 'Append the new timestamp, remove entries strictly older than the inclusive lower bound, and report queue size.')
question(232,'Implement Queue using Stacks','implement-queue-using-stacks',['queues','stacks'],
    'Moving a stack into another reverses its order.', 'Do not transfer while the output stack still has items.', 'Push to an input stack; refill the output stack only when empty. Each element transfers once, giving amortized O(1) operations.')
question(78,'Subsets','subsets',['backtracking','recursion'],
    'Each distinct input item has an include/exclude choice.', 'Undo a choice before visiting its sibling.', 'Explore both choices recursively and snapshot paths into output; include the empty subset and account for output size.')
question(39,'Combination Sum','combination-sum',['backtracking','recursion'],
    'Track the remaining target and the lowest allowed candidate index.', 'Reusing an index allows repeated use without reordered duplicates.', 'Explore candidates from a nondecreasing index, recurse with a reduced remainder and undo the choice; positive candidates justify pruning.')
question(104,'Maximum Depth of Binary Tree','maximum-depth-of-binary-tree',['binary-trees','recursion'],
    'What depth should an empty subtree return?', 'Combine two already solved child depths.', 'Return zero for null and one plus the larger child depth otherwise; specify that depth counts nodes.')
question(94,'Binary Tree Inorder Traversal','binary-tree-inorder-traversal',['binary-trees','recursion','stacks'],
    'Place the node visit between its child traversals.', 'A stack can hold the deferred ancestors.', 'Traverse left, visit node, traverse right; implement recursively first, then an explicit stack as an extension.')
question(700,'Search in a Binary Search Tree','search-in-a-binary-search-tree',['bst','binary-search'],
    'Compare target to the current key.', 'One whole subtree is impossible after each comparison.', 'Follow left for smaller targets and right for larger ones, returning the matching node or null; cost depends on height.')
question(98,'Validate Binary Search Tree','validate-binary-search-tree',['bst','binary-trees','recursion'],
    'Immediate child comparisons do not constrain all descendants.', 'Carry strict lower and upper bounds down the tree.', 'Each key must lie inside its inherited bounds; narrow the upper bound on the left and lower bound on the right, using safe bound types.')
question(703,'Kth Largest Element in a Stream','kth-largest-element-in-a-stream',['heaps','arrays'],
    'You only need to retain the k largest values so far.', 'The smallest retained value is the kth largest.', 'Maintain a min-heap of at most k values, remove its minimum when oversized and report the root under the API’s input guarantees.')
question(1046,'Last Stone Weight','last-stone-weight',['heaps'],
    'Each round needs the two current largest values.', 'Sorting from scratch repeats work.', 'Use a max-heap, remove two largest weights and insert their nonzero difference; return zero for an empty result.')
question(1791,'Find Center of Star Graph','find-center-of-star-graph',['graphs'],
    'Use the promise that this graph is a star.', 'The first two edges already share the centre.', 'Return their common endpoint; also explain the degree-counting representation-based solution and why the star guarantee is essential.')
question(102,'Binary Tree Level Order Traversal','binary-tree-level-order-traversal',['bfs','binary-trees','queues'],
    'The queue orders nodes by discovery depth.', 'Capture the current queue size before processing a level.', 'Process exactly that many nodes into one output row and enqueue their children for the next row; handle a null root.')
question(994,'Rotting Oranges','rotting-oranges',['bfs','matrices','queues'],
    'All initially rotten cells are simultaneous sources.', 'A BFS layer represents one minute, not one cell.', 'Queue all sources, mark fresh neighbours when enqueued, track minutes by layers and detect fresh cells left unreachable.')
question(200,'Number of Islands','number-of-islands',['dfs','graphs','matrices'],
    'One traversal consumes one connected land component.', 'Start a traversal only at unvisited land.', 'Scan the grid; each new land seed increments the count and floods its four-neighbour component using DFS or BFS.')
question(733,'Flood Fill','flood-fill',['dfs','matrices'],
    'Only the starting colour’s connected component changes.', 'If the replacement equals the starting colour, return early.', 'Visit matching four-neighbour cells and mark them before exploring neighbours; preserve disconnected matching regions.')
question(70,'Climbing Stairs','climbing-stairs',['dynamic-programming'],
    'Define a state as the number of routes to a step.', 'The final move comes from one or two steps below.', 'Use ways[0]=1 and the appropriate first-step base, then sum predecessor counts; explain why this differs from Fibonacci’s state interpretation.')
question(198,'House Robber','house-robber',['dynamic-programming','arrays'],
    'Define best for a prefix of houses.', 'For the last house, either skip it or take it and skip its neighbour.', 'Use best[i]=max(best[i-1], value[i-1]+best[i-2]) with empty-prefix base zero; optionally roll two previous results.')


def original(key, title, tags, hints, outline, local_problem=None):
    QUESTIONS[key] = dict(id=key, kind='local-problem-reference' if local_problem else 'original-exercise',
        platform='1on1', title=title, canonicalUrl=None, conceptTags=['concept-'+x for x in tags],
        progressiveHints=hints, approachOutline=outline,
        provenance=dict(sourceIds=['1on1-original'], selectionBasis='Original teaching exercise; no company attribution.'),
        implementationStatus='existing' if local_problem else 'planned-phase-2', localProblemId=local_problem)


original('original-operation-counts','Count Loop Operations',['complexity'],
    ['Choose exactly which operation is counted.','Count a single pass, then all ordered index pairs.','For n=8 the two counters are 8 and 64.'],
    'Derive n and n² body counts and separate those counts from measured machine time.')
original('original-growth-comparison','Compare Linear and Halving Growth',['complexity'],
    ['Write the visited halving values.','Compare n=8 and n=16.','Halving iterations rise from 4 to 5 while a full scan doubles.'],
    'Track integer halving until zero; explain the logarithmic count including its boundary case n=0.')
original('original-recursive-sum','Recursive Array Sum',['recursion','arrays'],
    ['What is the sum of an empty suffix?','Advance the index to reduce the remaining problem.','Return a[i]+sumFrom(a,i+1), with zero at i==length.'],
    'Use one stack frame per remaining element, showing both returned sum and O(n) stack use.')
original('original-adjacency-list','Build an Adjacency List',['graphs'],
    ['Allocate a row for every vertex.','Add each directed edge to its source row.','Keep isolated vertices, self loops and parallel edges visible.'],
    'Construct outgoing lists, validate vertex identifiers, then demonstrate how an undirected representation adds reverse entries.')
original('original-window-sum','Three-reading window',['fixed-window','arrays'],
    ['Adjacent windows share k-1 readings.','Subtract the outgoing reading and add the incoming reading.','Compare full windows only; initialize below all valid sums.'],
    'For this existing problem k=3: reuse a three-value sum and keep the largest full-window result, including all-negative inputs.', 'problem-three-window')

APPLICATIONS = [
    ['original-operation-counts','original-growth-comparison'], ['leetcode-1480','leetcode-121'],
    ['leetcode-14','leetcode-28'], ['leetcode-217','leetcode-1'], ['leetcode-88','leetcode-912'],
    ['leetcode-303','leetcode-560'], ['leetcode-125','leetcode-167'], ['leetcode-643','original-window-sum'],
    ['leetcode-3','leetcode-209'], ['leetcode-704','leetcode-35'], ['leetcode-56','leetcode-57'],
    ['leetcode-867','leetcode-54'], ['leetcode-206','leetcode-21'], ['leetcode-20','leetcode-155'],
    ['leetcode-933','leetcode-232'], ['original-recursive-sum','leetcode-206'], ['leetcode-78','leetcode-39'],
    ['leetcode-104','leetcode-94'], ['leetcode-700','leetcode-98'], ['leetcode-703','leetcode-1046'],
    ['original-adjacency-list','leetcode-1791'], ['leetcode-102','leetcode-994'], ['leetcode-200','leetcode-733'],
    ['leetcode-70','leetcode-198'],
]

# Each application explains its transfer, rather than implying all topic tags are prerequisites.
CONNECTIONS = [
    ['Apply counters to actual loop bodies.','Change input scale and compare growth.'],
    ['Record the sum at every position.','Replace a total with a minimum-so-far decision.'],
    ['Compare the same character position across strings.','Extend traversal to matching a candidate substring.'],
    ['Use membership to detect repetition.','Associate each earlier value with its index.'],
    ['Merge while preserving unread input.','Combine merging with recursive divide-and-conquer.'],
    ['Reuse preprocessing across range queries.','Combine prefix differences with hash-map counts.'],
    ['Move inward while applying text normalization.','Use sorted sums to discard pairs.'],
    ['Convert a best fixed-length sum into an average.','Use the existing original numeric-window problem.'],
    ['Maintain distinct characters with a membership structure.','Use positive values to justify sum-based shrinking.'],
    ['Find an exact target.','Return the first valid insertion boundary.'],
    ['Merge overlaps after ordering starts.','Exploit an already ordered disjoint collection.'],
    ['Swap coordinate roles.','Maintain four changing traversal boundaries.'],
    ['Reverse arrows iteratively.','Combine node references with merging.'],
    ['Match the most recent unfinished opening.','Attach a minimum summary to each depth.'],
    ['Discard expired timestamps from the front.','Compose FIFO behavior from two LIFO structures.'],
    ['Replace a loop with a base case and smaller suffix.','Revisit reversal recursively; compare extra stack use.'],
    ['Enumerate include/exclude choices.','Add a target, candidate reuse and duplicate-order control.'],
    ['Combine child results into a depth.','Choose the visit position relative to children.'],
    ['Discard one subtree after each comparison.','Propagate ancestor bounds to every descendant.'],
    ['Use a min-heap to retain the k largest stream values.','Use a max-heap for repeated largest-pair removal.'],
    ['Translate edges into a concrete representation.','Exploit a promised star structure and compare degree counts.'],
    ['Reuse FIFO for nodes grouped by depth.','Use simultaneous grid sources and layer-based minutes.'],
    ['Count components across a full grid scan.','Recolour only the start component with early visited marking.'],
    ['Derive route-count states and correct bases.','Derive maximum-value prefix states with take/skip choices.'],
]

EXTRA = {(5,1):['recursion'], (6,1):['hashing'], (22,0):['binary-trees']}
for c, question_ids, connections in zip(CONCEPTS, APPLICATIONS, CONNECTIONS):
    for i, (qid, connection) in enumerate(zip(question_ids, connections)):
        c['applications'].append(dict(questionId=qid, role='introduction' if i == 0 else 'transfer',
            connection=connection, additionalPrerequisites=['concept-'+x for x in EXTRA.get((c['order'],i),[])],
            perspective='recursive reversal' if c['order']==16 and qid=='leetcode-206' else 'primary application'))

SOURCES = [
    dict(id='handbook', url='https://www.techinterviewhandbook.org/algorithms/study-cheatsheet/', retrievedAt='2026-11-16', use='Concept coverage, constraints and edge cases.'),
    dict(id='grind75', url='https://www.techinterviewhandbook.org/grind75/faq', retrievedAt='2026-11-16', use='Pattern progression; prerequisite knowledge before mixed practice.'),
    dict(id='company-csv', url='https://github.com/liquidslr/leetcode-company-wise-problems',
         fileUrl='https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/main/Amazon/5.%20All.csv',
         revision=None, retrievedAt='2026-11-16', snapshotDate=None,
         dateNote='README states 2025-06-01; repository About states 2025-10-20. Freshness is ambiguous.',
         use='Inspected title/topic metadata as a supporting relevance signal. No frequency aggregation or employer verification.'),
    dict(id='company-2026', url='https://github.com/snehasishroy/leetcode-companywise-interview-questions',
         fileUrl='https://raw.githubusercontent.com/snehasishroy/leetcode-companywise-interview-questions/master/amazon/all.csv',
         revision=None, snapshotDate='2026-07-12', retrievedAt='2026-11-16',
         use='Secondary inspected schema/snapshot; no assumption of independent frequency evidence.'),
    dict(id='leetcode-canonical', url='https://leetcode.com/problemset/', retrievedAt='2026-11-16',
         use='Canonical external question IDs/links; availability checked by learner at source; not a statement import.'),
    dict(id='1on1-original', url=None, retrievedAt='2026-11-16', use='Original authored teaching exercises and existing local problem.')
]

provenance = json.loads((ROOT/'scripts/curriculum_provenance.json').read_text(encoding='utf-8'))
for source in SOURCES:
    observed = next((s for s in provenance['sources'] if s['id']==source['id']), None)
    if observed: source.update(observed)
for qid, observations in provenance['observations'].items():
    QUESTIONS[qid]['provenance']['companyObservations'] = observations
    QUESTIONS[qid]['provenance']['sourceIds'].append('company-2026')

hashing = next(c for c in CONCEPTS if c['id']=='concept-hashing')
hashing['java']['implementation'] += '''
static Map<Integer,Integer> frequencies(int[] a) {
    Map<Integer,Integer> counts=new LinkedHashMap<>();
    for(int value:a) counts.merge(value,1,Integer::sum);
    return counts;
}'''
hashing['java']['cases'] += [dict(expression='frequencies(new int[]{2,1,2})',expected='{2=2, 1=1}'),
                           dict(expression='frequencies(new int[]{})',expected='{}')]
queues = next(c for c in CONCEPTS if c['id']=='concept-queues')
queues['java']['implementation'] += '''
static List<Integer> bothEnds() {
    Deque<Integer> deque=new ArrayDeque<>();
    deque.addLast(2); deque.addFirst(1);
    return List.of(deque.removeFirst(),deque.removeLast());
}'''
queues['java']['cases'].append(dict(expression='bothEnds()',expected='[1, 2]'))
for c in CONCEPTS:
    c['java']['source']='import java.util.*;\nclass CurriculumExample {\n'+c['java']['implementation']+'\n}'

ANNOTATIONS = [
    ('for (int x = n;', 'Each halving iteration reduces the remaining scale; contrast its count with the two earlier loops.'),
    ('total += a[i]', 'Consume one slot; the accumulator now includes that slot.'),
    ('out.append(s.charAt(i))', 'Append the highlighted source character; the original string stays unchanged.'),
    ('!seen.add(value)', 'A failed insertion means exact membership was already present.'),
    ('while (i < a.length && j < b.length)', 'Compare the two current fronts; advance only the cursor whose value was emitted.'),
    ('p[i + 1] = p[i] + a[i]', 'The next boundary stores the previous prefix plus one new input value.'),
    ('if (sum < target) left++; else right--', 'Move the cursor justified by sorted order and the comparison.'),
    ('sum -= a[right - k]', 'Remove the outgoing value once the frame would exceed k elements.'),
    ('while (window.contains(incoming))', 'Restore validity by removing as many left values as needed.'),
    ('if (a[mid] < target)', 'Discard mid along with the impossible half, guaranteeing progress.'),
    ('out.get(out.size()-1)[1] = Math.max', 'Extend the latest merged end; preserve earlier disjoint output.'),
    ('out[c][r] = a[r][c]', 'Move one value to the swapped row/column coordinates.'),
    ('current.next = prev', 'Rewire the current node after saving its original successor.'),
    ('out.add(stack.pop())', 'Remove the newest remaining value from the top.'),
    ('out.add(queue.removeFirst())', 'Remove the earliest queued value from the front.'),
    ('return n * factorial(n - 1)', 'Suspend this frame, then multiply by its own n when the smaller call returns.'),
    ('path.remove(path.size() - 1)', 'Undo the last choice so the next sibling receives the parent path.'),
    ('walk(node.left, out); out.add(node.value);', 'Return from the left subtree, then visit the node before descending right.'),
    ('if (value < node.value)', 'Compare with this node and descend into the only possible insertion subtree.'),
    ('Collections.swap(h,parent,i)', 'Move a newly inserted value up one level while preserving the other heap entries.'),
    ('graph.get(e[0]).add(e[1])', 'Add one directed outgoing neighbour without losing isolated rows.'),
    ('distance[v]=distance[u]+1; queue.addLast(v)', 'Record discovery and distance before enqueueing, preventing duplicate queue entries.'),
    ('if(!seen[v]) explore', 'Suspend this frame and fully explore one unvisited neighbour before trying the next.'),
    ('dp[i]=dp[i-1]+dp[i-2]', 'Read two final dependencies and store the destination state exactly once.'),
]
for c, (anchor, explanation) in zip(CONCEPTS, ANNOTATIONS):
    lines=c['java']['implementation'].splitlines()
    c['java']['lineAnnotations']=[dict(line=next(i+1 for i,line in enumerate(lines) if anchor in line), explanation=explanation)]

for slug, expression in [('complexity','counts(-1)'),('fixed-window','bestWindow(new int[]{},0)'),
                          ('matrices','transpose(new int[][]{{1},{2,3}})'),('recursion','factorial(-1)'),
                          ('prefix-sums','range(prefix(new int[]{1}),0,2)')]:
    next(c for c in CONCEPTS if c['id']=='concept-'+slug)['java']['cases'].append(
        dict(expression=expression, expectedException='IllegalArgumentException'))

ADVANCED = [
    ('avl','AVL Trees',['bst']), ('trie','Tries',['hashing','strings']),
    ('dijkstra',"Dijkstra's Algorithm",['bfs','heaps']), ('max-flow','Maximum Flow: Edmonds–Karp',['bfs']),
    ('set-cover','Greedy Set Cover',['hashing']), ('quickselect','Randomized Quickselect',['sorting']),
    ('bloom-filter','Bloom Filters',['hashing']),
]


def manifest():
    return dict(version=1, title='1on1 Core Curriculum', conceptCount=24,
        flow=['visual-concept','minimal-java','question-applications'],
        sources=SOURCES, concepts=CONCEPTS, questions=list(QUESTIONS.values()),
        advancedBranch=[dict(lessonId='lesson-'+slug,title=title,prerequisites=['concept-'+x for x in deps]) for slug,title,deps in ADVANCED],
        delivery=dict(skillTreeUi='decision-after-curriculum-review', practice='phase-2', uiUx='phase-2'))


def apply(lessons, paths):
    """Add metadata/content without changing original problem IDs or challenge gold."""
    by_id = {lesson['id']: lesson for lesson in lessons}
    for c in CONCEPTS:
        primary = c['lessonIds'][0]
        if primary not in by_id:
            lesson = dict(id=primary, kind='lesson', published=True, minutes=12, difficulty='Foundations',
                body=c['mentalModel'], invariant=c['invariant'], pitfall=c['commonMistake'],
                timeComplexity=c['complexity']['time'], spaceComplexity=c['complexity']['space'],
                code=c['java']['implementation'].splitlines(), checkpoint=c['checkpoint'], linkedProblems=[])
            lessons.append(lesson); by_id[primary] = lesson
        for offset, lid in enumerate(c['lessonIds']):
            lesson = by_id[lid]
            child = {'lesson-merge-sort':'Merge Sort','lesson-quick-sort':'Quicksort',
                     'lesson-memoization':'Memoization','lesson-tabulation':'Tabulation'}.get(lid)
            lesson.update(title=child or c['title'], subtitle=child or c['title'],
                conceptId=c['id'], curriculumOrder=c['order'], branch='core',
                order=c['order']*10+offset,
                prerequisites=[next(x for x in CONCEPTS if x['id']==dep)['lessonIds'][0] for dep in c['prerequisites']],
                objectives=c['objectives'], teaching=c,
                contentStatus='authored', interactiveStatus='existing-limited' if lesson.get('experiment') else 'specification-only')
            # Child lessons retain distinct explanations and existing graded/reference journeys.
            if len(c['lessonIds']) == 1 and not lesson.get('referenceJourney'):
                lesson.update(body=c['mentalModel'], invariant=c['invariant'], pitfall=c['commonMistake'],
                    timeComplexity=c['complexity']['time'], spaceComplexity=c['complexity']['space'], checkpoint=c['checkpoint'])
            lesson['topics'] = list(dict.fromkeys([c['title']] + lesson.get('topics', [])))
            if not lesson.get('blocks'):
                lesson['blocks'] = [dict(id='worked', kind='explanation', title='Worked example', text=c['workedExample'], lines=[])]
        scene = by_id[primary].get('experiment')
        c['visualization'].update(interactiveStatus='existing-limited' if scene else 'specification-only',
            scene=scene, gaps=visual_gaps(c['id']))
    for index, (slug, title, deps) in enumerate(ADVANCED):
        lesson = by_id['lesson-'+slug]
        lesson.update(title=title, subtitle=title, branch='advanced', order=300+index,
            prerequisites=[next(x for x in CONCEPTS if x['id']=='concept-'+dep)['lessonIds'][0] for dep in deps])
    for order, lesson in enumerate(sorted(lessons,key=lambda lesson:lesson['order']),1):
        lesson['order']=order
    # Accurate DFS entry/return code for the corrected recursive teaching trace.
    by_id['lesson-dfs']['code'] = ['void dfs(int u) { seen[u] = true;',
        '  for (int v : neighbours[u]) {', '    if (!seen[v]) dfs(v);', '  }', '} // return to the parent frame']
    for path in paths:
        if path['id']=='path-foundations':
            path.update(title='DSA Foundations', description='Core concepts in prerequisite order: visual model, Java code, then applications.',
                lessons=[lid for c in CONCEPTS for lid in c['lessonIds']])
        elif path['id']=='path-core':
            path.update(title='Interview Patterns', description='Revisit core concepts through overlapping patterns; selected practice is planned for Phase 2.',
                lessons=[c['lessonIds'][0] for c in CONCEPTS if c['order'] in [4,6,7,8,9,10,11,13,14,17,18,19,20,22,23,24]])
        elif path['id']=='path-interview':
            path.update(title='Advanced Algorithms', description='Course applications in indexing, balancing, flow, approximation and randomization.',
                lessons=['lesson-'+x[0] for x in ADVANCED])
    return manifest()


def visual_gaps(cid):
    gaps = {
        'concept-sorting':['Current child traces cover whole sorting, not the two-run merge lesson input. Splits and per-merge cursor moves need refinement.'],
        'concept-linked-lists':['Java links preserve identity; the legacy renderer still needs to display every rewired arrow.'],
        'concept-recursion':['Base frame and returned values need a dedicated frame view; existing authored trace is not own-code tracing.'],
        'concept-backtracking':['Existing bounded trace records choices; branch-tree layout and undo transitions need refinement.'],
        'concept-binary-trees':['Existing child renderer uses BST insertion and level-order traversal. It cannot accept arbitrary binary trees or demonstrate the specified inorder traversal yet.'],
        'concept-heaps':['Trace shows completed insertions; capture/render every sift comparison and swap plus extraction before claiming full heap coverage.'],
        'concept-bfs':['Generated graph only; explicit graphs, cycles, disconnected vertices and multi-source grid input need renderer/input expansion.', 'The current trace records processing order; shortest-edge distances are verified in the Java example but are not yet displayed per vertex.'],
        'concept-dfs':['Generated graph only; explicit graphs and a visible call-frame stack remain Phase 2 work.'],
        'concept-dynamic-programming':['Fibonacci is supported; staircase and take/skip practice require their own state explanations and future interactive scenes.'],
        'concept-two-pointers':['Numeric sorted-pair trace only; string normalization and palindrome visuals are not implemented.'],
        'concept-queues':['FIFO is supported; deque operations at both ends and the two-stack implementation are specifications only.'],
        'concept-stacks':['Push/pop trace exists; bracket matching and per-depth minimum visuals remain future applications.'],
    }
    if cid in gaps: return gaps[cid]
    if cid in ['concept-fixed-window','concept-binary-search','concept-bst']:
        return ['Existing bounded scene supports the teaching operation; broader problem-specific visuals remain Phase 2.']
    return ['No matching interactive scene exists yet. Show the authored state sequence and Java code; do not substitute another algorithm.']


def write_artifacts(data):
    output=ROOT/'backend/src/main/resources/curriculum.json'
    output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# 1on1 — core curriculum', '',
        'Generated from the original authoring source in `scripts/curriculum_content.py`. Version 1. '
        '24 concepts; visual concept → minimal Java → 1–2 applications. The skill-tree interface is undecided; practice and UI/UX are Phase 2.', '',
        f'{len(data["questions"])} canonical question records serve 48 concept associations. '
        'Question references are planning metadata, not imported statements or new in-app grading integrations.', '',
        '## Source selection', '',
        'Topic coverage comes from Tech Interview Handbook; progression from Grind 75; inspected company CSV metadata is a secondary signal. '
        'No frequency is represented as interview probability. Reuse rights for third-party statements are not established, so those statements are not copied.', '']
    for source in SOURCES:
        if source['url']: lines.append(f'- [{source["id"]}]({source["url"]}): {source["use"]}')
    for c in data['concepts']:
        lines += ['',f'## {c["order"]}. {c["title"]}', '', '**Objectives:** '+ ' '.join(c['objectives']), '',
            '**Prerequisites:** '+(', '.join(c['prerequisites']) or 'Basic programming'), '',
            '### Visual concept', '',c['mentalModel'],'',c['workedExample'],'',
            '**Invariant:** '+c['invariant'],'', '**Watch out:** '+c['commonMistake'],'',
            '**Visual specification:** '+c['visualization']['exampleInput'],'',
            ' → '.join(c['visualization']['expectedStates']),'',
            '**Manipulation:** '+c['visualization']['manipulation'],'',
            '**Limits:** '+c['visualization']['limits'],'',
            '**Interactive readiness:** '+c['visualization']['interactiveStatus'], '']
        lines += ['- '+gap for gap in c['visualization']['gaps']]
        lines += ['', '### Minimal Java', '', '```java', c['java']['implementation'],'```','',
            '**Time:** '+c['complexity']['time']+'. **Space:** '+c['complexity']['space']+'.', '',
            '**Assumptions:** '+c['complexity']['assumptions'],'',
            '**Prediction:** '+c['checkpoint']['question'],'', '### Question applications — Phase 2', '']
        for annotation in c['java']['lineAnnotations']:
            lines += [f'Code line {annotation["line"]}: {annotation["explanation"]}', '']
        for app in c['applications']:
            q=QUESTIONS[app['questionId']]
            label=f'[{q["title"]}]({q["canonicalUrl"]})' if q['canonicalUrl'] else q['title']+' (original)'
            lines += [f'**{app["role"].title()}: {label}.** '+app['connection'], '',
                'Additional prerequisites: '+(', '.join(app['additionalPrerequisites']) or 'None beyond the concept sequence')+'.', '',
                'Progressive hints: '+ ' → '.join(q['progressiveHints']), '', 'Approach: '+q['approachOutline'], '']
    lines += ['## Phase 2 handover', '',
        '- Review the curriculum before deciding when to build the skill-tree interface. Use the manifest dependency graph; do not infer edges from display order.',
        '- Implement assigned practice progressively, preserving canonical question identity and the existing local problem catalogue.',
        '- Complete the recorded visualization gaps. Do not label specification-only concepts as fully interactive.',
        '- Refine layout, animation and mobile experience on top of stable lesson/challenge/trace contracts.',
        '- Retain old lessons, notes, progress and administrator edits. Keep advanced academic algorithms available outside the core path.',
        '- External question statements/editorials are not bundled; links are references and access can change.', '']
    (ROOT/'docs/CURRICULUM.md').write_text('\n'.join(lines),encoding='utf-8')

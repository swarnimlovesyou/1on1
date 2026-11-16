# 1on1 — core curriculum

Generated from the original authoring source in `scripts/curriculum_content.py`. Version 1. 24 concepts; visual concept → minimal Java → 1–2 applications. The skill-tree interface is undecided; practice and UI/UX are Phase 2.

47 canonical question records serve 48 concept associations. Question references are planning metadata, not imported statements or new in-app grading integrations.

## Source selection

Topic coverage comes from Tech Interview Handbook; progression from Grind 75; inspected company CSV metadata is a secondary signal. No frequency is represented as interview probability. Reuse rights for third-party statements are not established, so those statements are not copied.

- [handbook](https://www.techinterviewhandbook.org/algorithms/study-cheatsheet/): Concept coverage, constraints and edge cases.
- [grind75](https://www.techinterviewhandbook.org/grind75/faq): Pattern progression; prerequisite knowledge before mixed practice.
- [company-csv](https://github.com/liquidslr/leetcode-company-wise-problems): Inspected title/topic metadata as a supporting relevance signal. No frequency aggregation or employer verification.
- [company-2026](https://github.com/snehasishroy/leetcode-companywise-interview-questions): Secondary inspected schema/snapshot; no assumption of independent frequency evidence.
- [leetcode-canonical](https://leetcode.com/problemset/): Canonical external question IDs/links; availability checked by learner at source; not a statement import.

## 1. Time and Space Complexity

**Objectives:** Count repeated operations rather than guessing from syntax. Separate input storage, auxiliary space and output size.

**Prerequisites:** Basic programming

### Visual concept

Treat a loop as a counter of work. Doubling the input doubles a full scan, roughly quadruples a square nested loop, and adds about one iteration to repeated halving.

For n=8, a scan performs 8 visits, a square nested loop performs 64 visits, and repeated integer halving visits 8,4,2,1: 4 iterations. These counts describe the defined operations, not elapsed milliseconds.

**Invariant:** The operation counter increases once for each visit of the selected loop body.

**Watch out:** Two nested loops are not automatically quadratic: their bounds and dependencies determine the count. Big-O is a growth bound, not an exact runtime.

**Visual specification:** n=8

scan: 8 → square: 64 → halving: 8 → 4 → 2 → 1

**Manipulation:** Change n to 4 or 16 and predict the counters before comparing.

**Limits:** Nonnegative n; teaching counter only, not a runtime profiler.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static long[] counts(int n) {
        if (n < 0) throw new IllegalArgumentException("n must be nonnegative");
        long scan = 0, square = 0, halves = 0;
        for (int i = 0; i < n; i++) scan++;
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) square++;
        for (int x = n; x > 0; x /= 2) halves++;
        return new long[]{scan, square, halves};
    }
```

**Time:** O(n), O(n²), O(log n) for the three loops. **Space:** O(1) auxiliary.

**Assumptions:** n >= 0; counting loop-body visits, excluding printing.

**Prediction:** A square nested loop visits every pair for n=4. How many visits?

### Question applications — Phase 2

Code line 6: Each halving iteration reduces the remaining scale; contrast its count with the two earlier loops.

**Introduction: Count Loop Operations (original).** Apply counters to actual loop bodies.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Choose exactly which operation is counted. → Count a single pass, then all ordered index pairs. → For n=8 the two counters are 8 and 64.

Approach: Derive n and n² body counts and separate those counts from measured machine time.

**Transfer: Compare Linear and Halving Growth (original).** Change input scale and compare growth.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Write the visited halving values. → Compare n=8 and n=16. → Halving iterations rise from 4 to 5 while a full scan doubles.

Approach: Track integer halving until zero; explain the logarithmic count including its boundary case n=0.


## 2. Arrays

**Objectives:** Read and update by index. Traverse an array while maintaining a running result.

**Prerequisites:** concept-complexity

### Visual concept

An array is a numbered row of slots. Index i selects a position, not a value; duplicate values still occupy different slots.

For [2,1,5], visit indices 0,1,2. The running total becomes 2,3,8. An empty row has total 0.

**Invariant:** Before index i, total equals the sum of a[0..i).

**Watch out:** The last valid index is length-1. Iterating with i <= length reads beyond the array. Integer sums may overflow; use long for the accumulator.

**Visual specification:** [2,1,5]

i=0,total=2 → i=1,total=3 → i=2,total=8

**Manipulation:** Edit a slot or repeat a value; predict which intermediate sums change.

**Limits:** Empty to 32 integers; values have stable slot identities.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static long sum(int[] a) {
        long total = 0;
        for (int i = 0; i < a.length; i++) total += a[i];
        return total;
    }
```

**Time:** O(n). **Space:** O(1) auxiliary.

**Assumptions:** Non-null int array; sum accumulated in long.

**Prediction:** After visiting indices 0 and 1 of [2,1,5], what is total?

### Question applications — Phase 2

Code line 3: Consume one slot; the accumulator now includes that slot.

**Introduction: [Running Sum of 1D Array](https://leetcode.com/problems/running-sum-of-1d-array/).** Record the sum at every position.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Write the total after each position. → The next total reuses the previous one. → Scan left to right, add the current value, and record the running total.

Approach: Scan left to right, add the current value, and record the running total.

**Transfer: [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/).** Replace a total with a minimum-so-far decision.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: A sale must come after its purchase. → Remember the lowest earlier price. → Track the minimum price seen and the best later-price difference; retain zero if no profitable trade exists.

Approach: Track the minimum price seen and the best later-price difference; retain zero if no profitable trade exists.


## 3. Strings

**Objectives:** Traverse characters and distinguish positions from substrings. Build a result without repeatedly copying an immutable string.

**Prerequisites:** concept-arrays

### Visual concept

A string is an indexed sequence of text units. Reading does not mutate it; build changed text in a separate buffer.

Read "cat" from indices 2,1,0 and append t,a,c to produce "tac". The original string remains "cat".

**Invariant:** After k iterations, the buffer contains the final k characters in reverse order.

**Watch out:** Java char indexes UTF-16 code units, not all user-perceived characters. This introductory example is restricted to ASCII; it is not a Unicode grapheme reverser.

**Visual specification:** "cat"

read 2: t → read 1: ta → read 0: tac

**Manipulation:** Change the string and track source index separately from output length.

**Limits:** ASCII, 0–32 characters; Unicode expansion is separate.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static String reverse(String s) {
        StringBuilder out = new StringBuilder();
        for (int i = s.length() - 1; i >= 0; i--) out.append(s.charAt(i));
        return out.toString();
    }
```

**Time:** O(n). **Space:** O(n) output.

**Assumptions:** ASCII teaching input; StringBuilder avoids repeated string concatenation.

**Prediction:** After reading index 2 of "cat", what is in the output buffer?

### Question applications — Phase 2

Code line 3: Append the highlighted source character; the original string stays unchanged.

**Introduction: [Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/).** Compare the same character position across strings.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Compare the same position across strings. → Stop at a mismatch or the shortest length. → Scan characters of the first string while every other string matches; return the matched prefix.

Approach: Scan characters of the first string while every other string matches; return the matched prefix.

**Transfer: [Find the Index of the First Occurrence in a String](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/).** Extend traversal to matching a candidate substring.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Try each possible starting position. → A mismatch rules out that start, not every later start. → Use a bounded nested comparison as the introductory solution; separate this baseline from later KMP optimization.

Approach: Use a bounded nested comparison as the introductory solution; separate this baseline from later KMP optimization.


## 4. Hash Maps and Sets

**Objectives:** Use a set for exact membership and a map for key-associated state. Check previously seen values before inserting the current one.

**Prerequisites:** concept-arrays, concept-strings

### Visual concept

A set answers whether a value has appeared. A map additionally remembers a value such as the earlier index. Hashing locates a candidate bucket; equality still decides exact membership.

For [2,1,6,2,5], duplicate inserts 2, 1 and 6, then finds the second 2 already in seen and returns true. The animation runs frequencies on the same input instead: it keeps going, so 2 ends with count 2 and 1, 6 and 5 with count 1.

**Invariant:** Before reading position i, seen contains exactly the values at earlier positions.

**Watch out:** Hash lookup is expected constant time under normal assumptions, not a universal worst-case guarantee. A Bloom filter is not a replacement for an exact set.

**Visual specification:** [2,1,6,2,5]

2 inserted → 1 inserted → 6 is a different key: inserted → second 2 found: duplicate, count 2 → 5 inserted

**Manipulation:** Repeat a value, change it to a new value, and compare membership checks.

**Limits:** 0–32 integers; show exact key equality, not invented hash addresses.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static boolean duplicate(int[] a) {
        Set<Integer> seen = new HashSet<>();
        for (int value : a) if (!seen.add(value)) return true;
        return false;
    }
static Map<Integer,Integer> frequencies(int[] a) {
    Map<Integer,Integer> counts=new LinkedHashMap<>();
    for(int value:a) counts.merge(value,1,Integer::sum);
    return counts;
}
```

**Time:** Expected O(n). **Space:** O(n) auxiliary.

**Assumptions:** Java HashSet exact integer membership; expected hashing behaviour.

**Prediction:** Before processing the final 2 in [2,1,2], which values are in seen?

### Question applications — Phase 2

Code line 3: A failed insertion means exact membership was already present.

**Introduction: [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/).** Use membership to detect repetition.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: What must you remember from earlier positions? → A set stores membership without storing counts. → Scan once and return when insertion finds an already present value; otherwise no duplicate exists.

Approach: Scan once and return when insertion finds an already present value; otherwise no duplicate exists.

**Transfer: [Two Sum](https://leetcode.com/problems/two-sum/).** Associate each earlier value with its index.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: For a value x, which partner completes the target? → Look for target-x among earlier positions. → Check a value-to-index map before inserting the current index, so an element cannot pair with itself.

Approach: Check a value-to-index map before inserting the current index, so an element cannot pair with itself.


## 5. Sorting and Merging

**Objectives:** Merge two ordered sequences using two cursors. Explain how merge sort uses this operation after recursive splitting.

**Prerequisites:** concept-arrays

### Visual concept

Two sorted rows let you take the smaller front item each time. Once both fronts are ordered, the chosen value cannot be preceded by a smaller unconsumed value.

Merge [1,4] and [2,3]: choose 1,2,3, then drain 4. Output [1,2,3,4] is ordered and contains every input occurrence.

**Invariant:** The output prefix is sorted and contains exactly the consumed input prefixes.

**Watch out:** A merge assumes both inputs are sorted. Do not quote O(n) merging as the complexity of sorting arbitrary input. Choosing the left equal key preserves cross-run stability.

**Visual specification:** left=[1,4], right=[2,3]

out=[1] → out=[1,2] → out=[1,2,3] → out=[1,2,3,4]

**Manipulation:** Use duplicate keys and empty runs; keep element identity through merging.

**Limits:** Sorted runs of up to 16 elements each; splitting and pivot sorting are separate child traces.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static int[] merge(int[] a, int[] b) {
        int[] out = new int[a.length + b.length];
        int i = 0, j = 0, k = 0;
        while (i < a.length && j < b.length) out[k++] = a[i] <= b[j] ? a[i++] : b[j++];
        while (i < a.length) out[k++] = a[i++];
        while (j < b.length) out[k++] = b[j++];
        return out;
    }
```

**Time:** O(n+m) merge; O(n log n) merge sort. **Space:** O(n+m) merge output.

**Assumptions:** Both merge inputs are nondecreasing; merge-sort child lesson covers splitting.

**Prediction:** Merging [1,4] and [2,3], which value follows the first 1?

### Question applications — Phase 2

Code line 4: Compare the two current fronts; advance only the cursor whose value was emitted.

**Introduction: [Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/).** Merge while preserving unread input.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Writing at the front can overwrite unread values. → The spare slots are at the back. → Compare the largest remaining values and fill the destination backwards, then copy any remaining second-array values.

Approach: Compare the largest remaining values and fill the destination backwards, then copy any remaining second-array values.

**Transfer: [Sort an Array](https://leetcode.com/problems/sort-an-array/).** Combine merging with recursive divide-and-conquer.

Additional prerequisites: concept-recursion.

Progressive hints: Separate ordering into smaller ordered pieces. → Merge two sorted halves with two cursors. → Implement merge sort with a reusable temporary buffer; prove the merge invariant and include the O(n log n) total work.

Approach: Implement merge sort with a reusable temporary buffer; prove the merge invariant and include the O(n log n) total work.


## 6. Prefix Sums

**Objectives:** Build an exclusive-prefix table. Answer a half-open range sum using two stored values.

**Prerequisites:** concept-arrays

### Visual concept

Store the sum before every boundary. The sum between two boundaries is the later prefix minus the earlier prefix.

For [2,1,5], prefix=[0,2,3,8]. The range [1,3) sums to prefix[3]-prefix[1]=8-2=6.

**Invariant:** prefix[i] equals the sum of the first i values; prefix[0] is zero.

**Watch out:** Mixing inclusive and exclusive endpoints causes off-by-one errors. Prefix sums work with negative values; a positive-only shrinking window is a different technique.

**Visual specification:** a=[2,1,5], range=[1,3)

p=[0] → p=[0,2] → p=[0,2,3] → p=[0,2,3,8]; query=6

**Manipulation:** Move either query boundary and compare the highlighted original range.

**Limits:** 0–32 integers; half-open endpoints; long accumulation.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static long[] prefix(int[] a) {
        long[] p = new long[a.length + 1];
        for (int i = 0; i < a.length; i++) p[i + 1] = p[i] + a[i];
        return p;
    }
    static long range(long[] p, int left, int right) {
        if (left < 0 || left > right || right >= p.length) throw new IllegalArgumentException();
        return p[right] - p[left];
    }
```

**Time:** O(n) build; O(1) per range query. **Space:** O(n) table.

**Assumptions:** 0 <= left <= right <= n; long sums.

**Prediction:** For prefix=[0,2,3,8], which expression gives a[1..3)?

### Question applications — Phase 2

Code line 3: The next boundary stores the previous prefix plus one new input value.

**Introduction: [Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/).** Reuse preprocessing across range queries.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Repeated queries should reuse preprocessing. → Store a zero before the first value. → Build exclusive prefixes and convert the problem’s inclusive right endpoint to prefix[right+1]-prefix[left].

Approach: Build exclusive prefixes and convert the problem’s inclusive right endpoint to prefix[right+1]-prefix[left].

**Transfer: [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/).** Combine prefix differences with hash-map counts.

Additional prerequisites: concept-hashing.

Progressive hints: Write a subarray sum as a difference of prefixes. → Count earlier prefixes equal to currentPrefix-k. → Seed prefix frequency zero with one occurrence; query before incrementing the current prefix frequency. This handles negative values.

Approach: Seed prefix frequency zero with one occurrence; query before incrementing the current prefix frequency. This handles negative values.


## 7. Two Pointers

**Objectives:** Use ordering to discard impossible pairs. Move one pointer with a reason rather than enumerating every pair.

**Prerequisites:** concept-strings, concept-sorting

### Visual concept

Place a cursor at each end of a sorted row. If their sum is too small, moving the right cursor left cannot help; advance the left cursor instead.

Sorted [1,2,3,4,6,7], target=9: 1+7=8, so advance left. Then 2+7=9. The answer exists at two distinct positions.

**Invariant:** Any pair not yet ruled out lies within the current cursor interval.

**Watch out:** The ordering argument fails for unsorted input. Sort first when permitted and count that cost; sorted positions are not original indices.

**Visual specification:** sorted=[1,2,3,4,6,7], target=9

left=0,right=5,sum=8 → left=1,right=5,sum=9

**Manipulation:** Change target or repeat a value; distinguish sorted positions from original indices.

**Limits:** Sorted integers; distinct positions; preparation cost shown separately.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static boolean pair(int[] sorted, long target) {
        int left = 0, right = sorted.length - 1;
        while (left < right) {
            long sum = (long) sorted[left] + sorted[right];
            if (sum == target) return true;
            if (sum < target) left++; else right--;
        }
        return false;
    }
```

**Time:** O(n) search after sorting. **Space:** O(1) search auxiliary.

**Assumptions:** Input is already sorted; long pair sum avoids int overflow.

**Prediction:** At values 1 and 7 with target 9, which cursor moves?

### Question applications — Phase 2

Code line 6: Move the cursor justified by sorted order and the comparison.

**Introduction: [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/).** Move inward while applying text normalization.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Only relevant characters need comparison. → Skip non-alphanumeric characters at either end. → Move opposing cursors inward, compare normalized characters and stop at the first mismatch under the statement’s character rules.

Approach: Move opposing cursors inward, compare normalized characters and stop at the first mismatch under the statement’s character rules.

**Transfer: [Two Sum II - Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/).** Use sorted sums to discard pairs.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Use the ordering instead of trying every pair. → A small sum needs a larger left value. → Compare endpoint sums and move exactly the cursor justified by the comparison; convert indices to the required output convention.

Approach: Compare endpoint sums and move exactly the cursor justified by the comparison; convert indices to the required output convention.


## 8. Fixed-Size Sliding Window

**Objectives:** Reuse a fixed-length contiguous sum. Handle all-negative inputs and reject invalid window sizes.

**Prerequisites:** concept-arrays, concept-prefix-sums

### Visual concept

A frame holds k adjacent values. Move it right by subtracting the outgoing value and adding the incoming one.

For [2,1,5,1,3,2] and k=3, the full-window sums are 8,7,9,6. The largest is 9.

**Invariant:** The rolling sum equals the last min(k,right+1) values; compare with best only after a full window exists.

**Watch out:** Initializing best to zero breaks all-negative arrays. This fixed-size sum supports negative values; variable-size sum shrinking needs extra assumptions.

**Visual specification:** [2,1,5,1,3,2], k=3

[2,1,5]:8 → [1,5,1]:7 → [5,1,3]:9 → [1,3,2]:6

**Manipulation:** Edit input or k, then predict incoming/outgoing values.

**Limits:** 1–32 integers; 1 <= k <= n; existing interactive window trace.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static long bestWindow(int[] a, int k) {
        if (k < 1 || k > a.length) throw new IllegalArgumentException();
        long sum = 0, best = Long.MIN_VALUE;
        for (int right = 0; right < a.length; right++) {
            sum += a[right];
            if (right >= k) sum -= a[right - k];
            if (right >= k - 1) best = Math.max(best, sum);
        }
        return best;
    }
```

**Time:** O(n). **Space:** O(1) auxiliary.

**Assumptions:** 1 <= k <= n; long accumulated sums.

**Prediction:** A window sum of 8 loses 2 and gains 1. What is the next sum?

### Question applications — Phase 2

Code line 6: Remove the outgoing value once the frame would exceed k elements.

**Introduction: [Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/).** Convert a best fixed-length sum into an average.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Every candidate contains the same number of values. → Maximizing average is equivalent to maximizing its fixed-size sum. → Maintain the k-value sum and best sum, then divide by k using floating-point arithmetic.

Approach: Maintain the k-value sum and best sum, then divide by k using floating-point arithmetic.

**Transfer: Three-reading window (original).** Use the existing original numeric-window problem.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Adjacent windows share k-1 readings. → Subtract the outgoing reading and add the incoming reading. → Compare full windows only; initialize below all valid sums.

Approach: For this existing problem k=3: reuse a three-value sum and keep the largest full-window result, including all-negative inputs.


## 9. Variable-Size Sliding Window

**Objectives:** Grow and shrink a contiguous range to restore a condition. Separate a distinct-character condition from positive-sum conditions.

**Prerequisites:** concept-hashing, concept-fixed-window

### Visual concept

Stretch a frame while it remains valid. When a repeated character enters, remove characters from the left until the frame is valid again.

For "abba", the frame grows through a and ab. The second b forces both a and the old b out, leaving b. Then a enters to make ba, and the best length stays 2. One removal would not have been enough.

**Invariant:** After shrinking, all characters in the current frame are distinct.

**Watch out:** Removing only once can leave a repeated character inside the frame. For minimum-length sum windows, positivity is what makes shrinking monotonic; arbitrary negatives break that proof.

**Visual specification:** "abba"

[a],best=1 → [ab],best=2 → b repeats: remove a, then b; [b],best=2 → [ba],best=2

**Manipulation:** Try "abca" to see a removal that stops after one character.

**Limits:** ASCII 0–32 characters; no sum-window claims for negative numbers.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static int longestDistinct(String s) {
        Set<Character> window = new HashSet<>();
        int left = 0, best = 0;
        for (int right = 0; right < s.length(); right++) {
            char incoming = s.charAt(right);
            while (window.contains(incoming)) window.remove(s.charAt(left++));
            window.add(incoming);
            best = Math.max(best, right - left + 1);
        }
        return best;
    }
```

**Time:** Expected O(n). **Space:** O(min(n, alphabet size)).

**Assumptions:** ASCII example; each character enters/leaves at most once.

**Prediction:** When the second b arrives in "abba", is removing only the first a enough?

### Question applications — Phase 2

Code line 6: Restore validity by removing as many left values as needed.

**Introduction: [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/).** Maintain distinct characters with a membership structure.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: A valid frame contains each character at most once. → Shrink until the incoming character is absent. → Maintain a set or latest-position map and update the longest valid contiguous length after restoring the invariant.

Approach: Maintain a set or latest-position map and update the longest valid contiguous length after restoring the invariant.

**Transfer: [Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/).** Use positive values to justify sum-based shrinking.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: The positivity constraint makes sums grow when extending. → Once valid, shrink while the target remains satisfied. → Extend right and repeatedly remove left values while sum>=target, recording minimum length; return the stated no-solution result.

Approach: Extend right and repeatedly remove left values while sum>=target, recording minimum length; return the stated no-solution result.


## 10. Binary Search

**Objectives:** Maintain an inclusive candidate interval. Guarantee progress and distinguish exact search from insertion boundaries.

**Prerequisites:** concept-sorting

### Visual concept

A comparison with the middle of an ordered row discards a whole impossible half.

In [1,2,3,4,6,7], target 5: mid=2 gives 3, mid=4 gives 6, then mid=3 gives 4. The interval becomes empty and returns -1.

**Invariant:** If the target exists, some occurrence remains in [low,high].

**Watch out:** Using low=mid or high=mid in this inclusive version can stop progress. Exact-match search may return any duplicate occurrence; lower-bound search answers a different question.

**Visual specification:** sorted=[1,2,3,4,6,7], target=5

low=0,high=5,mid=2 → low=3,high=5,mid=4 → low=3,high=3,mid=3 → low=4,high=3: absent

**Manipulation:** Try present, absent and duplicated values; show sorting as preparation.

**Limits:** 0–32 sorted values; current trace accepts nonempty teaching input.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static int search(int[] a, int target) {
        int low = 0, high = a.length - 1;
        while (low <= high) {
            int mid = low + (high - low) / 2;
            if (a[mid] == target) return mid;
            if (a[mid] < target) low = mid + 1; else high = mid - 1;
        }
        return -1;
    }
```

**Time:** O(log n). **Space:** O(1) auxiliary.

**Assumptions:** Sorted nondecreasing array; mid uses low+(high-low)/2.

**Prediction:** If a[mid] is smaller than target, what is the new low in this version?

### Question applications — Phase 2

Code line 6: Discard mid along with the impossible half, guaranteeing progress.

**Introduction: [Binary Search](https://leetcode.com/problems/binary-search/).** Find an exact target.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Which half can contain the target? → Every comparison must shrink the interval. → Use inclusive low/high boundaries and mid±1 updates; return an index on equality or -1 when the interval empties.

Approach: Use inclusive low/high boundaries and mid±1 updates; return an index on equality or -1 when the interval empties.

**Transfer: [Search Insert Position](https://leetcode.com/problems/search-insert-position/).** Return the first valid insertion boundary.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Find the first position whose value is at least target. → Keep a boundary even when equality is not found. → Use a lower-bound search over [low,high); the final boundary is the insertion position and may equal the length.

Approach: Use a lower-bound search over [low,high); the final boundary is the insertion position and may equal the length.


## 11. Intervals

**Objectives:** Sort intervals by start and merge overlaps. State whether touching endpoints count as overlap.

**Prerequisites:** concept-sorting

### Visual concept

Lay closed segments on a number line. Sorted starts let you extend the latest output segment or begin a separate one.

For [1,3],[2,6],[8,10], the second segment overlaps the first and extends its end to 6. Result: [1,6],[8,10].

**Invariant:** Output segments are disjoint and cover exactly the processed input intervals.

**Watch out:** For closed intervals [1,2] and [2,3], equality means overlap. Half-open intervals need a different convention. Never mutate caller intervals accidentally while merging.

**Visual specification:** [1,3],[2,6],[8,10]

sort by start → extend [1,3] to [1,6] → append [8,10]

**Manipulation:** Move endpoints and compare touching, nested and disjoint segments.

**Limits:** 0–16 valid closed intervals; distinguish endpoint convention.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static int[][] mergeIntervals(int[][] input) {
        int[][] a = Arrays.stream(input).map(int[]::clone).toArray(int[][]::new);
        Arrays.sort(a, Comparator.comparingInt(x -> x[0]));
        List<int[]> out = new ArrayList<>();
        for (int[] next : a) {
            if (out.isEmpty() || out.get(out.size()-1)[1] < next[0]) out.add(next);
            else out.get(out.size()-1)[1] = Math.max(out.get(out.size()-1)[1], next[1]);
        }
        return out.toArray(int[][]::new);
    }
```

**Time:** O(n log n). **Space:** O(n) copy/output.

**Assumptions:** Valid closed [start,end] pairs; endpoints may touch; caller input preserved.

**Prediction:** With closed endpoints, do [1,2] and [2,3] merge?

### Question applications — Phase 2

Code line 7: Extend the latest merged end; preserve earlier disjoint output.

**Introduction: [Merge Intervals](https://leetcode.com/problems/merge-intervals/).** Merge overlaps after ordering starts.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Unordered starts obscure which segment comes next. → After sorting, only the latest merged interval can overlap. → Sort by start, extend the current end for overlaps and append a new segment for disjoint intervals; state endpoint rules.

Approach: Sort by start, extend the current end for overlaps and append a new segment for disjoint intervals; state endpoint rules.

**Transfer: [Insert Interval](https://leetcode.com/problems/insert-interval/).** Exploit an already ordered disjoint collection.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: The input is already sorted and disjoint. → There are before, overlapping and after regions. → Copy intervals strictly before the new one, merge the overlapping range, then append the untouched suffix.

Approach: Copy intervals strictly before the new one, merge the overlapping range, then append the untouched suffix.


## 12. Matrices and Grid Coordinates

**Objectives:** Distinguish row and column dimensions. Map a cell (r,c) to (c,r) during transpose.

**Prerequisites:** concept-arrays

### Visual concept

A rectangular matrix is a row of rows. Coordinates identify both a row and a column; a transpose swaps their roles.

Transpose [[1,2,3],[4,5,6]] into [[1,4],[2,5],[3,6]]. The input is 2×3 and the output is 3×2.

**Invariant:** Every copied source cell a[r][c] appears at out[c][r].

**Watch out:** Using row count for both dimensions only works for square inputs. Reject ragged rows for this rectangular operation.

**Visual specification:** [[1,2,3],[4,5,6]]

(0,0) → (0,0) → (0,1) → (1,0) → (1,2) → (2,1)

**Manipulation:** Use a non-square grid and follow one cell into the output.

**Limits:** Rectangular grid up to 6×6; ragged input explicitly invalid.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static int[][] transpose(int[][] a) {
        int rows = a.length, cols = rows == 0 ? 0 : a[0].length;
        for (int[] row : a) if (row.length != cols) throw new IllegalArgumentException("ragged matrix");
        int[][] out = new int[cols][rows];
        for (int r = 0; r < rows; r++) for (int c = 0; c < cols; c++) out[c][r] = a[r][c];
        return out;
    }
```

**Time:** O(rows × columns). **Space:** O(rows × columns) output.

**Assumptions:** Rectangular non-null rows; zero rows produce an empty matrix.

**Prediction:** Where does source cell (1,2) go during transpose?

### Question applications — Phase 2

Code line 5: Move one value to the swapped row/column coordinates.

**Introduction: [Transpose Matrix](https://leetcode.com/problems/transpose-matrix/).** Swap coordinate roles.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: A source row becomes a destination column. → The output dimensions must swap. → Allocate columns×rows output and copy input[r][c] to output[c][r]; test a rectangular example.

Approach: Allocate columns×rows output and copy input[r][c] to output[c][r]; test a rectangular example.

**Transfer: [Spiral Matrix](https://leetcode.com/problems/spiral-matrix/).** Maintain four changing traversal boundaries.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Track the unvisited rectangular boundaries. → Each side traversal consumes one boundary. → Walk top, right, bottom and left while shrinking bounds; recheck bounds before the final two sides to avoid duplicates.

Approach: Walk top, right, bottom and left while shrinking bounds; recheck bounds before the final two sides to avoid duplicates.


## 13. Linked Lists

**Objectives:** Follow node references rather than adjacent indexes. Reverse links without losing the unprocessed suffix.

**Prerequisites:** concept-arrays

### Visual concept

Each node holds a value and a reference to the next node. Move arrows, not values, when reversing the chain.

For 4→2→7→1→3→6, first save 2, point 4 to null, then continue from 2. The final head is 6 and the chain is 6→3→1→7→2→4.

**Invariant:** prev heads the reversed prefix; current heads the untouched suffix.

**Watch out:** Overwriting current.next before saving it loses access to the remaining nodes. Equal values still have distinct node identities.

**Visual specification:** 4→2→7→1→3→6

prev=null,current=4 → 4→null; current=2 → 2→4→null; current=7 → head=6: 6→3→1→7→2→4

**Manipulation:** Use duplicate values and track node IDs while reversing arrows.

**Limits:** Acyclic list; no cyclic-list claims; existing renderer needs arrow-state refinement.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static Node reverseList(Node current) {
        Node prev = null;
        while (current != null) {
            Node next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        return prev;
    }
    static class Node {
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
}
```

**Time:** O(n). **Space:** O(1) auxiliary.

**Assumptions:** Acyclic singly linked list; null is an empty list.

**Prediction:** What must be saved before overwriting current.next?

### Question applications — Phase 2

Code line 5: Rewire the current node after saving its original successor.

**Introduction: [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/).** Reverse arrows iteratively.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Preserve access to the suffix before changing an arrow. → Track previous, current and saved next. → Iteratively reverse one link at a time; later revisit recursively by reversing the suffix and reconnecting the former head.

Approach: Iteratively reverse one link at a time; later revisit recursively by reversing the suffix and reconnecting the former head.

**Transfer: [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/).** Combine node references with merging.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: The smaller head can be chosen permanently. → A dummy head simplifies the first append. → Advance the chosen list and tail, then attach the remaining suffix; maintain sorted output and do not create cycles.

Approach: Advance the chosen list and tail, then attach the remaining suffix; maintain sorted output and do not create cycles.


## 14. Stacks

**Objectives:** Use last-in, first-out operations. Handle an empty structure before removing an element.

**Prerequisites:** concept-arrays

### Visual concept

A stack is a pile with one accessible end. The last item placed on top is the first removed.

Push 4,2,7,1,3,6. Pop returns 6,3,1,7,2,4. Values below the top retain their relative order.

**Invariant:** The top is the most recently pushed item that has not been popped.

**Watch out:** A queue removes from the opposite end. Check emptiness before pop; use a Deque rather than treating sorted order as stack order.

**Visual specification:** push [4,2,7,1,3,6]

top=4 → top=6 after pushes → pop 6,3,1,7,2,4

**Manipulation:** Interleave pushes and pops; attempt a pop only after checking emptiness.

**Limits:** 0–32 values; top and empty state explicit.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static List<Integer> popOrder(int[] a) {
        Deque<Integer> stack = new ArrayDeque<>();
        for (int value : a) stack.push(value);
        List<Integer> out = new ArrayList<>();
        while (!stack.isEmpty()) out.add(stack.pop());
        return out;
    }
```

**Time:** O(n) for n pushes and pops; amortized O(1) per deque operation. **Space:** O(n) structure.

**Assumptions:** ArrayDeque used as an implementation, not an assessed algorithm replacement.

**Prediction:** Push 4, then 2, then 7. Which value pops first?

### Question applications — Phase 2

Code line 5: Remove the newest remaining value from the top.

**Introduction: [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/).** Match the most recent unfinished opening.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: The latest unmatched opening must close first. → An unexpected closing bracket can fail immediately. → Push opening brackets; each closing bracket must match the current top. Accept only when the stack is empty at the end.

Approach: Push opening brackets; each closing bracket must match the current top. Accept only when the stack is empty at the end.

**Transfer: [Min Stack](https://leetcode.com/problems/min-stack/).** Attach a minimum summary to each depth.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: The minimum must recover after a pop. → Store the minimum at each depth, not just one global minimum. → Keep a parallel minimum stack or value/minimum pair so push, pop, top and minimum have constant-time state updates.

Approach: Keep a parallel minimum stack or value/minimum pair so push, pop, top and minimum have constant-time state updates.


## 15. Queues and Deques

**Objectives:** Use first-in, first-out processing. Distinguish a queue discipline from a deque container.

**Prerequisites:** concept-arrays, concept-stacks

### Visual concept

Join at the back and leave from the front. A deque supports both ends, so the operations you choose determine FIFO or LIFO behavior.

Enqueue 4,2,7,1,3,6 at the back. Removing from the front returns 4,2,7,1,3,6.

**Invariant:** The front is the earliest enqueued item that has not been removed.

**Watch out:** Using removeLast after addLast turns a deque into a stack. BFS depends on FIFO; substituting the wrong removal changes exploration order.

**Visual specification:** enqueue [4,2,7,1,3,6]

front=4 → back=6 after enqueues → dequeue 4,2,7,1,3,6

**Manipulation:** Switch removal end and explain why the behavior becomes LIFO.

**Limits:** 0–32 values; show front/back and FIFO ordering.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static List<Integer> queueOrder(int[] a) {
        Deque<Integer> queue = new ArrayDeque<>();
        for (int value : a) queue.addLast(value);
        List<Integer> out = new ArrayList<>();
        while (!queue.isEmpty()) out.add(queue.removeFirst());
        return out;
    }
static List<Integer> bothEnds() {
    Deque<Integer> deque=new ArrayDeque<>();
    deque.addLast(2); deque.addFirst(1);
    return List.of(deque.removeFirst(),deque.removeLast());
}
```

**Time:** O(n) total; amortized O(1) per deque operation. **Space:** O(n) structure.

**Assumptions:** Explicit addLast/removeFirst; empty removal guarded.

**Prediction:** After addLast(4), addLast(2), what does removeFirst return?

### Question applications — Phase 2

Code line 5: Remove the earliest queued value from the front.

**Introduction: [Number of Recent Calls](https://leetcode.com/problems/number-of-recent-calls/).** Discard expired timestamps from the front.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Calls older than the time window can be discarded. → Increasing timestamps put expired entries at the front. → Append the new timestamp, remove entries strictly older than the inclusive lower bound, and report queue size.

Approach: Append the new timestamp, remove entries strictly older than the inclusive lower bound, and report queue size.

**Transfer: [Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/).** Compose FIFO behavior from two LIFO structures.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Moving a stack into another reverses its order. → Do not transfer while the output stack still has items. → Push to an input stack; refill the output stack only when empty. Each element transfers once, giving amortized O(1) operations.

Approach: Push to an input stack; refill the output stack only when empty. Each element transfers once, giving amortized O(1) operations.


## 16. Recursion and the Call Stack

**Objectives:** Define a base case and a smaller subproblem. Distinguish a suspended frame from a returned value.

**Prerequisites:** concept-stacks

### Visual concept

A function leaves a frame on the call stack while a smaller call runs. Returning resumes that exact frame with its own local state.

factorial(5) waits for factorial(4), down to factorial(0)=1. Unwinding returns 1,2,6,24,120. Each multiplication happens after the smaller call returns.

**Invariant:** factorial(n) returns n times factorial(n-1), with factorial(0)=1.

**Watch out:** A missing base case or a call that does not reduce the problem can recurse indefinitely. The call stack consumes space even when no explicit array is allocated.

**Visual specification:** factorial(5)

call 5,4,3,2,1,0 → base returns 1 → unwind 1,2,6,24,120

**Manipulation:** Change n and follow frame-local n separately from returned result.

**Limits:** n=0..10; show base frame and unwind; no arbitrary own-code tracing.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static long factorial(int n) {
        if (n < 0 || n > 10) throw new IllegalArgumentException();
        if (n == 0) return 1;
        return n * factorial(n - 1);
    }
    static long sumFrom(int[] a, int i) {
        if (i == a.length) return 0;
        return a[i] + sumFrom(a, i + 1);
    }
```

**Time:** O(n). **Space:** O(n) call stack.

**Assumptions:** 0 <= n <= 10 for this bounded example; array-sum application uses the same base/reduction structure.

**Prediction:** What is still pending when factorial(5) calls factorial(4)?

### Question applications — Phase 2

Code line 4: Suspend this frame, then multiply by its own n when the smaller call returns.

**Introduction: Recursive Array Sum (original).** Replace a loop with a base case and smaller suffix.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: What is the sum of an empty suffix? → Advance the index to reduce the remaining problem. → Return a[i]+sumFrom(a,i+1), with zero at i==length.

Approach: Use one stack frame per remaining element, showing both returned sum and O(n) stack use.

**Transfer: [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/).** Revisit reversal recursively; compare extra stack use.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Preserve access to the suffix before changing an arrow. → Track previous, current and saved next. → Iteratively reverse one link at a time; later revisit recursively by reversing the suffix and reconnecting the former head.

Approach: Iteratively reverse one link at a time; later revisit recursively by reversing the suffix and reconnecting the former head.


## 17. Backtracking

**Objectives:** Explore choices recursively and restore shared state. Snapshot a result instead of keeping an alias to the mutable path.

**Prerequisites:** concept-recursion

### Visual concept

Walk a decision tree with a reusable path. Choose an item, explore descendants, then undo that choice before trying the next branch.

For [1,2], visit records [] first, then chooses 1 and records [1], chooses 2 and records [1,2], undoes 2 and then 1, and finally chooses 2 alone and records [2]. Every node of the decision tree is a subset.

**Invariant:** On entering visit(start), path holds chosen values in increasing index order, all from indices below start.

**Watch out:** Missing the undo contaminates sibling branches. Storing path itself makes every result alias one mutable list. Duplicate input values require a separate deduplication policy.

**Visual specification:** [1,2]

record [] → choose 1: record [1] → choose 2: record [1,2] → undo 2, then undo 1 → choose 2: record [2]

**Manipulation:** Change the input and watch each undo restore the parent path before the next sibling.

**Limits:** Distinct values; at most 5 items in existing trace; exponential output explicit.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static List<List<Integer>> subsets(int[] a) {
        List<List<Integer>> out = new ArrayList<>();
        visit(a, 0, new ArrayList<>(), out);
        return out;
    }
    static void visit(int[] a, int start, List<Integer> path, List<List<Integer>> out) {
        out.add(new ArrayList<>(path));
        for (int i = start; i < a.length; i++) {
            path.add(a[i]);
            visit(a, i + 1, path, out);
            path.remove(path.size() - 1);
        }
    }
```

**Time:** O(n × 2^n) including copied subsets. **Space:** O(n) auxiliary; O(n × 2^n) output.

**Assumptions:** Distinct input values; bounded teaching subset size.

**Prediction:** Why copy path when recording a subset?

### Question applications — Phase 2

Code line 11: Undo the last choice so the next sibling receives the parent path.

**Introduction: [Subsets](https://leetcode.com/problems/subsets/).** Enumerate include/exclude choices.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Each distinct input item has an include/exclude choice. → Undo a choice before visiting its sibling. → Explore both choices recursively and snapshot paths into output; include the empty subset and account for output size.

Approach: Explore both choices recursively and snapshot paths into output; include the empty subset and account for output size.

**Transfer: [Combination Sum](https://leetcode.com/problems/combination-sum/).** Add a target, candidate reuse and duplicate-order control.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Track the remaining target and the lowest allowed candidate index. → Reusing an index allows repeated use without reordered duplicates. → Explore candidates from a nondecreasing index, recurse with a reduced remainder and undo the choice; positive candidates justify pruning.

Approach: Explore candidates from a nondecreasing index, recurse with a reduced remainder and undo the choice; positive candidates justify pruning.


## 18. Binary Trees and Traversal

**Objectives:** Distinguish a general binary tree from a BST. Visit a tree in inorder or compute height from child results.

**Prerequisites:** concept-linked-lists, concept-recursion

### Visual concept

A binary tree node has up to two child references. Traversal chooses when to visit the node relative to those children; no ordering property is required.

For root 4 with left subtree 2(1,3) and right subtree 7(6,null), inorder visits [1,2,3,4,6,7] and height is 3 nodes. This example is ordered, but arbitrary binary trees need not be.

**Invariant:** inorder(node) processes every node in left subtree, then node, then right subtree.

**Watch out:** Inorder output is sorted only for a valid BST. Define whether height counts nodes or edges; the empty tree has height 0 in this lesson.

**Visual specification:** 4 with children 2(1,3),7(6,null)

walk left:1,2,3 → visit root:4 → walk right:6,7

**Manipulation:** Change a value without rewiring links to see why general inorder need not be sorted.

**Limits:** Small acyclic tree; inorder specification separate from the existing level-order renderer.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static List<Integer> inorder(Tree root) {
        List<Integer> out = new ArrayList<>(); walk(root, out); return out;
    }
    static void walk(Tree node, List<Integer> out) {
        if (node == null) return;
        walk(node.left, out); out.add(node.value); walk(node.right, out);
    }
    static int height(Tree node) {
        return node == null ? 0 : 1 + Math.max(height(node.left), height(node.right));
    }
    static class Tree {
    int value; Tree left, right;
    Tree(int value, Tree left, Tree right) { this.value=value; this.left=left; this.right=right; }
}
static Tree sample() {
    return new Tree(4, new Tree(2,new Tree(1,null,null),new Tree(3,null,null)),new Tree(7,new Tree(6,null,null),null));
}
```

**Time:** O(n). **Space:** O(h) call stack, plus O(n) output.

**Assumptions:** Acyclic tree; height counts nodes; existing interactive child demonstrates level order, not inorder.

**Prediction:** Does inorder traversal sort every binary tree?

### Question applications — Phase 2

Code line 6: Return from the left subtree, then visit the node before descending right.

**Introduction: [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/).** Combine child results into a depth.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: What depth should an empty subtree return? → Combine two already solved child depths. → Return zero for null and one plus the larger child depth otherwise; specify that depth counts nodes.

Approach: Return zero for null and one plus the larger child depth otherwise; specify that depth counts nodes.

**Transfer: [Binary Tree Inorder Traversal](https://leetcode.com/problems/binary-tree-inorder-traversal/).** Choose the visit position relative to children.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Place the node visit between its child traversals. → A stack can hold the deferred ancestors. → Traverse left, visit node, traverse right; implement recursively first, then an explicit stack as an extension.

Approach: Traverse left, visit node, traverse right; implement recursively first, then an explicit stack as an extension.


## 19. Binary Search Trees

**Objectives:** Insert/search using subtree ordering. Explain why an unbalanced BST may degrade to linear height.

**Prerequisites:** concept-binary-search, concept-binary-trees

### Visual concept

Each node splits the remaining keys: every left key is smaller and every right key is larger. Follow that decision at each level.

Insert [8,3,10,1,6,14,4,7,13]. Inorder becomes [1,3,4,6,7,8,10,13,14]; inserting 6 again leaves the tree unchanged.

**Invariant:** For every node, all left descendants are smaller and all right descendants are larger.

**Watch out:** Checking only immediate children does not validate a whole BST. Sorted insertion can produce a chain; O(log n) requires a height assumption.

**Visual specification:** insert [8,3,10,1,6,14,4,7,13]

root 8 → 3 left,10 right → 6 right of 3 → 13 left of 14

**Manipulation:** Insert sorted or repeated keys; follow comparisons and stable node IDs.

**Limits:** 1–32 input keys; equal keys ignored; no balancing guarantee.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static Tree insert(Tree node, int value) {
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
    static class Tree {
    int value; Tree left, right;
    Tree(int value, Tree left, Tree right) { this.value=value; this.left=left; this.right=right; }
}
static Tree sample() {
    return new Tree(4, new Tree(2,new Tree(1,null,null),new Tree(3,null,null)),new Tree(7,new Tree(6,null,null),null));
}
```

**Time:** O(h) per insertion/search; worst O(n). **Space:** O(h) recursive stack; O(n) stored nodes.

**Assumptions:** Distinct keys; duplicates ignored; no balancing in this lesson.

**Prediction:** After 8,3,10, where does 6 go?

### Question applications — Phase 2

Code line 3: Compare with this node and descend into the only possible insertion subtree.

**Introduction: [Search in a Binary Search Tree](https://leetcode.com/problems/search-in-a-binary-search-tree/).** Discard one subtree after each comparison.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Compare target to the current key. → One whole subtree is impossible after each comparison. → Follow left for smaller targets and right for larger ones, returning the matching node or null; cost depends on height.

Approach: Follow left for smaller targets and right for larger ones, returning the matching node or null; cost depends on height.

**Transfer: [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/).** Propagate ancestor bounds to every descendant.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Immediate child comparisons do not constrain all descendants. → Carry strict lower and upper bounds down the tree. → Each key must lie inside its inherited bounds; narrow the upper bound on the left and lower bound on the right, using safe bound types.

Approach: Each key must lie inside its inherited bounds; narrow the upper bound on the left and lower bound on the right, using safe bound types.


## 20. Heaps and Priority Queues

**Objectives:** Maintain parent/child heap order. Distinguish the maximum at the root from a fully sorted array.

**Prerequisites:** concept-sorting, concept-binary-trees

### Visual concept

A complete tree fits in an array: parent of i is (i-1)/2. In a max-heap, a new value moves up until its parent is at least as large.

Insert [4,2,7,1,3,6]. After 7 enters, it swaps with 4; the final heap is [7,3,6,1,2,4]. Only parent-child order is guaranteed.

**Invariant:** Every parent is at least as large as its children.

**Watch out:** A heap is not a sorted array, and Java PriorityQueue defaults to a min-heap. A top-k problem needs a deliberate choice of min/max orientation.

**Visual specification:** insert [4,2,7,1,3,6]

[4] → [4,2] → [7,2,4] → [7,3,6,1,2,4]

**Manipulation:** Insert a new maximum and observe every parent comparison/swap.

**Limits:** 0–32 values; existing trace records completed insertions, intermediate bubble swaps remain a renderer/trace gap.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static List<Integer> heap(int[] a) {
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
    }
```

**Time:** O(log n) per insertion; O(n log n) repeated insertion. **Space:** O(n) heap storage.

**Assumptions:** Custom max-heap insertion shown; bottom-up O(n) heap building is a later extension.

**Prediction:** Is every sibling pair ordered in a max-heap?

### Question applications — Phase 2

Code line 8: Move a newly inserted value up one level while preserving the other heap entries.

**Introduction: [Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/).** Use a min-heap to retain the k largest stream values.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: You only need to retain the k largest values so far. → The smallest retained value is the kth largest. → Maintain a min-heap of at most k values, remove its minimum when oversized and report the root under the API’s input guarantees.

Approach: Maintain a min-heap of at most k values, remove its minimum when oversized and report the root under the API’s input guarantees.

**Transfer: [Last Stone Weight](https://leetcode.com/problems/last-stone-weight/).** Use a max-heap for repeated largest-pair removal.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Each round needs the two current largest values. → Sorting from scratch repeats work. → Use a max-heap, remove two largest weights and insert their nonzero difference; return zero for an empty result.

Approach: Use a max-heap, remove two largest weights and insert their nonzero difference; return zero for an empty result.


## 21. Graph Representation

**Objectives:** Build an adjacency list including isolated vertices. Distinguish directed edges, undirected edges and edge weights.

**Prerequisites:** concept-hashing, concept-matrices

### Visual concept

A graph names vertices and stores their connections. An adjacency list gives every vertex a row of outgoing neighbours, including an empty row for an isolated vertex.

For n=4 and directed edges 0→1,0→2,2→3, adjacency is [[1,2],[],[3],[]]. Making this undirected also requires the reverse connection for each edge.

**Invariant:** Every supplied directed edge u→v contributes v to exactly the outgoing row for u.

**Watch out:** Forgetting isolated vertices changes n. A matrix costs O(V²) storage, while a list stores O(V+E). Parallel edges and self loops require an explicit policy.

**Visual specification:** V=4; edges 0→1,0→2,2→3

create four empty rows → row 0=[1,2] → row 2=[3]; rows 1,3 stay empty

**Manipulation:** Toggle directedness or add an isolated vertex, self loop or parallel edge.

**Limits:** 0–8 vertices and up to 16 edges; explicit graph-input renderer not yet implemented.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.

### Minimal Java

```java
static List<List<Integer>> adjacency(int n, int[][] edges) {
    if(n<0)throw new IllegalArgumentException();
    List<List<Integer>> graph=new ArrayList<>();
    for(int i=0;i<n;i++)graph.add(new ArrayList<>());
    for(int[] e:edges) {
        if(e.length!=2 || e[0]<0 || e[0]>=n || e[1]<0 || e[1]>=n)throw new IllegalArgumentException();
        graph.get(e[0]).add(e[1]);
    }
    return graph;
}
```

**Time:** O(V+E) build. **Space:** O(V+E).

**Assumptions:** Vertices 0..n-1; directed edges; preserve parallel edges and self loops.

**Prediction:** For an undirected edge between 0 and 1, which rows need entries?

### Question applications — Phase 2

Code line 7: Add one directed outgoing neighbour without losing isolated rows.

**Introduction: Build an Adjacency List (original).** Translate edges into a concrete representation.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Allocate a row for every vertex. → Add each directed edge to its source row. → Keep isolated vertices, self loops and parallel edges visible.

Approach: Construct outgoing lists, validate vertex identifiers, then demonstrate how an undirected representation adds reverse entries.

**Transfer: [Find Center of Star Graph](https://leetcode.com/problems/find-center-of-star-graph/).** Exploit a promised star structure and compare degree counts.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Use the promise that this graph is a star. → The first two edges already share the centre. → Return their common endpoint; also explain the degree-counting representation-based solution and why the star guarantee is essential.

Approach: Return their common endpoint; also explain the degree-counting representation-based solution and why the star guarantee is essential.


## 22. Breadth-First Search

**Objectives:** Use FIFO to explore by edge-distance layers. Mark discovery on enqueue so a vertex is queued once.

**Prerequisites:** concept-queues, concept-graphs

### Visual concept

A queue holds the discovered frontier. Removing the oldest vertex finishes the nearer layer before later discoveries.

For the teaching graph with edges i→i+1 and i→i+2 where valid, start from 0. Queue [0] becomes [1,2], then [2,3], then [3,4]. Distances are [0,1,1,2,2,3].

**Invariant:** When first enqueued, distance[v] is the minimum number of unweighted edges from the source.

**Watch out:** Visited-on-removal can enqueue the same vertex many times. BFS does not minimize arbitrary weighted costs; unreachable vertices retain -1.

**Visual specification:** generated 6-vertex graph; source 0

queue=[0] → expand 0:queue=[1,2] → expand 1:queue=[2,3] → distance=[0,1,1,2,2,3]

**Manipulation:** Compare queue and discovery state; change generated input length.

**Limits:** Current trace generates a directed graph and ignores displayed weights for BFS; explicit adjacency/grid input is future work.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.
- Traversal graphs are generated from numeric inputs; arbitrary grid/multi-source practice is outside this scene.

### Minimal Java

```java
static int[] distances(List<List<Integer>> graph,int source) {
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
    static List<List<Integer>> adjacency(int n, int[][] edges) {
    if(n<0)throw new IllegalArgumentException();
    List<List<Integer>> graph=new ArrayList<>();
    for(int i=0;i<n;i++)graph.add(new ArrayList<>());
    for(int[] e:edges) {
        if(e.length!=2 || e[0]<0 || e[0]>=n || e[1]<0 || e[1]>=n)throw new IllegalArgumentException();
        graph.get(e[0]).add(e[1]);
    }
    return graph;
}
```

**Time:** O(V+E) with adjacency lists. **Space:** O(V) auxiliary.

**Assumptions:** Unweighted directed graph; valid source; neighbour order follows input.

**Prediction:** Why mark a vertex discovered when it enters the queue?

### Question applications — Phase 2

Code line 7: Record discovery and distance before enqueueing, preventing duplicate queue entries.

**Introduction: [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/).** Reuse FIFO for nodes grouped by depth.

Additional prerequisites: concept-binary-trees.

Progressive hints: The queue orders nodes by discovery depth. → Capture the current queue size before processing a level. → Process exactly that many nodes into one output row and enqueue their children for the next row; handle a null root.

Approach: Process exactly that many nodes into one output row and enqueue their children for the next row; handle a null root.

**Transfer: [Rotting Oranges](https://leetcode.com/problems/rotting-oranges/).** Use simultaneous grid sources and layer-based minutes.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: All initially rotten cells are simultaneous sources. → A BFS layer represents one minute, not one cell. → Queue all sources, mark fresh neighbours when enqueued, track minutes by layers and detect fresh cells left unreachable.

Approach: Queue all sources, mark fresh neighbours when enqueued, track minutes by layers and detect fresh cells left unreachable.


## 23. Depth-First Search

**Objectives:** Explore a branch before returning to its parent. Use a visited set to handle cycles and a forest to cover disconnected components.

**Prerequisites:** concept-recursion, concept-graphs

### Visual concept

Keep the current path on the call stack. Enter an unvisited neighbour, finish its descendants, then return to try the next neighbour.

With neighbours in ascending order on the generated six-vertex graph, DFS enters 0,1,2,3,4,5 before unwinding. Changing neighbour order can produce a different valid DFS.

**Invariant:** Every active frame represents a discovered vertex whose outgoing neighbours are not yet fully explored.

**Watch out:** DFS does not guarantee shortest paths. Mark before descending to break cycles. Pre-marking every sibling before exploring one can produce a traversal that is not recursive DFS.

**Visual specification:** generated 6-vertex graph, ascending neighbours

enter 0 → descend 1,2,3,4,5 → exit 5,4,3,2,1,0

**Manipulation:** Step through entry and return; compare recursive path with BFS frontier.

**Limits:** Up to 8 generated vertices; trace visits source component, full-code forest also handles disconnected graphs.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.
- Traversal graphs are generated from numeric inputs; arbitrary grid/multi-source practice is outside this scene.

### Minimal Java

```java
static List<Integer> dfs(List<List<Integer>> graph) {
        boolean[] seen=new boolean[graph.size()]; List<Integer> out=new ArrayList<>();
        for(int u=0;u<graph.size();u++) if(!seen[u]) explore(graph,u,seen,out);
        return out;
    }
    static void explore(List<List<Integer>> graph,int u,boolean[] seen,List<Integer> out) {
        seen[u]=true; out.add(u);
        for(int v:graph.get(u)) if(!seen[v]) explore(graph,v,seen,out);
    }
    static List<List<Integer>> adjacency(int n, int[][] edges) {
    if(n<0)throw new IllegalArgumentException();
    List<List<Integer>> graph=new ArrayList<>();
    for(int i=0;i<n;i++)graph.add(new ArrayList<>());
    for(int[] e:edges) {
        if(e.length!=2 || e[0]<0 || e[0]>=n || e[1]<0 || e[1]>=n)throw new IllegalArgumentException();
        graph.get(e[0]).add(e[1]);
    }
    return graph;
}
```

**Time:** O(V+E). **Space:** O(V) visited/call stack.

**Assumptions:** Small teaching graphs; outer loop covers disconnected components; recursion may overflow on deep real graphs.

**Prediction:** Does finding a vertex first with DFS prove the shortest route?

### Question applications — Phase 2

Code line 8: Suspend this frame and fully explore one unvisited neighbour before trying the next.

**Introduction: [Number of Islands](https://leetcode.com/problems/number-of-islands/).** Count components across a full grid scan.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: One traversal consumes one connected land component. → Start a traversal only at unvisited land. → Scan the grid; each new land seed increments the count and floods its four-neighbour component using DFS or BFS.

Approach: Scan the grid; each new land seed increments the count and floods its four-neighbour component using DFS or BFS.

**Transfer: [Flood Fill](https://leetcode.com/problems/flood-fill/).** Recolour only the start component with early visited marking.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Only the starting colour’s connected component changes. → If the replacement equals the starting colour, return early. → Visit matching four-neighbour cells and mark them before exploring neighbours; preserve disconnected matching regions.

Approach: Visit matching four-neighbour cells and mark them before exploring neighbours; preserve disconnected matching regions.


## 24. Dynamic Programming: Memoization and Tabulation

**Objectives:** Define state, base cases and dependencies before coding. Compare top-down caching with bottom-up evaluation and transfer to a new recurrence.

**Prerequisites:** concept-prefix-sums, concept-recursion

### Visual concept

A dependency graph can revisit the same smaller question. Memoization caches answers when requested; tabulation chooses an order with dependencies already available.

F(0)=0,F(1)=1. For n=7, both versions return 13 from table [0,1,1,2,3,5,8,13]. Staircase counts and House Robber reuse state thinking but have different meanings and base cases.

**Invariant:** A cached state is final; a bottom-up state reads only final earlier dependencies.

**Watch out:** Using zero to mean both uncomputed and a valid answer is ambiguous. Memorizing Fibonacci code does not define a state for House Robber; derive take/skip decisions for the prefix instead.

**Visual specification:** F(7), base F(0)=0,F(1)=1

base [0,1] → write 1,2,3,5,8,13 → both methods return 13

**Manipulation:** Change n, compare repeated calls with cache hits and bottom-up writes.

**Limits:** n=0..16; do not imply Fibonacci is the complete DP curriculum; practice derives two distinct state models.

**Interactive readiness:** interactive

- This is bounded authored execution, not tracing arbitrary student code.
- The interactive dependency example is Fibonacci; staircase and House Robber practice remain distinct Phase 2 applications.

### Minimal Java

```java
static int fibMemo(int n) {
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
    }
```

**Time:** O(n) per Fibonacci version. **Space:** O(n) table; top-down also O(n) call stack.

**Assumptions:** n=0..16; examples keep table for visibility; final-value rolling storage can use O(1).

**Prediction:** If F(4)=3 and F(5)=5, what is F(6)?

### Question applications — Phase 2

Code line 11: Read two final dependencies and store the destination state exactly once.

**Introduction: [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/).** Derive route-count states and correct bases.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Define a state as the number of routes to a step. → The final move comes from one or two steps below. → Use ways[0]=1 and the appropriate first-step base, then sum predecessor counts; explain why this differs from Fibonacci’s state interpretation.

Approach: Use ways[0]=1 and the appropriate first-step base, then sum predecessor counts; explain why this differs from Fibonacci’s state interpretation.

**Transfer: [House Robber](https://leetcode.com/problems/house-robber/).** Derive maximum-value prefix states with take/skip choices.

Additional prerequisites: None beyond the concept sequence.

Progressive hints: Define best for a prefix of houses. → For the last house, either skip it or take it and skip its neighbour. → Use best[i]=max(best[i-1], value[i-1]+best[i-2]) with empty-prefix base zero; optionally roll two previous results.

Approach: Use best[i]=max(best[i-1], value[i-1]+best[i-2]) with empty-prefix base zero; optionally roll two previous results.

## Phase 2 handover

- Review the curriculum before deciding when to build the skill-tree interface. Use the manifest dependency graph; do not infer edges from display order.
- Implement assigned practice progressively, preserving canonical question identity and the existing local problem catalogue.
- Complete the recorded visualization gaps. Do not label specification-only concepts as fully interactive.
- Refine layout, animation and mobile experience on top of stable lesson/challenge/trace contracts.
- Retain old lessons, notes, progress and administrator edits. Keep advanced academic algorithms available outside the core path.
- External question statements/editorials are not bundled; links are references and access can change.

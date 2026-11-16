PROSE = {
    'lesson-dfs': dict(
        body="Picture exploring a cave with a ball of string. You follow one passage as far as it goes, and only when it dead-ends do you wind the string back to the last fork and try the next opening. Depth-first search does the same on a graph: the call stack is the string, recording the path from the start to where you stand. It answers questions such as which vertices can I reach, is there a cycle, or what belongs to one connected piece. In the animation, watch the list of open frames grow by one vertex each time the search goes deeper, and shrink by one each time a vertex is finished. The order in which vertices are entered and the order in which they finish are both useful later, for example in topological sorting.",
        worked=dict(
            title="One long dive, then unwind",
            text="The search starts at vertex 0 and marks it entered. From 0 it descends to neighbour 1 before looking at any other neighbour of 0, and the same thing repeats: 1 descends to 2, 2 to 3, 3 to 4, and 4 to 5. At that moment six frames are open, [0, 1, 2, 3, 4, 5], which is the exact path from the source. Vertex 5 has nothing new to explore, so it finishes and returns. Then 4, 3, 2, 1 and 0 finish in turn. None of them finds another unvisited neighbour on the way back, so the stack empties without a second dive. The final state reports 6 visited vertices, and the entry order 0, 1, 2, 3, 4, 5 is what dfs returns in its out list.",
        ),
        invariant=dict(
            title="The open frames are the path",
            text="At every moment, the open frames form a path of discovered vertices from the source to the vertex being explored, and each of them may still have neighbours left to check. A vertex is marked in seen the moment explore is called on it, before any of its neighbours are tried. That early mark keeps the search finite: if a cycle leads back to a vertex already marked, the check fails and the search does not enter it again. When a frame returns, every vertex reachable from it through still-unmarked vertices has been entered. So no vertex is entered twice, and every vertex reachable from the source is entered once.",
        ),
        tradeoff=dict(
            title="Each edge is checked once",
            text="Each vertex is entered once because seen blocks a second entry, and each vertex's neighbour list is scanned once while its frame is open. Across the whole graph that is V entries plus E neighbour checks, so the time is O(V+E) with adjacency lists. The space is O(V): the seen array has one slot per vertex, and in the worst case, a long chain like the one in this trace, the call stack holds every vertex at once. On a large graph shaped like a long line, recursion can overflow Java's stack, so switch to an explicit stack. If you need the fewest edges to a target, use BFS instead. The outer loop in dfs restarts from every unmarked vertex, so disconnected parts are covered too.",
        ),
        pitfall="Do not expect DFS to find shortest routes. It follows the first neighbour as deep as it goes, so a target one edge away can be reached through a long detour first. Also mark a vertex when you enter it, not when you finish it. If the mark comes late, a cycle sends the search back into a vertex that is still on the path, and the recursion never ends.",
        prerequisiteNotes={
            'concept-recursion': "explore calls itself for each unvisited neighbour, and the call stack remembers where to resume when a deeper call returns.",
            'concept-graphs': "The search walks the lists built by adjacency, reading each vertex's row of outgoing neighbours.",
        },
    ),
    'lesson-memoization': dict(
        body="Suppose a friend asks you for 37 times 43 and you work it out on paper. If they ask again five minutes later, you read your answer off the paper instead of redoing the multiplication. Memoization gives a recursive function that same notepad. Plain recursive Fibonacci calls F(n-1) and F(n-2), and those two calls share almost all of their work, so the number of calls explodes as n grows. Storing each answer the first time it is finished collapses that tree of calls into one computation per value of n. In the animation, watch two things: the chain of frames that dives down to the base cases once, and the cache hits on the way back up, where a call returns at once without opening any deeper frames.",
        worked=dict(
            title="Dive once, then reuse",
            text="The trace computes F(8). The first call opens frames for 8, 7, 6, 5, 4, 3, 2 and finally 1, always taking the n minus one branch first. F(1) returns 1 and F(0) returns 0 as base cases, so F(2) is stored as 1. Back in F(3), its second call F(1) is another base case, and F(3) is stored as 2. Now the reuse starts. F(4) needs F(2), which is already in the table: a cache hit returns 1 with no new frames, and F(4) is stored as 3. The same pattern repeats at every level. F(5) reuses F(3) and becomes 5, F(6) reuses F(4) and becomes 8, F(7) reuses F(5) and becomes 13, and F(8) reuses F(6) and becomes 21. The finished table is [0, 1, 1, 2, 3, 5, 8, 13, 21], and the answer read from it is 21.",
        ),
        invariant=dict(
            title="A stored value is final",
            text="Once memo holds a value for n, that value is the true F(n) and never changes. It is written only after both recursive calls have returned, and those calls return correct values by the same argument applied to smaller n, with F(0) and F(1) returned directly as base cases. So a cache hit is safe: reading memo[n] gives exactly what recomputing would give. The table in the trace fills strictly left to right, because an entry can only be written after the entries it depends on. The bottom-up fibTable relies on the same fact in loop form: when it writes dp[i], the two entries before it are already final.",
        ),
        tradeoff=dict(
            title="Calls drop from exponential to linear",
            text="Without the cache, F(n) makes two calls that each make two more, and the shared work is redone again and again, so the call count grows exponentially, roughly like the Fibonacci numbers themselves. With memo, each n from 2 up to the target is computed once, and every other call is a base case or a cache hit that does constant work. That gives O(n) time. Space is O(n) for the memo array, plus O(n) for the recursion stack, which in the trace is deepest with 8 frames open. fibTable has the same O(n) time and table with no recursion, so it cannot overflow the stack. If you only need the final value, keep the last two numbers and the space drops to O(1). Note that int overflows after F(46); use long for larger n.",
        ),
        pitfall="Check the cache before recursing and store the result before returning. If the two recursive calls still run on every visit and memo is only written afterwards, the table fills up but nothing is saved. A quick test: every repeated n should show a cache hit with no new frames under it. Also keep not computed apart from a computed zero; memo uses Integer and null for that reason.",
        prerequisiteNotes={
            'concept-prefix-sums': "fibTable fills dp left to right, each entry built from earlier entries, the same pattern as building a prefix table.",
            'concept-recursion': "solve calls itself twice, and reading the trace means following how frames open, return and resume their callers.",
        },
    ),
    'lesson-complexity': dict(
        body="Timing code with a stopwatch tells you about one machine on one day. Complexity asks a sturdier question: if the input doubles, how much more work does the code do? To answer it, pick one basic operation, here one pass through a loop body, and count how many times it runs as a formula in n. Think of counting steps instead of minutes: a walker's speed changes from day to day, the number of steps does not. In the animation the same n drives three loops. Notice how differently their counters grow. One ticks once per position, one adds a whole row at a time, and one stops after a handful of visits because its variable is halved each time.",
        worked=dict(
            title="Three counters for n = 8",
            text="With n = 8, the scan loop visits positions 0 through 7, and its counter climbs one step at a time until it reads 8. The nested loop counts ordered pairs. Each outer row contributes a full inner loop of 8 visits, so the counter jumps to 8, 16, 24, 32, 40, 48, 56 and ends at 64 after row 7. The halving loop starts with x at 8 and divides by two: it visits 8, 4, 2 and 1, and when x becomes 0 the loop stops, giving 4 visits. The final comparison is 8, 64 and 4 for the same input size. Try predicting n = 16 before you run it: the scan doubles, the pair count grows fourfold, and the halving count grows by one.",
        ),
        invariant=dict(
            title="Count what the body does",
            text="Each counter in counts goes up by exactly one every time its loop body runs, so when a loop finishes, its counter equals the number of times that body executed. That is the whole method: choose the operation you care about, write down how many times it runs, and keep the term that grows fastest. For the scan the count is n. For the square loop the inner body runs n times for each of n outer values, so n times n. For halving, x takes the values n, n/2, n/4 and so on down to 1, which is about log2(n) plus one values. Big-O then drops constant factors and smaller terms, because they stop mattering as n grows.",
        ),
        tradeoff=dict(
            title="Why growth beats milliseconds",
            text="The three loops cost O(n), O(n²) and O(log n) time because those are the formulas their counters follow. Space is O(1) auxiliary: however large n is, counts keeps three long counters and a loop variable or two, and nothing grows with n. Growth rate matters more than constant factors once inputs get large. At n = 1000 the scan does a thousand visits and the square loop a million, so a quadratic method that was fine on a small test can stall on real data. Counting has limits too. It ignores memory effects and fixed overhead, so for small n a plain O(n²) loop can beat a cleverer method. Treat Big-O as a guide to how cost scales, then measure when the constants matter.",
        ),
        pitfall="Do not read complexity off the shape of the code. Two nested loops are quadratic only when both run about n times. If the inner loop runs a fixed 3 times, or halves its range, the count is very different. Write down how many times the inner body runs for each outer value and add those numbers up.",
        prerequisiteNotes={},
    ),
    'lesson-arrays': dict(
        body="Think of an array as a row of numbered lockers. Each locker has a fixed position, and you can open locker 2 directly without walking past lockers 0 and 1. That direct jump is why arrays are the default container for ordered data: reading or writing any slot by its index costs the same, however long the row is. The index names a place, not what is stored there, so two lockers can hold the same value and still be different slots. In the animation, watch the index move left to right while a running total absorbs one slot at a time. That pattern, a loop plus a variable that summarises everything seen so far, is the shape of most array algorithms you will meet next.",
        worked=dict(
            title="Summing [2, 1, 5] slot by slot",
            text="Before the loop starts, total is 0 because nothing has been read yet. At index 0 the loop reads 2, and total becomes 2. At index 1 it reads 1, and total becomes 3. At index 2 it reads 5, and total becomes 8. The condition i < a.length now fails, since the length is 3, and sum returns 8. Notice that each step adds only the value in the current slot. The earlier slots are never read again, because total already stands for them. If the array were empty, the loop body would never run and the method would return the starting value 0.",
        ),
        invariant=dict(
            title="Total covers the slots behind i",
            text="Each time the loop is about to read index i, total equals the sum of every slot before i and none after it. At the start i is 0 and no slots are behind it, so total must be 0, which is how it is initialised. Each iteration adds a[i] and then moves i forward by one, so the statement is true again for the new i. When the loop ends, i equals a.length, and every slot before i means the whole array. That is why the returned value is the full sum. This style of reasoning, true at the start, kept by each step, useful at the end, is how you check any loop.",
        ),
        tradeoff=dict(
            title="One visit per slot",
            text="The loop body runs once per slot and does constant work each time, so summing takes O(n) time. You cannot do better for a sum, because every value must be read at least once. Auxiliary space is O(1): one long and one int index, whatever the length. The accumulator is long rather than int because adding many large ints can pass the int limit of about 2.1 billion and wrap silently to a negative number. Arrays are the right tool for indexed reads and scans, but their size is fixed when they are created, and inserting into the middle means shifting every later slot. When the size changes often, a growable list or a linked structure fits better.",
        ),
        prerequisiteNotes={
            'concept-complexity': "You count loop-body visits to see why sum runs in O(n) time with O(1) extra space.",
        },
    ),
    'lesson-strings': dict(
        body="A string is a fixed line of characters, each at a numbered position, like letters stamped on a strip of metal. In Java you can read any position, but you cannot change the strip itself: String is immutable. To produce changed text, you copy characters into a new buffer and turn that buffer into a fresh string at the end. This matters for cost. Gluing strings together with + inside a loop copies the whole growing result each time, while a StringBuilder appends in place. In the animation, keep two things apart: the read index, which walks backwards through the source, and the output, which grows forwards one character at a time. The source never changes.",
        worked=dict(
            title="Reversing \"cat\" into a buffer",
            text="The source is \"cat\", with c at index 0, a at index 1 and t at index 2. The output buffer starts empty. The loop begins at the last index, 2, and appends t, so the output is \"t\". Next it reads index 1 and appends a, giving \"ta\". Then it reads index 0 and appends c, giving \"tac\". The index would now be negative, the condition i >= 0 fails, and reverse returns \"tac\". The source is still \"cat\", because every step only read from it. Notice that the read index goes 2, 1, 0 while the output length goes 1, 2, 3. That is why the two must be tracked separately.",
        ),
        invariant=dict(
            title="The buffer holds a reversed suffix",
            text="After k characters have been appended, the buffer holds the last k characters of the source in reverse order. Before the loop, k is 0 and the buffer is empty, which matches. Each step reads the next character further left and appends it to the right end of the buffer, so the reversed suffix grows by one and stays in the right order. When i passes index 0, k equals the length of the source, the suffix is the whole string, and the buffer is its full reverse. Because nothing is ever written to s, any other code holding a reference to it still sees the original text.",
        ),
        tradeoff=dict(
            title="Why the builder keeps it linear",
            text="The loop runs once per character, and each append adds one character to the end of the builder, which is amortised constant work. So the reversal costs O(n) time. Space is O(n) because the output is a new string of the same length, which you cannot avoid since the original cannot be changed. Concatenating onto a String with + inside the loop would copy the partial result on every step, 1 + 2 + ... + n characters in total, which is O(n²). For one or two concatenations + is fine. One caution: charAt reads UTF-16 code units, so reversing text with emoji or combined accents can split a character in two.",
        ),
        prerequisiteNotes={
            'concept-arrays': "A string is read by index like an array, from 0 to length minus one, so the backwards loop uses the same bounds reasoning.",
        },
    ),
    'lesson-hashing': dict(
        body="Think of a coat check. You hand over a coat, get a ticket number, and later the attendant goes straight to the right hook instead of searching every coat. A hash set does that for values: it turns a key into a bucket number, goes to that bucket, and compares only the few keys stored there. A hash map adds a value to each key, such as a count or an earlier index. This turns questions like have I seen this before, or how many times did this appear, from a scan of everything seen so far into one lookup that takes expected constant time. In the animation, notice that two different keys can land in the same bucket. The bucket only narrows the search; an equality check decides whether the key is really there.",
        worked=dict(
            title="Counting [2, 1, 6, 2, 5]",
            text="The trace follows frequencies on [2, 1, 6, 2, 5], using an illustrative bucket rule of key mod 4. Key 2 goes to bucket 2, is not found, and enters with count 1. Key 1 goes to bucket 1 and enters with count 1. Key 6 also lands in bucket 2, but equality shows it is not 2, so it becomes a separate entry: 3 unique keys now. The second 2 goes to bucket 2, matches the existing key, and its count rises to 2 without a new entry. Finally 5 shares bucket 1 with key 1 and enters as the fourth unique key. The map ends with 2 counted twice and 1, 6 and 5 once each. With duplicate, the second 2 is where seen.add returns false and the method returns true.",
        ),
        invariant=dict(
            title="The table mirrors what came before",
            text="Before position i is read, the set or map contains exactly the distinct values from positions before i, and in frequencies each count equals how often that value has appeared so far. It starts empty, which is correct for an empty prefix. Each step either finds the key and updates it, or inserts it, so the statement holds again for the next position. For duplicate this gives a clean proof: seen.add fails exactly when the current value already appeared earlier, so the first false means a repeat, and finishing the loop means every value was new. Correctness also rests on equality and hashing agreeing: equal keys must hash to the same bucket, or a lookup searches the wrong place.",
        ),
        tradeoff=dict(
            title="Expected constant, not guaranteed",
            text="Each element costs one lookup plus one insert or update. With a good hash function and a table that resizes as it fills, buckets stay short, so each operation takes expected constant time and the whole pass is expected O(n). The worst case is worse: if many keys collide, a bucket grows long and lookups slow down, which is why the bound says expected. Space is O(n) because, when all values are distinct, every one gets an entry. Compare the alternatives. Checking each value against all earlier ones is O(n²) with no extra memory, and sorting first is O(n log n) and puts repeats next to each other. Use a LinkedHashMap, as frequencies does, when you also need the insertion order back.",
        ),
        pitfall="Do not treat the bucket as the answer. Keys 2 and 6 share a bucket in the trace but are different keys; only equality settles membership. For your own key classes, define equality and hashing together, or equal objects will be stored twice and lookups will miss. And remember the speed is expected, not guaranteed: many colliding keys make lookups slow.",
        prerequisiteNotes={
            'concept-arrays': "A hash table keeps its buckets in an array, and the trace scans the input array once, position by position.",
            'concept-strings': "Strings are the most common hash keys, and key equality compares content the same way two strings are compared.",
        },
    ),
    'lesson-prefix-sums': dict(
        body="Imagine a long road with a milestone at every kilometre, each showing the distance from the start. To find the length of any stretch you do not walk it: you read two milestones and subtract. A prefix-sum table puts those milestones on an array. Entry i holds the total of everything before boundary i, so the sum of any contiguous range is one subtraction. This pays off when you need many range sums from the same data. You pay one pass to build the table, then each question is answered in constant time instead of by adding up the slots again. In the animation, watch the table gain one boundary per step, then watch the query use only two of its entries.",
        worked=dict(
            title="Building [0, 2, 3, 8]",
            text="The input is [2, 1, 5]. Boundary 0 stores 0, since nothing has been added yet. Boundary 1 stores 0 + 2 = 2, the sum of the first value. Boundary 2 stores 2 + 1 = 3. Boundary 3 stores 3 + 5 = 8, the sum of the whole array. The table has 4 entries for 3 values, one per boundary. The query asks for the half-open range from 1 to 3, which covers the values 1 and 5. The method reads the entry at the right boundary, 8, and subtracts the entry at the left boundary, 2, giving 6. Check by hand: 1 + 5 is 6.",
        ),
        invariant=dict(
            title="Each entry sums everything before it",
            text="p[i] always equals the sum of the first i values of a, and p[0] is 0 because zero values add to nothing. The loop keeps this true: p[i + 1] is p[i] plus a[i], so it covers exactly one more value. Given that, a range from left to right, including left and excluding right, is the first right values with the first left values taken away. That is p[right] minus p[left], and nothing else is needed. The half-open convention is what keeps the formula clean: the range length is right minus left, and an empty range, where left equals right, correctly sums to 0.",
        ),
        tradeoff=dict(
            title="One pass now, constant time later",
            text="Building the table touches each value once, so it costs O(n) time, and the table takes O(n) space for its n plus one entries. Each range query then reads two entries and subtracts, which is O(1) however wide the range is. For a single query this is no win, since summing the range directly is also O(n). The payoff comes with many queries: q questions cost O(n + q) instead of up to O(n times q). Prefix sums work with negative values too. They handle updates badly: changing one value forces every later entry to change, so for frequent updates use a Fenwick tree or a segment tree. The entries are long so that sums of many values do not overflow.",
        ),
        prerequisiteNotes={
            'concept-arrays': "The table is an array one slot longer than the input, and the build loop reads a[i] while writing p[i + 1].",
        },
    ),
    'lesson-variable-window': dict(
        body="Think of reading a sentence through a stretchable frame that must never show the same letter twice. You keep pulling the right edge forward to see more. When a new letter would repeat one already inside, you slide the left edge forward until the old copy drops out, then carry on. Each edge only ever moves right. That one-way movement is what makes the technique fast: instead of checking every substring, you find the longest valid one in a single sweep. Unlike a fixed window, the width here changes. In the animation, watch left jump forward in a burst when a repeat arrives, and notice that the frame may have to drop more than one character before it is valid again.",
        worked=dict(
            title="Why \"abba\" needs a loop",
            text="Take \"abba\". With right at 0 the frame is a and best becomes 1. With right at 1 the frame is ab and best becomes 2. At right 2 the incoming b is already inside. Removing the leftmost character, a, moves left to 1, but the old b is still there, so shrinking continues: removing b moves left to 2. Now the frame is the single b at index 2 and best stays 2. At right 3 the incoming a is no longer in the set, because it left during the shrink, so the frame becomes ba from index 2 to 3, length 2. The answer is best = 2. A single if in place of the while would have stopped after removing a and left two b characters in the frame.",
        ),
        invariant=dict(
            title="Distinct after every shrink",
            text="After the while loop ends and incoming is added, window holds exactly the characters from index left through index right, all distinct. The loop runs until incoming is absent, so adding it cannot create a repeat. Why is it safe to drop characters from the left for good? Any frame that starts before the new left and ends at right would contain the repeated character twice, and extending such a frame further right keeps that repeat. So no frame the method skips can be valid and longer than one it measured, and best ends as the true maximum.",
        ),
        tradeoff=dict(
            title="Each character enters and leaves once",
            text="The right edge moves n times in total, and the left edge moves at most n times across the whole run, since it never moves back. Each move does one set operation in expected constant time, so the total is expected O(n), even though there is a loop inside a loop. Space is O(min(n, alphabet size)) because the set holds only distinct characters: at most the length of the string, and at most the size of the alphabet. A brute-force check of every substring costs O(n²) or more. Use this pattern only when shrinking from the left always helps restore validity. For sums with negative numbers that property fails, and prefix sums with a hash map are the usual alternative.",
        ),
        pitfall="Writing if instead of while removes only one character per repeat. On \"abba\" the buggy version leaves the frame bb after the second b, then lets a in and reports 3, while the correct answer is 2. Test any window code on an input where the repeated character is not the leftmost one.",
        prerequisiteNotes={
            'concept-hashing': "The set window tells you in expected constant time whether the incoming character is already in the frame.",
            'concept-fixed-window': "You already slide a frame by adding on the right and removing on the left; here the frame's width is allowed to change.",
        },
    ),
    'lesson-intervals': dict(
        body="Picture bookings for a shared meeting room, written as time ranges on a whiteboard in no particular order. To see when the room is actually busy, you would first line the bookings up by start time, then sweep left to right, joining any booking that starts before the current busy block ends. That is interval merging. Sorting is the step that makes it work: once starts are in order, a new interval can only overlap the most recent merged block, so you never look further back. The same sort-then-sweep idea shows up in calendar conflicts and total covered length. In the animation, notice that each interval causes exactly one of two outcomes: extend the last block, or start a new one.",
        worked=dict(
            title="Merging three segments",
            text="The input pairs are [1, 3], [2, 6] and [8, 10], so there are 3 intervals. Sorting by start leaves them in the same order, since 1, 2, 8 is already ascending. The output is empty, so [1, 3] is appended and there is 1 merged block. Next, [2, 6] starts at 2, which is not past the block's end of 3, so the two overlap and the block's end grows to the larger end, 6. The count stays at 1 and the block is now [1, 6]. Finally [8, 10] starts at 8, past the end 6, so it is appended as a separate block. The result is [1, 6] and [8, 10]: 2 blocks.",
        ),
        invariant=dict(
            title="Only the last block can overlap",
            text="After each interval is processed, the output blocks are in order, do not overlap, and together cover exactly the intervals seen so far. Sorting is what lets the loop compare only with the last block. Every earlier block ends before the last block starts, and every new interval starts at or after the last block's start, so a new interval cannot reach back to an earlier block. If the new start is at most the last end, the two share at least one point and joining them keeps coverage exact. If the start is greater, there is a real gap, and a new block keeps the output disjoint. Taking the larger of the two ends matters when one interval sits inside another.",
        ),
        tradeoff=dict(
            title="Sorting dominates the cost",
            text="The sweep visits each interval once and does constant work, so it is O(n). The sort before it is O(n log n), and that term dominates, so the whole method is O(n log n). If the intervals already arrive sorted by start, you can skip the sort and merge in O(n). Space is O(n): mergeIntervals clones every pair so the caller's arrays are not changed, and the output can hold up to n blocks when nothing overlaps. Decide edge cases up front. Touching endpoints such as [1, 2] and [2, 3] merge here because the intervals are closed, while half-open ranges would keep them apart. An empty input returns an empty array.",
        ),
        prerequisiteNotes={
            'concept-sorting': "Arrays.sort with a comparator on the start puts intervals in order, which lets the merge look only at the last block.",
        },
    ),
    'lesson-matrices': dict(
        body="A matrix is a grid, like a spreadsheet or a seating chart. Every cell has two coordinates: which row it is in and which column. In Java a matrix is an array of row arrays, so a[r][c] means pick row r first, then column c inside it. Grids appear everywhere: images, game boards, distance tables, and the adjacency matrix of a graph. The transpose is a good first exercise because it forces you to keep the two dimensions apart. Rows become columns, so a wide grid turns tall. In the animation, follow one source cell to its new home and notice that its two coordinates trade places, while the row and column counts of the output trade places too.",
        worked=dict(
            title="From 2 × 3 to 3 × 2",
            text="The input values 1, 2, 3, 4, 5, 6 form 2 rows of 3: row 0 is 1, 2, 3 and row 1 is 4, 5, 6. So out is created with 3 rows and 2 columns. The loop walks the source row by row. Cell (0,0) goes to (0,0), (0,1) goes to (1,0) and (0,2) goes to (2,0). The first source row becomes the first output column, which now reads 1, 2, 3 from top to bottom. Then (1,0) goes to (0,1), (1,1) to (1,1) and (1,2) to (2,1), filling column 1 with 4, 5, 6. The result is [[1, 4], [2, 5], [3, 6]]. Cells on the diagonal, (0,0) and (1,1), keep their coordinates.",
        ),
        invariant=dict(
            title="Cell (r, c) lands at (c, r)",
            text="Every source cell a[r][c] is written to out[c][r], and each output cell receives exactly one source cell. That one rule makes the whole result correct: row r of the input becomes column r of the output, and column c becomes row c. The output shape follows from it. Source row numbers now index output columns, so out needs cols rows and rows columns. The nested loop visits every (r, c) pair once, so no cell is missed or copied twice. The ragged check before the loop guarantees that a[r][c] exists for every r and c the loop will touch.",
        ),
        tradeoff=dict(
            title="Every cell is copied once",
            text="The nested loop runs cols times for each of rows, and each pass copies one value, so the time is O(rows × columns). You cannot do better, because every cell must move. Space is also O(rows × columns), since the result is a new grid with the same number of cells. A square matrix can be transposed in place by swapping a[r][c] with a[c][r] for the cells above the diagonal, which needs O(1) extra space, but a non-square grid cannot, because its shape changes. Edge cases: zero rows give an empty result, and a ragged input, where rows have different lengths, is rejected with an exception instead of producing a wrong grid.",
        ),
        prerequisiteNotes={
            'concept-arrays': "A matrix is an array whose slots are arrays, so every cell access is two index lookups with the usual bounds.",
        },
    ),
    'lesson-graphs': dict(
        body="A graph is a set of things and the connections between them: cities and roads, people and friendships, web pages and links. The things are vertices and the connections are edges. Before any search can run, you need to store the connections so that you can quickly ask what is next to this vertex. An adjacency list gives each vertex its own row listing where its edges lead. It is like one contacts page per person: you open a page and see only that person's links, not the whole network. In the animation, watch the rows get created first, one per vertex even if nothing connects to it, and then watch each edge drop its endpoint into the row of the vertex it leaves from.",
        worked=dict(
            title="Four rows, three edges",
            text="The trace uses 4 vertices and the edges 0 to 1, 0 to 2 and 2 to 3. First, adjacency creates 4 empty rows, numbered 0 to 3, before reading any edge, so a vertex with no edges still has a row. Edge 0 to 1 adds 1 to row 0. Edge 0 to 2 adds 2 to row 0, which now reads [1, 2]. Edge 2 to 3 adds 3 to row 2. After 3 edges the graph is [[1, 2], [], [3], []]. Rows 1 and 3 stay empty: those vertices have no outgoing edges, even though edges point into them. Because the edges are directed, asking for the neighbours of 1 returns nothing, not 0.",
        ),
        invariant=dict(
            title="Each edge lands in one row",
            text="Every edge u to v that has been read appears as v in row u, once, and nowhere else. The rows are created for all n vertices before any edge is read, so every valid u has a row waiting. The validity check rejects an edge whose endpoint is outside 0 to n minus one, so a bad edge cannot slip into the wrong row or cause a crash later. With this property, the neighbours of u are exactly row u, which is what BFS and DFS rely on. For an undirected graph, add each edge twice, u to v and v to u. Repeated edges and self loops are kept as given, so decide whether your problem allows them.",
        ),
        tradeoff=dict(
            title="Lists versus a matrix",
            text="Building takes O(V+E) time: one pass creates V rows and a second pass appends each of the E edges in amortised constant time. Space is O(V+E) for the same reason, one row per vertex plus one entry per edge. An adjacency matrix uses V × V cells, so it costs O(V²) space even when there are few edges, but it answers whether an edge u to v exists in O(1). Lists are the usual choice for sparse graphs, where E is far smaller than V², and they let you loop over a vertex's neighbours in time proportional to how many it has. When vertex names are strings rather than 0 to n minus one, map each name to an index first with a hash map.",
        ),
        prerequisiteNotes={
            'concept-hashing': "When vertices have names instead of numbers, a hash map turns each name into the row index this lesson uses.",
            'concept-matrices': "The adjacency matrix is the grid alternative to these lists, and this lesson compares their space costs.",
        },
    ),
}

"""Teaching prose upgrades, batch 1. Checked by check_prose.py 1."""

PROSE = {
    'lesson-two-pointers': dict(
        body=("Picture two people at opposite ends of a shelf of books sorted by price, looking for two books that together "
              "cost exactly your budget. If the pair is too cheap, the person at the cheap end steps inward, because even the "
              "most expensive remaining book could not lift that cheap one to the budget. If the pair is too expensive, the "
              "person at the expensive end steps inward. Each comparison rules out a whole set of pairs at once, so you never "
              "test most of the n(n-1)/2 possible pairs. In the animation, watch which cursor moves after each comparison and "
              "ask which pairs that move has ruled out. Also notice the first step: the input arrives unsorted and is sorted "
              "before the search starts, which is a separate cost."),
        worked=dict(
            title="Sort first, then two sums",
            text=("The input arrives as 4, 2, 7, 1, 3, 6, so the first step sorts it into 1, 2, 3, 4, 6, 7. Now left = 0 "
                  "points at 1 and right = 5 points at 7. Their sum is 8, below the target 9. Since 7 is the largest value "
                  "left, no partner can rescue 1, so left moves to 1. The cursors now point at 2 and 7, the sum is 9, and the "
                  "search stops with the pair 2 + 7. Only two sums were computed. Every pair containing 1 was ruled out by a "
                  "single comparison, and right never had to move. The answer refers to positions in the sorted array, not "
                  "to where 2 and 7 sat in the original input."),
        ),
        invariant=dict(
            title="Why a discarded value never mattered",
            text=("Before every comparison, any pair that sums to the target lies between left and right inclusive. It "
                  "starts true because the cursors cover the whole sorted array. When the sum is too small, sorted[left] "
                  "plus the largest remaining value is still short, so sorted[left] plus any smaller value is short too, and "
                  "dropping left loses no answer. When the sum is too large, sorted[right] plus the smallest remaining value "
                  "already overshoots, so dropping right is safe. Each step shrinks the interval by one and keeps the claim "
                  "true. When left meets right, no pair of distinct positions remains, so returning false is correct."),
        ),
        tradeoff=dict(
            title="Where the linear cost comes from",
            text=("Each loop iteration either returns or moves one cursor one place inward, and the gap between them starts "
                  "at n - 1. So the search makes at most n - 1 comparisons: O(n) time, with O(1) extra space for two indexes "
                  "and a sum. That bound assumes the input is already sorted. If it is not, sorting costs O(n log n) and "
                  "dominates; for one query on unsorted data, a hash set of values seen so far gives O(n) expected time "
                  "without sorting, at the cost of O(n) space. Two pointers reports sorted positions, so keep each value's "
                  "original index alongside it if the problem asks for indices. The sum is computed as a long so adding two "
                  "large int values cannot overflow."),
        ),
        pitfall=("Moving the wrong cursor. If the sum is too small and you move right inward, you throw away the partner most "
                 "likely to help and can skip the answer. Too small moves left, too large moves right. On unsorted input "
                 "neither move is justified, so sort first and count that cost."),
        prerequisiteNotes={
            'concept-strings': "Strings use the same indexed positions, and checking a palindrome is the same inward walk from both ends.",
            'concept-sorting': "The discard rule relies on sorted order, so you need to know what sorting costs and that it changes positions.",
        },
    ),

    'lesson-binary-search': dict(
        body=("Think of guessing a number between 1 and 100 when someone tells you higher or lower. A good guess sits in the "
              "middle, because whichever answer comes back, half of the possibilities disappear. Binary search does the same "
              "with a sorted array: one comparison with the middle value tells you which half cannot contain the target. That "
              "turns a search through n values into about log2 n comparisons, the difference between a million checks and "
              "about twenty. In the animation, keep your eye on the interval between low and high rather than on mid. Each "
              "step should shrink it, and the search ends either on a match or when the interval is empty."),
        worked=dict(
            title="Searching for a missing 5",
            text=("The input 4, 2, 7, 1, 3, 6 is first sorted to 1, 2, 3, 4, 6, 7, and the target is 5. The interval starts "
                  "at low = 0, high = 5. The middle index is 2, holding 3. Since 3 is less than 5, the target can only be to "
                  "the right, so low becomes 3. Now mid = 4 holds 6, which is too large, so high becomes 3. The interval is "
                  "the single index 3, holding 4, still too small, so low becomes 4. With low = 4 and high = 3 the interval "
                  "is empty, and the search returns -1. Three comparisons settled it, and the last two pinned the gap between "
                  "4 and 6, exactly where 5 would have to be."),
        ),
        invariant=dict(
            title="The interval always holds the answer",
            text=("If the target is in the array, some copy of it sits between low and high inclusive. At the start the "
                  "interval is the whole array, so this is true. When a[mid] < target, every index up to mid holds a value no "
                  "larger than a[mid], so none of them can be the target and low = mid + 1 is safe. When a[mid] > target, the "
                  "same argument applies to everything from mid upward, so high = mid - 1 is safe. Because mid itself is "
                  "always excluded, the interval shrinks every iteration and the loop must end. If it ends with low > high, "
                  "the interval is empty, and the invariant says the target was never there."),
        ),
        tradeoff=dict(
            title="Why halving gives log n",
            text=("Each iteration removes at least half of the remaining interval, so after k steps at most n / 2^k "
                  "candidates are left. The loop stops once that drops below one, which takes about log2 n iterations: "
                  "O(log n) time. Space is O(1) because only low, high and mid are stored. The catch is the sorted "
                  "precondition. Sorting once costs O(n log n), which pays off only when you search the same data many "
                  "times; for a single lookup in unsorted data a linear scan is cheaper. Computing mid as "
                  "low + (high - low) / 2 avoids int overflow on huge arrays. With duplicates, this version returns "
                  "whichever match it hits first, not necessarily the first occurrence."),
        ),
        pitfall=("Writing low = mid or high = mid in this inclusive version. When the interval has two elements, mid equals "
                 "low, so low = mid leaves the interval unchanged and the loop never ends. Test any variant on a two-element "
                 "array with the target absent."),
        prerequisiteNotes={
            'concept-sorting': "Binary search is only valid on sorted input, and the sort it depends on usually costs more than the search.",
        },
    ),

    'lesson-merge-sort': dict(
        body=("Imagine sorting a tall stack of exam papers with a friend. You split the stack, each of you sorts half, and "
              "then you merge: look at the top paper of each sorted pile and take whichever comes first, again and again. "
              "Merge sort applies that split recursively until every pile holds one paper, which is sorted by definition. All "
              "of the real work happens in the merges. Each merge only compares the two front items, because in a sorted pile "
              "nothing behind the front can come earlier. In the animation, notice that splitting changes nothing in the "
              "array; values only move when a merge commits its buffer back. Watch the buffer fill one value at a time and "
              "count how many values each level of merging touches."),
        worked=dict(
            title="From pairs to the final merge",
            text=("The input 4, 2, 7, 1, 3, 6 is split at mid = 2 into indexes 0 to 2 and 3 to 5, and the left part is split "
                  "again until 4 and 2 stand alone. Their merge takes 2, then 4, and the array becomes 2, 4, 7, 1, 3, 6. "
                  "Merging 2, 4 with 7 takes all three in order and changes nothing. The right part repeats the pattern: 1 "
                  "and 3 merge in order, then 1, 3 merges with 6, again unchanged. A merge still runs when values are already "
                  "in order; the algorithm cannot know that without comparing. The final merge fills a buffer of 6 values "
                  "from the fronts of 2, 4, 7 and 1, 3, 6, taking 1, 2, 3, 4, 6, then draining 7, and the array becomes "
                  "1, 2, 3, 4, 6, 7."),
        ),
        invariant=dict(
            title="The buffer prefix is already final",
            text=("During a merge, the buffer holds the smallest values consumed so far, in sorted order, and the unconsumed "
                  "parts of both runs are still sorted. Each step compares only a[i] and b[j]. Every other unconsumed value "
                  "sits behind one of those fronts, so it is at least as large as a front. The smaller front is therefore the "
                  "smallest value left anywhere, and appending it keeps the buffer sorted. When one run empties, the rest of "
                  "the other run is no smaller than anything in the buffer, so copying it in order is safe. A single value is "
                  "sorted, and every merge combines two runs that smaller merges already sorted, so the top merge produces a "
                  "fully sorted array."),
        ),
        tradeoff=dict(
            title="Where n log n comes from",
            text=("Halving the interval each time gives about log2 n levels of splitting. On each level the merges together "
                  "touch every value once, so each level costs O(n) and the whole sort costs O(n log n). That holds for every "
                  "input, sorted or reversed, which is the main reason to choose merge sort over quicksort: no bad cases. The "
                  "price is the O(n) buffer each merge writes into; heapsort or quicksort sort in place instead. Taking from "
                  "the left run on ties, the <= in merge, keeps equal values in their original order, so the sort is stable. "
                  "For very small arrays insertion sort is often faster in practice. Merge sort also suits linked lists and "
                  "data too large for memory, where sequential merging is cheap."),
        ),
        pitfall=("Comparing with < instead of <= when the fronts are equal. The output is still sorted, but equal keys from "
                 "the right run jump ahead of those from the left, so the sort stops being stable. Also check the two drain "
                 "loops: when one run empties, the rest of the other must still be copied, or values silently disappear."),
        prerequisiteNotes={
            'concept-arrays': "Merging copies values by index into a new array, and each split works on a range of array positions.",
        },
    ),

    'lesson-quick-sort': dict(
        body=("Picture lining people up by height using one person as a reference. Everyone shorter or equal steps to the "
              "left, everyone taller to the right. The reference person is now standing exactly where they belong in the "
              "final line, even though neither group is sorted yet. Quicksort repeats this on each group. The step that does "
              "the work is the partition: one scan with a boundary that marks the end of the small values found so far. In "
              "the animation, watch the boundary. It advances only when a scanned value is no larger than the pivot, and a "
              "value moves only when it has to jump over a larger one. After each partition, check that the pivot never moves "
              "again."),
        worked=dict(
            title="Three partitions sort the row",
            text=("With 4, 2, 7, 1, 3, 6 the last value, 6, is the first pivot. 4 and 2 are no larger, so the boundary passes "
                  "over them without moving anything. 7 is larger and stays put. Then 1 swaps with 7, giving 4, 2, 1, 7, 3, 6, "
                  "and 3 swaps with 7, giving 4, 2, 1, 3, 7, 6. The pivot swaps into index 4: 4, 2, 1, 3, 6, 7. The right side "
                  "holds only 7, so it is done. The left side uses pivot 3: 4 stays, 2 and then 1 swap past it, and 3 lands at "
                  "index 2, giving 2, 1, 3, 4, 6, 7. Finally pivot 1 lands at index 0 and the row is 1, 2, 3, 4, 6, 7. Each "
                  "partition placed its pivot for good."),
        ),
        invariant=dict(
            title="What the boundary guarantees",
            text=("During a partition, every value left of the boundary is no larger than the pivot, every value between the "
                  "boundary and the scan position is larger, and everything past the scan is unexamined. A small value found "
                  "by the scan swaps to the boundary and the boundary advances, so both regions stay correct. When the scan "
                  "reaches the pivot, swapping the pivot to the boundary puts every smaller-or-equal value on its left and "
                  "every larger value on its right. That is exactly its sorted position, so it never moves again. Each "
                  "recursive call works on a strictly smaller range, and a range of zero or one value is already sorted, so "
                  "the process ends with every value placed."),
        ),
        tradeoff=dict(
            title="Why the pivot decides the cost",
            text=("One partition scans its range once, so it costs time proportional to the range. If pivots split ranges "
                  "roughly in half, there are about log n levels and each level scans about n values in total: O(n log n) on "
                  "average. If the pivot is always the largest or smallest value, as a last-element pivot is on sorted input, "
                  "each partition peels off one value, giving n levels and O(n²) comparisons. Recursion depth is the space "
                  "cost: O(log n) on average, up to n frames in the bad case. A random pivot makes the bad case unlikely; "
                  "choose merge sort when you need a guaranteed bound or stability, since quicksort is not stable. It is often "
                  "fastest in practice because it sorts in place."),
        ),
        pitfall=("Recursing on a range that still includes the placed pivot. The range may not shrink and the recursion never "
                 "ends. Also expect a last-element pivot to degrade to quadratic time on input that is already sorted: every "
                 "partition then places only the largest value."),
        prerequisiteNotes={
            'concept-arrays': "Partitioning swaps values in place by index, so you need to read and swap array positions with confidence.",
        },
    ),

    'lesson-linked-list': dict(
        body=("Think of a scavenger hunt where each clue tells you where the next one is hidden. You cannot jump to the fifth "
              "clue; you have to follow the chain from the start. A singly linked list works the same way: each node stores a "
              "value and a reference to the next node, and the list is reachable only through its head. Inserting or removing "
              "next to a node you already hold is cheap, because you only rewrite references, but reaching a position is slow. "
              "Reversing the list is the classic exercise because it forces you to rewrite every arrow without losing your "
              "grip on the rest of the chain. In the animation, watch the three markers for previous, current and next, and "
              "notice that the values never move. Only the arrows change direction."),
        worked=dict(
            title="Six link flips, one per node",
            text=("The chain is 4, 2, 7, 1, 3, 6, and previous starts as null, shown as -1. In the first step current is the "
                  "node holding 4. Its next node, 2, is saved first, then the arrow from 4 is pointed at null, and the markers "
                  "advance so previous is 4 and current is 2. The same three moves repeat: 2 now points back to 4, then 7 "
                  "back to 2, then 1 to 7, then 3 to 1. In the sixth step current is 6, the old tail; the saved next is null, "
                  "6 is pointed at 3, and current falls off the end. previous now holds 6, which is returned as the new head, "
                  "and following the arrows gives 6, 3, 1, 7, 2, 4."),
        ),
        invariant=dict(
            title="Two lists that never overlap",
            text=("At the top of every loop iteration the nodes form two separate lists. prev heads the part already "
                  "reversed, which runs backwards from the most recent node to the original head and ends in null. current "
                  "heads the untouched remainder, still linked in its original direction. No node belongs to both and none is "
                  "lost. One iteration moves exactly one node from the front of the remainder to the front of the reversed "
                  "part. Saving current.next before overwriting it is what keeps the remainder reachable. When current "
                  "becomes null the remainder is empty, so prev heads the whole list, reversed."),
        ),
        tradeoff=dict(
            title="Linear time, constant extra space",
            text=("The loop visits each node once and does a fixed amount of work there: one read and three reference writes. "
                  "That gives O(n) time. The only extra storage is the three references prev, current and next, whatever the "
                  "length, so the auxiliary space is O(1). A recursive reversal is shorter to write but uses one stack frame "
                  "per node, O(n) space, and can overflow on long lists. Copying values into an array and writing them back "
                  "also works but costs O(n) space and surprises anyone holding a reference to a particular node. Check the "
                  "edges: an empty list returns null, and a one-node list returns itself. On a list with a cycle the loop "
                  "never ends."),
        ),
        pitfall=("Writing current.next = prev before saving current.next. The moment that arrow changes, the rest of the list "
                 "is unreachable and the loop stops after one node. A related slip is returning current instead of prev: when "
                 "the loop ends, current is always null."),
        prerequisiteNotes={
            'concept-arrays': "Contrasting with arrays shows what a list gives up: no index jumps, so reaching a node means following links.",
        },
    ),

    'lesson-stack': dict(
        body=("Think of a stack of plates. You add a plate to the top and take a plate from the top; the ones underneath wait "
              "until everything above them is gone. That rule, last in first out, fits every situation where the most recent "
              "unfinished thing must be finished first: undo history, matching brackets, returning from nested function calls "
              "and depth-first search. A stack never lets you look inside or reorder it, and that restriction is what makes it "
              "useful, because the top always tells you what to handle next. In the animation, the values go in one order and "
              "come out in the opposite order. Notice that the first value pushed stays at the bottom until everything above "
              "it has been popped."),
        worked=dict(
            title="Six pushes, then six pops",
            text=("The values 4, 2, 7, 1, 3, 6 are pushed one at a time, and the size climbs from 1 to 6 with each new value "
                  "landing on top. When the last push finishes, 6 is on top and 4 is at the bottom. Popping then removes 6 "
                  "first, leaving 4, 2, 7, 1, 3. The next pops remove 3, then 1, then 7, then 2, each time taking whatever is "
                  "on top. The last pop removes 4, and the stack is empty with size 0. The pop order 6, 3, 1, 7, 2, 4 is the "
                  "push order reversed. Nothing was sorted or compared; the order came entirely from when each value arrived."),
        ),
        invariant=dict(
            title="The top is the newest survivor",
            text=("At every moment the top of the stack is the value pushed most recently among those not yet popped, and the "
                  "values below it are in push order from the bottom up. A push puts the new value above the old top, which "
                  "keeps that true. A pop removes the top and exposes the value pushed immediately before it, which is now the newest "
                  "survivor. Because each operation touches only the top, the rest of the stack is never disturbed. That is "
                  "why popping everything returns the exact reverse of the push order, and why a stack can remember where you "
                  "were in nested work: the innermost open item is always on top."),
        ),
        tradeoff=dict(
            title="Constant work at one end",
            text=("Each push and pop touches only the top, so it does a fixed amount of work. ArrayDeque keeps its values in a "
                  "resizable array; when the array is full it copies everything into a larger one, which is occasionally O(n) "
                  "but averages out to O(1) per operation. Pushing and popping n values therefore costs O(n) time, and holding "
                  "them costs O(n) space. ArrayDeque behind the Deque interface is the usual choice in Java. Check isEmpty "
                  "before pop, because pop on an empty ArrayDeque throws an exception rather than returning a value. If you "
                  "need the oldest item first instead of the newest, you want a queue."),
        ),
        pitfall=("Popping without checking isEmpty first. On an empty ArrayDeque, pop throws an exception, and the bug usually "
                 "means an earlier step pushed too little or popped too much. In bracket matching, a closing bracket with "
                 "nothing on the stack is an answer to report, not a crash."),
        prerequisiteNotes={
            'concept-arrays': "ArrayDeque keeps the stack in an array that grows when full, which explains the amortized O(1) cost.",
        },
    ),

    'lesson-queue': dict(
        body=("A queue is the line at a ticket counter. People join at the back and are served from the front, so whoever has "
              "waited longest goes next. That first in, first out rule is what you want when order of arrival must be "
              "respected: print jobs, requests to a server, and the frontier in breadth-first search, where vertices must be "
              "processed in the order they were discovered. Java's ArrayDeque can act as a queue or a stack depending on which "
              "ends you use, so the discipline lives in your choice of methods, not in the container. In the animation, "
              "compare this with the stack lesson: the same six values go in, but they come out in the same order rather than "
              "reversed."),
        worked=dict(
            title="First in is first out",
            text=("The values 4, 2, 7, 1, 3, 6 are added at the back one at a time, and the size grows from 1 to 6. The front "
                  "is 4 the whole time because nothing has left yet. The first removal takes 4 from the front and leaves 2, 7, "
                  "1, 3, 6. The next removals take 2, then 7, then 1, then 3, and the final one takes 6, leaving the queue "
                  "empty with size 0. The removal order 4, 2, 7, 1, 3, 6 matches the arrival order exactly. Had the same "
                  "values been taken from the back instead, they would have come out reversed, which is the stack's behaviour."),
        ),
        invariant=dict(
            title="The front waited longest",
            text=("At every moment the front of the queue is the earliest-added value that has not been removed, and the "
                  "values behind it are in arrival order. addLast puts a new value behind everything already waiting, so it "
                  "cannot overtake anyone. removeFirst takes the front, which exposes the next-oldest value. Neither operation "
                  "changes the relative order of the values in between. This is why breadth-first search finds fewest-edge "
                  "distances: every vertex at distance d is enqueued before any vertex at distance d + 1, so the queue hands "
                  "them out layer by layer."),
        ),
        tradeoff=dict(
            title="Two ends, both constant time",
            text=("ArrayDeque keeps its values in a circular array with a head index and a tail index. Adding at the back and "
                  "removing from the front each move one index, so they cost O(1); when the array fills, it is copied into a "
                  "larger one, which averages out to O(1) per operation. Processing n values therefore takes O(n) time and up "
                  "to O(n) space while they wait. An ArrayList used as a queue is a common slow alternative, because removing "
                  "index 0 shifts every remaining element and makes each removal O(n). If items should leave by priority "
                  "rather than arrival, use a priority queue. Check isEmpty before removeFirst, which throws on an empty deque."),
        ),
        prerequisiteNotes={
            'concept-arrays': "ArrayDeque stores the queue in a circular array, so knowing how arrays grow explains the amortized O(1) cost.",
            'concept-stacks': "A queue is easiest to understand next to a stack: the same container, the opposite removal end, the opposite order.",
        },
    ),

    'lesson-recursion': dict(
        body=("Picture a line of people passing a question along: each person asks the next one an easier version and waits, "
              "notes in hand, until the answer comes back. The last person can answer without asking anyone. Then the answers "
              "travel back, and each person finishes their own part using the answer they received. A recursive function works "
              "this way. Each call gets its own frame on the call stack, holding its own copy of n, and stays paused until the "
              "smaller call returns. Every recursive function needs a base case that answers directly and a call that moves "
              "toward it. In the animation, the column of frames is the call stack. Notice that it grows first with no "
              "multiplying at all, and every multiplication happens while the stack shrinks."),
        worked=dict(
            title="Five frames wait for the base case",
            text=("The animation computes factorial(5). The first call cannot answer yet, so it pauses and calls "
                  "factorial(4), which pauses and calls factorial(3), and so on. After five calls the stack holds frames for 5, "
                  "4, 3, 2 and 1, and the call for 0 is pushed on top. That call hits the base case and returns 1 without "
                  "recursing. Its frame is popped, and the frame for 1 resumes: 1 times 1 is 1. Each paused frame then resumes "
                  "in turn, newest first: 2 times 1 gives 2, 3 times 2 gives 6, 4 times 6 gives 24, and 5 times 24 gives 120. "
                  "The stack is empty again and the result is 120."),
        ),
        invariant=dict(
            title="Each frame trusts the smaller call",
            text=("factorial(n) returns n times factorial(n - 1), and factorial(0) returns 1. To see that every call returns "
                  "the right answer, argue by induction on n. The base case is correct by definition. If factorial(n - 1) "
                  "returns (n - 1)!, then n times it is n!, so factorial(n) is correct too. Termination comes from the argument "
                  "shrinking by one each call, so it must reach 0. While a call is paused, its local n is safe in its own "
                  "frame; the smaller calls get their own frames and cannot overwrite it. That is why the frame for 5 still "
                  "multiplies by 5 after four deeper calls have come and gone."),
        ),
        tradeoff=dict(
            title="Paying for the waiting frames",
            text=("factorial(n) makes n + 1 calls, each doing one comparison and at most one multiplication, so the time is "
                  "O(n). The space is also O(n), not because of any array but because up to n + 1 frames are alive at once on "
                  "the call stack. That stack is limited, and very deep recursion crashes with a stack overflow. A loop that "
                  "multiplies 1 through n gives the same answer in O(1) space, and Java does not optimise tail calls, so for a "
                  "simple linear recursion like this a loop is the safer choice. Recursion pays off when the problem branches, "
                  "as in trees and backtracking. The Java rejects negative n, which has no base case to reach, and caps n at "
                  "10 to keep the example small."),
        ),
        prerequisiteNotes={
            'concept-stacks': "Each call pushes a frame and each return pops one, so the call stack follows the same last-in, first-out rule.",
        },
    ),

    'lesson-backtracking': dict(
        body=("Imagine exploring a maze with a ball of string. At each fork you pick a corridor and keep unrolling string. "
              "When a corridor ends, you wind the string back to the last fork and try the next corridor. You never need a "
              "second ball of string, because winding back restores exactly where you were. Backtracking explores every "
              "combination of choices the same way: one shared path list, an add before exploring a branch and a remove after "
              "it. Generating all subsets is the cleanest example, since each value is either in or out. In the animation, "
              "watch the path grow and shrink like the string. Every undo should restore the path to exactly what it was "
              "before the matching choice, and every recorded subset is a copy, not the live path."),
        worked=dict(
            title="Following the path through the trace",
            text=("The trace begins by recording the empty path. It then chooses values in input order and records each path "
                  "on the way down: 4, then 4, 2, then 4, 2, 7, then 4, 2, 7, 1, then 4, 2, 7, 1, 3. Nothing is left to add, so "
                  "it undoes 3 and then 1, returning to 4, 2, 7, and records 4, 2, 7, 3. Undoing 3 and 7 brings it back to "
                  "4, 2, which leads to 4, 2, 1, then 4, 2, 1, 3, then 4, 2, 3. Removing 2 leaves 4, and the next branch is "
                  "4, 7. A long stretch continues the same way. Near the end the path visits 7, 3, then 1 and 1, 3, then 3 "
                  "alone, and the final undo leaves it empty. This trace uses only the first five values, so 6 never joins "
                  "the path."),
        ),
        invariant=dict(
            title="Undo restores the parent exactly",
            text=("Whenever a call starts, the shared path holds exactly the choices made on the way from the root of the "
                  "decision tree to this call, and nothing else. Each call that adds a value removes that same value before it "
                  "returns, so the path is handed back to its caller unchanged. That is what lets siblings share one list: the "
                  "second branch starts from the same path the first branch started from. In the Java, visit(i) is entered "
                  "with path holding the chosen values among indices below i, so when i reaches a.length the path is one "
                  "complete subset and a copy goes into out. Each subset matches one root-to-leaf route, so none is missed "
                  "or repeated."),
        ),
        tradeoff=dict(
            title="Exponential output, linear working space",
            text=("With n distinct values there are 2^n subsets, because each value is independently in or out. You cannot do "
                  "better than producing all of them, and copying each one costs up to n, so the time is O(n × 2^n). The "
                  "working space is small: the path holds at most n values and the recursion is at most n + 1 calls deep, so "
                  "O(n) auxiliary space. The output itself is O(n × 2^n). That growth is why backtracking suits only small n; "
                  "at 30 values there are over a billion subsets. If you need only a count or the best subset, look for "
                  "pruning or dynamic programming instead. With duplicate values this code produces repeated subsets, so sort "
                  "and skip equal siblings when that matters."),
        ),
        prerequisiteNotes={
            'concept-recursion': "Each choice is a recursive call, and returning from it is the moment the path must be restored.",
        },
    ),

    'lesson-tree-traversal': dict(
        body=("A family tree has a person at the top and branches below, and there is no single obvious order to read it in. "
              "Tree traversal gives you rules for that order. The recursive shape is always the same: handle the left "
              "subtree, the node itself and the right subtree, and the three classic orders differ only in where the node "
              "goes. Preorder visits the node first, inorder in the middle, postorder last. Inorder matters most for binary "
              "search trees, where it reads values in sorted order, but the rule itself knows nothing about values; it only "
              "follows links. In the animation, watch frames open and close. A node is emitted only after its whole left "
              "subtree has finished, and its frame stays open until its right subtree is done too."),
        worked=dict(
            title="Left, node, right on this tree",
            text=("The input 4, 2, 7, 1, 3, 6 is read as level-order slots: 4 is the root, 2 and 7 are its children, 1 and 3 "
                  "hang under 2, and 6 is the left child of 7. The walk enters 4, then 2, then 1. Node 1 has no left child, so "
                  "it emits 1 and returns. Back in 2, the left side is done, so it emits 2, then enters 3, emits 3 and "
                  "returns. Node 2 returns to 4, which emits 4 and turns right. It enters 7, then 6, emits 6 and returns. Node "
                  "7 emits 7, has no right child, and returns, and finally 4 returns. The output is 1, 2, 3, 4, 6, 7. It is "
                  "sorted because this tree happens to satisfy the search-tree ordering, not because inorder sorts anything."),
        ),
        invariant=dict(
            title="A subtree finishes before moving on",
            text=("When walk returns from a node, out has gained exactly the values of that node's subtree, in inorder, and "
                  "nothing else. For an empty subtree this holds trivially, because walk returns at once. For a real node, the "
                  "first recursive call adds its whole left subtree in order, then out.add places the node, then the second "
                  "call adds the right subtree. Each subtree is smaller, so the claim follows by induction from the leaves "
                  "up, and calling walk on the root lists every node exactly once. The order depends only on the shape of the "
                  "links. If the tree also has the search-tree property, that order is sorted."),
        ),
        tradeoff=dict(
            title="Linear time, height-deep stack",
            text=("walk is called once for each node and once for each null child, and a tree with n nodes has n + 1 null "
                  "links, so there are 2n + 1 calls doing constant work each: O(n) time. The space that matters is the call "
                  "stack, which holds one frame per node on the current root-to-leaf path, so O(h) where h is the height. For "
                  "a balanced tree h is about log n; for a tree that degenerates into a chain h is n, and a deep enough chain "
                  "can overflow the stack. An explicit stack in a loop avoids that limit, and level order needs a queue "
                  "instead. The output list adds O(n). height uses the same pattern and counts nodes, so the empty tree has "
                  "height 0."),
        ),
        prerequisiteNotes={
            'concept-linked-lists': "A tree node is a linked-list node with two next references, so following and null-checking links carries over.",
            'concept-recursion': "walk calls itself on each child and resumes the parent's frame afterwards, which is the suspended-frame idea.",
        },
    ),

    'lesson-heap': dict(
        body=("Think of a company org chart where every manager earns more than the people who report directly to them. You "
              "can see the top earner at a glance, but nothing tells you whether someone in one department earns more than "
              "someone in another. A max-heap keeps exactly that weak order: every parent is at least as large as its "
              "children, so the maximum is always at the root. Because the tree is complete, it packs into an array with no "
              "gaps. That partial order is cheaper to maintain than full sorting, which is why heaps power priority queues. In "
              "the animation, follow the newly inserted value. It only ever moves up its own path toward the root, and it "
              "stops at the first parent that is at least as large."),
        worked=dict(
            title="Six insertions, three swaps",
            text=("Inserting 4 makes it the root. 2 lands at index 1; its parent at index 0 holds 4, which is larger, so "
                  "nothing moves. 7 lands at index 2, its parent 4 is smaller, so they swap and the array is 7, 2, 4 with 7 at "
                  "the root. 1 lands at index 3 under 2 and stays. 3 lands at index 4, beats its parent 2 at index 1 and "
                  "swaps up, giving 7, 3, 4, 1, 2; the next comparison with 7 stops it. Finally 6 lands at index 5, beats its "
                  "parent 4 at index 2 and swaps, giving 7, 3, 6, 1, 2, 4, and 7 stops it again. The root is the maximum, but "
                  "the array is not sorted in either direction."),
        ),
        invariant=dict(
            title="Only one path can break",
            text=("Before each insertion, every parent in the array is at least as large as its children. Adding a value at "
                  "the end can break that rule in one place only: between the new value and its parent. If the parent is at "
                  "least as large, the heap is valid and the loop breaks. If not, swapping fixes that pair, and the value that "
                  "moves down was already the parent of that position, so it is still at least as large as anything below it. "
                  "The only possible violation has moved one level up the same path. Repeating this ends at a large-enough "
                  "parent or at index 0, and either way the whole array is a valid heap again, with the maximum at the root."),
        ),
        tradeoff=dict(
            title="Height bounds every insertion",
            text=("A complete tree with n nodes has height about log2 n, and an inserted value climbs at most that many "
                  "levels, comparing and maybe swapping once per level. So one insertion costs O(log n), and inserting n "
                  "values one by one costs O(n log n). The array holds every value once, O(n) space, with no child references "
                  "because index arithmetic replaces them. Use a heap when you repeatedly need the current maximum while "
                  "values keep arriving. If you need everything in order once, sort instead; searching a heap for an "
                  "arbitrary value is O(n). Building a heap bottom-up from a full array is O(n), faster than repeated "
                  "insertion. Equal values are fine: the >= check stops the climb."),
        ),
        prerequisiteNotes={
            'concept-sorting': "Comparing with a full sort shows what a heap gives up: only the maximum is in place, so insertion is cheaper.",
            'concept-binary-trees': "The heap is a complete binary tree stored in an array, so parent and child positions come from tree shape.",
        },
    ),
}

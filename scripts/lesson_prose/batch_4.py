PROSE = {
    'lesson-bits': dict(
        body="Every int is stored as 32 bits, and the bitwise operators work on all of them at once. AND keeps a bit only where both inputs have it, OR keeps it where either has it, and XOR keeps it where exactly one has it. Two facts about XOR do most of the work in this lesson: a value XORed with itself gives 0, and XOR with 0 changes nothing. Because XOR is also order-independent, a list in which every value but one appears twice collapses to that one value. A second trick, n & (n-1), removes the lowest set bit of n, so repeating it counts the set bits in as many steps as there are ones. In the animation, watch the binary row of the accumulator: each incoming value flips exactly the bits where it has a 1.",
        worked=dict(
            title="Pairs cancel, one value remains",
            text="The input is 4, 1, 2, 1, 2 and the accumulator starts at 0. XOR with 4 gives 4, binary 100. XOR with 1 switches on the last bit: 101, which is 5. XOR with 2 switches on the middle bit: 111, which is 7. The second 1 switches the last bit off again: 110, which is 6. The second 2 switches the middle bit off: 100, which is 4. Both pairs have undone themselves and 4 is the answer. The animation then counts the set bits of 4 with the second trick: 4 - 1 is 011, and 100 & 011 is 0, so the loop runs once and 4 has 1 set bit. A value with more ones takes more steps: for 6, binary 110, 6 & 5 gives 4 and 4 & 3 gives 0, two steps for two set bits.",
        ),
        invariant=dict(
            title="The accumulator holds the odd ones out",
            text="After reading any prefix of the list, the accumulator equals the XOR of that prefix. Because XOR is associative and commutative, that is the same as XORing each distinct value once for every time it has appeared, and a value XORed an even number of times contributes 0. So the accumulator is the XOR of exactly the values seen an odd number of times. When every value but one occurs twice, only that one is odd at the end. For counting, each n & (n-1) step clears exactly one set bit and leaves every other bit unchanged, because n-1 differs from n only at and below its lowest one. The loop therefore runs once per set bit and stops at 0.",
        ),
        tradeoff=dict(
            title="One word of memory, narrow conditions",
            text="The XOR scan is O(n) time with O(1) extra space, which beats a hash map of counts, O(n) space, and sorting, O(n log n) time. The price is that it only works under its exact promise: if one value appears three times, or two values appear once, the result mixes them together. Variants exist, such as splitting by a set bit to find two singles, but each needs its own argument. Counting with n & (n-1) costs one step per set bit, so it is fast for sparse values; library calls such as Integer.bitCount use a constant number of operations or a single CPU instruction. Bit tricks also cost readability, so name them in helper methods.",
        ),
        pitfall="Mind Java's two right shifts. >> copies the sign bit, so shifting a negative int never reaches 0 and a loop waiting for it runs forever; >>> shifts in zeros. Operator precedence also bites: x & 1 == 0 parses as x & (1 == 0) and does not compile for ints, so write (x & 1) == 0.",
        objectives=[
            "Use XOR to cancel paired values and explain why order does not matter.",
            "Clear the lowest set bit with n & (n-1) and count set bits with it.",
        ],
        prerequisiteNotes={
            'concept-arrays': "The XOR scan is a single pass over an array that keeps one running result, like a running sum.",
        },
    ),
    'lesson-union-find': dict(
        body="Some questions about a graph arrive while the graph is still growing: after these connections, are a and b linked? Running a search after every new edge repeats almost all the work. Union-find keeps each connected group as a small tree inside a parent array, where the root of the tree names the group. find walks from a vertex up to its root, and union attaches one root beneath the other. Two refinements keep the trees flat: union by size hangs the smaller tree under the larger, and path halving makes vertices point closer to the root as find walks past them. In the animation, notice that union always works on roots, never on the two vertices it was given, and watch the component count fall by one on every merge that joins two different groups.",
        worked=dict(
            title="Four unions, two groups",
            text="There are 6 vertices, each its own root, so 6 groups. Union 0 and 1: the roots are 0 and 1 with size 1 each, so 1 is hung under 0 and 5 groups remain. Union 2 and 3 does the same with 3 under 2, leaving 4 groups. Union 1 and 2 first finds roots: 1 leads to 0, and 2 is its own root. Both trees have size 2, so root 2 is hung under 0, which now heads a group of 4, and 3 groups remain. Union 4 and 5 hangs 5 under 4, leaving 2 groups. The parent array is now [0, 0, 0, 2, 4, 4]. A later find on 3 walks 3, 2, 0 and halves the path, so 3 then points straight at 0. The answer is 2 groups: {0, 1, 2, 3} and {4, 5}.",
        ),
        invariant=dict(
            title="One root per group",
            text="Every vertex reaches exactly one root by following parent links, and two vertices have the same root precisely when the unions so far connect them. The links never form a cycle, because union only ever points one root at another root, and a root points at itself. Merging two groups changes exactly one parent entry, so every vertex in the absorbed tree inherits the new root without being touched. Path halving changes parents too, but each change points a vertex at its grandparent, which lies on the same path to the same root, so group membership is unchanged. Union by size ensures a vertex moves one level deeper only when its group at least doubles, so no tree is taller than log2 n even before path halving.",
        ),
        tradeoff=dict(
            title="Almost constant, but only for merging",
            text="With union by size and path compression or halving together, any sequence of m operations on n items takes O(m α(n)) time, where α is the inverse Ackermann function and stays below 5 for any input that fits in a computer. Space is two arrays of n integers. That makes union-find the tool of choice when connections only ever get added, such as Kruskal's algorithm or counting components as edges stream in. It cannot answer what path joins two vertices, and it cannot remove an edge; deleting connections needs other structures or rebuilding. For a single static question about connectivity, one BFS or DFS over the whole graph costs O(V + E) and is just as good.",
        ),
        pitfall="The most common bug is linking the vertices themselves, parent[a] = b, instead of their roots. It splits a group in two whenever a was not a root. Always call find on both arguments first, and return early when the roots are equal, or the component count drops for a union that merged nothing.",
        objectives=[
            "Merge groups and test whether two items share a group in near-constant time.",
            "Explain how union by size and path halving keep the trees shallow.",
        ],
        prerequisiteNotes={
            'concept-arrays': "The whole forest lives in a parent array and a size array indexed by vertex number.",
            'concept-graphs': "Each union adds an undirected edge, and the groups are the graph's connected components.",
        },
    ),
    'lesson-topological-sort': dict(
        body="Courses with prerequisites, build targets with inputs and tasks with dependencies all ask the same question: in what order can everything be done so that each item comes after the items it needs? Model each item as a vertex and each requirement u before v as a directed edge u to v. Kahn's algorithm counts the edges coming into every vertex. A vertex with no incoming edges can go first, so it is placed in a queue. Placing a vertex removes its outgoing edges, which lowers the counts of its successors, and any successor that reaches zero joins the queue. If some vertices never reach zero, they are stuck on a cycle and no valid order exists. In the animation, follow the indegree row and the queue together: a vertex enters the queue at the moment its count becomes 0.",
        worked=dict(
            title="Freeing vertices one edge at a time",
            text="The edges are 0 to 2, 1 to 2, 2 to 3, 3 to 4 and 1 to 4, on 5 vertices. Counting incoming edges gives indegrees 0, 0, 2, 1 and 2. Vertices 0 and 1 start in the queue. Placing 0 removes the edge into 2, whose count drops to 1. Placing 1 removes its edges into 2 and 4: vertex 2 reaches 0 and joins the queue, and vertex 4 drops to 1. Placing 2 brings 3 to 0. Placing 3 brings 4 to 0. Placing 4 changes nothing. All 5 vertices were placed, so the graph has no cycle, and the order is 0, 1, 2, 3, 4. Every edge points forward in it: for example, 1 to 4 goes from position 1 to position 4.",
        ),
        invariant=dict(
            title="A vertex waits for all its predecessors",
            text="A vertex's remaining indegree always equals the number of its predecessors that have not been placed yet. It enters the queue exactly when that number reaches zero, so every vertex is placed after all of its predecessors, and every edge points forward in the output. Each vertex enters the queue at most once, because its count can reach zero only once. The algorithm also proves when no order exists: on a cycle, each vertex waits for the one before it, so none of them can ever reach zero. Hence, if the output has fewer than n vertices, the leftovers include a cycle or depend on one, and the right answer is to report it rather than return a partial order.",
        ),
        tradeoff=dict(
            title="Linear time, many valid orders",
            text="Counting indegrees reads every edge once, and each vertex and edge is processed once more when placed, so Kahn's algorithm runs in O(V + E) time with O(V) space for the counts and the queue, plus the graph itself. A depth-first search that records vertices as they finish, then reverses that list, gives a topological order with the same bounds; it suits recursive code but needs extra colours to detect cycles. Most graphs have many valid orders. A FIFO queue gives one of them; a priority queue gives the lexicographically smallest at O(V log V) extra cost, which matters when the output must be reproducible. Neither approach works on a graph with cycles; those need strongly connected components first.",
        ),
        pitfall="Watch the edge direction. A prerequisite pair written as [course, needs] means the edge goes from needs to course; reversing it produces a valid order of the wrong graph. Also do not stop at the first empty queue without comparing the count of placed vertices with n, or a cycle silently produces a short answer.",
        objectives=[
            "Order the vertices of a directed acyclic graph so that every edge points forward.",
            "Detect a cycle when some vertices never reach indegree zero.",
        ],
        prerequisiteNotes={
            'concept-bfs': "Kahn's algorithm uses the same FIFO queue of discovered vertices, releasing a vertex when its last incoming edge is removed.",
        },
    ),
    'lesson-kruskal': dict(
        body="Suppose several sites must all be connected, every possible link has a cost, and the total cost must be as small as possible. The cheapest network that connects everything is a tree, because any cycle contains an edge that could be removed while keeping everything connected. Kruskal's algorithm builds that minimum spanning tree greedily. It sorts the edges from cheapest to dearest and considers each in turn. An edge that joins two vertices already connected would form a cycle, so it is skipped; any other edge is taken and its two components merge. Union-find answers the connected question in nearly constant time. In the animation, the taken edges first form several separate pieces, which grow and merge until n - 1 edges hold every vertex together.",
        worked=dict(
            title="Six edges, four taken",
            text="The 5 vertices have edges 0-1 weight 4, 0-2 weight 1, 1-2 weight 2, 1-3 weight 5, 2-3 weight 8 and 3-4 weight 3. Sorted by weight, the order is 0-2, 1-2, 3-4, 0-1, 1-3, 2-3. Edge 0-2 joins two separate vertices, so it is taken: total 1. Edge 1-2 links 1 to that piece: total 3. Edge 3-4 starts a second piece: total 6. Edge 0-1 is skipped, because 0 and 1 are both already in the piece {0, 1, 2}. Edge 1-3 joins the two pieces: total 11, and 4 edges now connect all 5 vertices, so the tree is complete. Edge 2-3 with weight 8 is still examined and skipped, because 2 and 3 are now connected. The minimum spanning tree weighs 11.",
        ),
        invariant=dict(
            title="Every taken edge is safe",
            text="At each step, the edges taken so far belong to some minimum spanning tree. Suppose Kruskal takes edge e, joining components A and B. Take any minimum spanning tree T containing the earlier choices. If T lacks e, adding e to T creates a cycle, and that cycle must cross from A to the rest of the graph through another edge f. Because edges are considered in sorted order and f was not yet taken or rejected, f weighs at least as much as e. Swapping f for e gives a spanning tree no heavier than T, so it is also minimum and contains every choice so far. This exchange argument is the cut property, and it is why the greedy choice never needs to be undone.",
        ),
        tradeoff=dict(
            title="Sorting dominates",
            text="Sorting the E edges costs O(E log E), and the union-find pass is nearly linear, so Kruskal runs in O(E log E) time and O(V + E) space. It shines on sparse graphs given as edge lists. On dense graphs, where E is close to V squared, Prim's algorithm with an adjacency matrix runs in O(V squared) without listing every edge, and with a heap it runs in O(E log V). If the graph is disconnected, Kruskal naturally produces a minimum spanning forest, one tree per component, which this lesson's code reports as -1 because no single tree exists. With equal weights, several different minimum spanning trees can exist; they all share the same total.",
        ),
        pitfall="A minimum spanning tree is not a set of shortest paths. It minimises the total weight of the whole network, and the route between two particular vertices inside it can be much longer than their shortest path. If the question is about the cheapest route between two points, use Dijkstra or Bellman-Ford instead.",
        objectives=[
            "Build a minimum spanning tree by taking the cheapest edge that joins two components.",
            "Use union-find to reject edges that would close a cycle.",
        ],
        prerequisiteNotes={
            'concept-sorting': "The edges are processed in nondecreasing weight order, so the algorithm begins with a sort.",
            'concept-union-find': "Union-find decides in near-constant time whether an edge's two ends are already connected.",
        },
    ),
    'lesson-bellman-ford': dict(
        body="Dijkstra's algorithm settles each vertex once and never revisits it, which is only safe when no edge can reduce a cost. Some graphs have negative edges, such as refunds, energy regained or rewards, and then a settled distance can still improve. Bellman-Ford makes no such assumption. It relaxes every edge in a fixed order, and repeats. After the first pass, every shortest path that uses one edge is known; after the second, every one that uses at most two edges, and so on. A shortest path visits each vertex at most once, so n - 1 passes always suffice. If a further pass still improves something, a cycle with negative total weight is reachable and shortest paths do not exist. In the animation, watch a single pass lower the same vertex twice as better routes are found.",
        worked=dict(
            title="One busy pass, one quiet pass",
            text="The source is 0, so distances start as 0 for vertex 0 and infinity elsewhere. The first pass relaxes the edges in input order. 0 to 1 with weight 6 sets vertex 1 to 6. 0 to 2 with weight 7 sets vertex 2 to 7. 1 to 2 would give 6 + 8 = 14, worse than 7. 1 to 3 sets vertex 3 to 6 + 5 = 11. 2 to 3 with weight -3 gives 7 - 3 = 4, so vertex 3 drops to 4. 3 to 1 with weight -2 gives 4 - 2 = 2, so vertex 1 drops from 6 to 2. After one pass the distances are 0, 2, 7 and 4. The second pass tries every edge again: 1 to 3 would give 2 + 5 = 7, worse than 4, and 1 to 2 gives 10, worse than 7. Nothing changes, so no later pass can change anything either, and the answer is [0, 2, 7, 4].",
        ),
        invariant=dict(
            title="After k passes, k-edge paths are done",
            text="Every finite distance is always the length of some real path from the source, because a relaxation only copies a path length and adds one edge. After pass k, each distance is also at most the length of the shortest path that uses k edges or fewer: such a path ends with an edge from a vertex whose (k-1)-edge route was already known after the previous pass, and pass k relaxes that edge. Without negative cycles, some shortest path to each vertex has at most n - 1 edges, so n - 1 passes give exact distances, and a pass that changes nothing proves they are final. With a reachable negative cycle, going round it once more always helps, so every pass changes something, which is exactly the check the code makes on pass n.",
        ),
        tradeoff=dict(
            title="Slower than Dijkstra, but honest",
            text="Each pass relaxes all E edges, and there are at most V passes, so Bellman-Ford takes O(VE) time and O(V) space. Dijkstra with a heap takes O((V + E) log V), which is far faster on large graphs, but it gives wrong answers when an edge is negative. Stopping early when a pass changes nothing often cuts the work sharply, as in this lesson's input, where 2 passes are enough. Bellman-Ford also adapts to limits on the number of edges: running exactly k passes, each reading the previous pass's distances, finds the cheapest route with at most k edges. When negative edges exist but no negative cycles, Johnson's algorithm uses one Bellman-Ford run to reweight the graph and then runs Dijkstra from every vertex.",
        ),
        pitfall="Never add a weight to an infinite distance. With a large sentinel such as Long.MAX_VALUE, infinity plus a negative weight looks like a real, finite route, and infinity plus a positive weight overflows into a negative number. Skip edges whose source is still unreachable, as the code does, before comparing anything.",
        objectives=[
            "Find shortest paths from a source when some edge weights are negative.",
            "Detect a reachable negative cycle with one extra pass.",
        ],
        prerequisiteNotes={
            'concept-graphs': "The algorithm walks a list of directed, weighted edges and needs vertices numbered 0 to n-1.",
            'concept-dynamic-programming': "Pass k builds best k-edge distances from the best (k-1)-edge ones, a table filled in dependency order.",
        },
    ),
    'lesson-floyd-warshall': dict(
        body="Single-source algorithms answer how far every vertex is from one starting point. When the questions can start anywhere, running one of them from every vertex works but needs a heap and care with negative edges. Floyd-Warshall fills an n by n distance table directly. It starts with the direct edge weights, 0 on the diagonal and infinity where there is no edge. Then it lets vertex 0 serve as a stopover, then vertices 0 and 1, and so on: in round k, each entry d[i][j] is compared with d[i][k] + d[k][j], the route that passes through k. After the last round every vertex may be used as a stop, so the table holds all shortest distances. In the animation, highlight the row and column of k: only entries that can be improved through them change in that round.",
        worked=dict(
            title="Four rounds, three improvements",
            text="There are 4 vertices and the edges 0 to 1 weight 3, 1 to 2 weight 1, 0 to 2 weight 7 and 2 to 3 weight 2. The starting table holds those weights, with 0 on the diagonal and infinity everywhere else. Round 0 allows vertex 0 as a stop, but no edge leads into 0, so nothing improves. Round 1 allows vertex 1: from 0 to 2, going through 1 costs 3 + 1 = 4, which beats the direct 7, so d[0][2] becomes 4. Round 2 allows vertex 2: d[0][3] becomes 4 + 2 = 6, and d[1][3] becomes 1 + 2 = 3. Round 3 allows vertex 3, but no edge leaves 3, so nothing changes. Row 0 ends as [0, 3, 4, 6], and the distance from 0 to 3 is 6, along 0, 1, 2, 3.",
        ),
        invariant=dict(
            title="Rounds widen the allowed stops",
            text="After round k, d[i][j] is the length of the shortest path from i to j whose intermediate vertices all lie in 0 to k. Before any round, only direct edges qualify, which is the starting table. In round k, a shortest path that may now also use k either avoids k, and its length is already in d[i][j], or passes through k exactly once, splitting into a part from i to k and a part from k to j that use only vertices 0 to k-1 as stops; both parts are already in the table. Taking the minimum of the two cases keeps the statement true. Updating in place is safe, because round k never changes d[i][k] or d[k][j]: going through k to reach k cannot help without a negative cycle.",
        ),
        tradeoff=dict(
            title="Cubic time, tiny code",
            text="Three nested loops over n vertices give O(V cubed) time and O(V squared) space for the table, whatever the number of edges. For a dense graph of a few hundred vertices that is perfectly practical and simpler than running Dijkstra V times, which costs O(V (V + E) log V) and fails with negative edges. For large sparse graphs, V cubed becomes far too slow, and repeated Dijkstra or Johnson's algorithm wins. Floyd-Warshall handles negative edges without change, and a negative entry on the diagonal at the end reveals a negative cycle. Storing, for each pair, the vertex to visit next lets you rebuild the actual routes as well as their lengths.",
        ),
        pitfall="The loop over the stopover vertex k must be the outermost one. With i or j outside, an entry is finalised before the stops it needs have been considered, and the table quietly misses shorter routes. Also guard infinite entries before adding them: two large sentinels added together overflow an int and appear as a short negative distance.",
        objectives=[
            "Compute shortest distances between every pair of vertices with one table.",
            "Explain why the loop over intermediate vertices must be outermost.",
        ],
        prerequisiteNotes={
            'concept-graphs': "The input is a set of directed weighted edges between numbered vertices.",
            'concept-matrices': "Distances live in an n by n table read by row i and column j, including whole rows and columns of vertex k.",
            'concept-dynamic-programming': "Round k builds on the finished table of round k-1, which is the dependency order of the recurrence.",
        },
    ),
    'lesson-segment-tree': dict(
        body="Prefix sums answer any range sum with one subtraction, but changing a single value forces every later prefix to change, so an update costs O(n). Adding up the range directly makes updates free but queries slow. A segment tree balances the two. The values sit in the leaves, padded with zeros to a power-of-two count; each internal node stores the sum of its two children, so the root holds the whole array and its children hold the left and right halves. Any range can be written as a few whole nodes, at most two per level, so a query visits O(log n) nodes. An update changes one leaf and then the sums on its path to the root, also O(log n). In the animation, watch the query split at nodes that the range cuts, take nodes that lie fully inside it, and ignore nodes that lie fully outside.",
        worked=dict(
            title="Querying positions 1 to 4",
            text="The values 5, 2, 7, 1, 3, 6 fill leaves 8 to 13, and leaves 14 and 15 hold 0. Building from node 7 down to node 1: node 7 covers the two padding leaves and holds 0, node 6 holds 3 + 6 = 9, node 5 holds 7 + 1 = 8, node 4 holds 5 + 2 = 7, node 3 holds 9 + 0 = 9, node 2 holds 7 + 8 = 15, and the root, node 1, holds 15 + 9 = 24. The query asks for positions 1 to 4. The root covers [0,7] and is cut, so both children are asked. Node 2 covers [0,3] and is cut, and so is node 4 for [0,1]: its leaf [0,0] lies outside, and node 9 for [1,1] lies inside and gives 2. Node 5 covers [2,3], fully inside, and gives its stored 8 without going deeper. On the right, node 3 for [4,7] and node 6 for [4,5] are cut, and node 12 for [4,4] gives 3. The answer is 2 + 8 + 3 = 13, from 3 stored nodes.",
        ),
        invariant=dict(
            title="Parents are the sum of children",
            text="Every internal node stores exactly the sum of its two children, and therefore the sum of the original values in its range. Build establishes this from the leaves up, and an update restores it by recomputing each node on the path from the changed leaf to the root, the only nodes whose range contains that position. A query relies on the invariant in three cases: a node outside the range contributes 0, a node inside contributes its stored sum, and a node that is cut passes the question to its children, whose ranges split it without overlap. So every position in the range is counted exactly once and no position outside it is counted. On each level at most two nodes are cut, which bounds the work by O(log n).",
        ),
        tradeoff=dict(
            title="Logarithmic everything, more memory",
            text="Building takes O(n), and each query or point update takes O(log n). Padding to a power of two needs an array of fewer than 4n slots, versus n + 1 for prefix sums or a Fenwick tree. In return, a segment tree handles any associative combination, such as minimum, maximum or greatest common divisor, not only sums that can be subtracted. With lazy propagation it also applies an update to a whole range in O(log n), by leaving a pending change on a node instead of pushing it to every leaf. If the array never changes, prefix sums are simpler and answer in O(1). If you only need prefix sums with point updates, a Fenwick tree is shorter and faster in practice.",
        ),
        pitfall="Keep one rule for range ends. This lesson's query bounds are inclusive at both ends, so outside means r < lo or hi < l. Mixing in a half-open bound turns that test into an off-by-one error that counts one extra position or misses one. Pad the leaves with the identity of the operation: 0 for sums, but a very large value for minimums, or the padding becomes the answer.",
        objectives=[
            "Answer range-sum queries and point updates in O(log n) each.",
            "Split a query range into whole tree nodes and explain why each position counts once.",
        ],
        prerequisiteNotes={
            'concept-prefix-sums': "Prefix sums are the static baseline that a segment tree improves on when values change.",
            'concept-binary-trees': "Every node has a left and right child covering the two halves of its range, visited recursively.",
        },
    ),
    'lesson-fenwick': dict(
        body="A Fenwick tree, or binary indexed tree, keeps running totals that stay correct while individual values change. It is a single array, numbered from 1. Slot i stores the sum of a block of values ending at position i, and the block's length is the lowest set bit of i, written i & -i. Slot 4, binary 100, covers 4 values; slot 6, binary 110, covers 2; slot 5 covers just itself. To add up a prefix, read a slot and jump down by its lowest bit until reaching 0. To change a value, add the difference to its slot and jump up by the lowest bit until past the end. Both walks touch at most log2 n slots. In the animation, compare the jumps with the binary form of each index: every jump clears or carries exactly one bit.",
        worked=dict(
            title="Building six slots, reading two",
            text="The values are 5, 2, 7, 1, 3, 6, placed at slots 1 to 6. Each slot covers the block ending there: slot 1 holds 5, slot 2 holds 5 + 2 = 7, slot 3 holds 7, slot 4 holds 5 + 2 + 7 + 1 = 15, slot 5 holds 3, and slot 6 holds 3 + 6 = 9. The question asks for the sum of indices 0 to 4, which are slots 1 to 5. The walk starts at slot 5 and reads 3. The lowest bit of 5, binary 101, is 1, so it jumps to slot 4 and reads 15, making 18. The lowest bit of 4 is 4, so it jumps to 0 and stops. The answer is 18 after only 2 reads, because slot 4 already summarised the first four values.",
        ),
        invariant=dict(
            title="Each slot owns one block",
            text="Slot i always equals the sum of the original values at positions i - lowbit(i) + 1 through i. A prefix query for position p reads slot p, which covers the block ending at p, then jumps to p - lowbit(p), the position just before that block, and repeats. The blocks it reads are adjacent and together cover 1 to p exactly once. An update at position p must change every slot whose block contains p. Those are exactly p, then p + lowbit(p), then that plus its own lowest bit, and so on: each jump moves to the next larger block that still includes p. Since each step clears or carries one bit, both walks take at most about log2 n steps.",
        ),
        tradeoff=dict(
            title="Smaller and simpler than a segment tree",
            text="Both prefix queries and point updates cost O(log n), and the structure needs one array of n + 1 integers, with loops short enough to write from memory. Building by repeated adds takes O(n log n); a linear-time build exists if needed. The limitation is what it can answer: prefix sums, and range sums as the difference of two prefixes. Range minimum or maximum cannot be recovered by subtraction, so they need a segment tree. A Fenwick tree over counts also answers rank questions, such as how many values seen so far are smaller than x, which is the basis of inversion counting. For static data, plain prefix sums answer in O(1) and need no tree at all.",
        ),
        pitfall="Forgetting the 1-based shift is the classic bug. Slot 0 has lowest bit 0, so an update loop that starts there adds 0 forever and never ends. Convert a public index i to slot i + 1 before walking, and remember that a range sum from l to r is prefix(r) minus prefix(l - 1), not minus prefix(l).",
        objectives=[
            "Maintain prefix sums under point updates in O(log n).",
            "Use the lowest set bit to find which slot covers which block.",
        ],
        prerequisiteNotes={
            'concept-prefix-sums': "The tree answers the same prefix question, but keeps the answer correct when a value changes.",
            'concept-bits': "Every jump is i & -i, the lowest set bit, so binary forms of the indices explain the whole structure.",
        },
    ),
    'lesson-interval-scheduling': dict(
        body="A single room, a single machine or a single channel can serve only one request at a time, and each request has a fixed start and end. Which requests should be accepted to serve as many as possible? Trying every subset is exponential, and several natural greedy rules fail: taking the shortest request first, or the one that starts first, can each block better choices. The rule that works is to sort by end time and repeatedly take the request that finishes earliest among those still compatible. Finishing early leaves the most room for everything that follows. In the animation, keep an eye on the end of the last chosen interval. Each later interval is taken if it starts at or after that point, and skipped otherwise; it is never reconsidered.",
        worked=dict(
            title="Eight requests, three accepted",
            text="The intervals are (1,4), (3,5), (0,6), (5,7), (3,9), (5,9), (6,10) and (8,11). Sorting by end time leaves them in this order, with (3,9) before (5,9) because the sort keeps input order on ties. The last end starts below every time. (1,4) is taken and the last end becomes 4. (3,5) starts at 3, before 4, so it is skipped, and so is (0,6). (5,7) starts at 5, after 4, so it is taken and the last end becomes 7. (3,9), (5,9) and (6,10) all start before 7 and are skipped. (8,11) starts at 8, after 7, and is taken. The schedule is (1,4), (5,7), (8,11): 3 requests, and no compatible set of 4 exists.",
        ),
        invariant=dict(
            title="Greedy stays ahead",
            text="Let the greedy choices be g1, g2 and so on, in order, and let any optimal schedule be o1, o2 and so on, also sorted by end time. After each step k, the end of gk is no later than the end of ok. For k = 1 this holds because g1 has the earliest end of all intervals. If it holds for k, then ok+1 starts after ok ends, which is at or after the end of gk, so ok+1 was still available when greedy made its next choice, and greedy picked something ending no later. So greedy never falls behind, and if the optimal schedule had more intervals than greedy, its next interval would also have been available to greedy, which contradicts greedy stopping. Therefore greedy picks the maximum number.",
        ),
        tradeoff=dict(
            title="One sort, one scan, one narrow problem",
            text="Sorting costs O(n log n) and the scan O(n), with O(n) space for the sorted copy. The result is optimal only for this exact goal: the largest number of compatible intervals on one resource, all counting equally. If intervals carry different values, earliest finish can be badly wrong, and weighted interval scheduling needs dynamic programming over the sorted ends with a binary search for the last compatible interval. If there are several rooms and every request must be served, the question becomes how many rooms are needed, answered by sorting starts and tracking overlaps with a min-heap of end times. Removing the fewest intervals to eliminate overlaps is the same problem in disguise: keep the greedy set and remove the rest.",
        ),
        pitfall="Decide what touching means before coding. Here an interval may start exactly when the previous one ends, so the test is start >= last end. If touching endpoints count as an overlap, as with closed intervals, the test must be strict, and the answer can change. Sorting by start time instead of end time is the other frequent slip; it fails as soon as an early, long interval covers several short ones.",
        objectives=[
            "Choose the largest set of non-overlapping intervals by earliest finish time.",
            "Prove the rule with a stays-ahead argument and know where it stops applying.",
        ],
        prerequisiteNotes={
            'concept-intervals': "You need to sort intervals and test overlap between a start and the last chosen end.",
        },
    ),
    'lesson-kmp': dict(
        body="The simplest substring search tries every starting position and compares character by character, and after a mismatch it starts again one position later. That throws away what the comparison already learned. If abcab was just matched, the text is known to end with ab, which is also how the pattern begins, so the search could continue with two characters already matched. Knuth-Morris-Pratt stores this knowledge in a failure table: for every prefix of the pattern, the length of its longest proper prefix that is also a suffix. On a mismatch, the matched length k falls back to the table value instead of 0, and the text index never moves backwards. In the animation, watch the two indices: the text position only advances, while the pattern position jumps back through the table.",
        worked=dict(
            title="One fallback saves the match",
            text="The pattern abcaby has failure table 0, 0, 0, 1, 2, 0: for example, the prefix abcab ends with ab and begins with ab, so its entry is 2. Scanning abxabcabcaby, a and b match at text positions 0 and 1, then x does not equal c. k falls back to the entry for ab, which is 0, and x does not match a either, so the scan moves on. From position 3, a, b, c, a and b match, reaching k = 5 at text position 7. At position 8 the text has c but the pattern wants y. k falls back to the entry for abcab, which is 2, meaning ab is still matched. Now c matches the third pattern character, and a, b and y follow at positions 9 to 11. k reaches 6 at position 11, so the match starts at 11 - 6 + 1 = 6.",
        ),
        invariant=dict(
            title="k is the longest live match",
            text="Before the text character at position i is read, the first k characters of the pattern equal the k text characters just before i, and no longer prefix of the pattern ends there. If the next characters match, the prefix grows by one and the statement holds at i + 1. If they differ, the longest shorter candidate that still ends at i is a prefix of the pattern that is also a suffix of the matched part, and the failure table names its length, so k = f[k - 1] keeps the statement true. Repeating the fallback tries the next shorter candidate. Because only prefixes that are known to match are kept, no occurrence of the pattern can be skipped. The failure table is built by running the same procedure on the pattern against itself.",
        ),
        tradeoff=dict(
            title="Linear guarantee, modest everyday gain",
            text="Building the table takes O(m) and the scan O(n), so KMP runs in O(n + m) time with O(m) extra space, even on inputs such as aaaa...ab that make the naive search take O(nm). Each fallback reduces k, and k grows by at most one per text character, so the total number of fallbacks is at most n. On ordinary text, mismatches tend to happen at the first character, so the naive method is often just as fast, and libraries frequently use it or Boyer-Moore variants that skip ahead. KMP matters when the worst case must be bounded, when the text is a stream that cannot be reread, or when the failure table itself is the goal, as in finding periods. Aho-Corasick extends the same idea to many patterns at once.",
        ),
        pitfall="Index errors in the failure table are the usual bug. f[i] describes the prefix ending at position i, so after a mismatch with k characters matched the fallback is f[k - 1], not f[k]. Also keep the while loop: one fallback may not be enough, and stopping after one misses matches whose prefix is shorter still.",
        objectives=[
            "Build the failure table of a pattern and explain each entry.",
            "Match the pattern without ever moving the text index backwards.",
        ],
        prerequisiteNotes={
            'concept-strings': "The algorithm compares characters by position and reasons about prefixes and suffixes of the pattern.",
        },
    ),
    'lesson-rabin-karp': dict(
        body="Comparing the pattern with every window of the text costs up to m character comparisons per window. Rabin-Karp first compares a number instead. It treats a string of length m as a number written in base B and keeps it small by taking the remainder modulo M. The pattern's hash is computed once. The first window's hash is computed directly, and each later window's hash is derived from the previous one in constant time: remove the outgoing character's contribution, multiply by B and add the incoming character. Only a window whose hash equals the pattern's needs a character comparison, because different hashes prove the strings differ while equal hashes only suggest a match. In the animation, the hash changes as the window slides, and a comparison happens only when it matches the pattern's hash.",
        worked=dict(
            title="Five windows, one comparison",
            text="Using base 31, modulus 101 and Java character codes, where a is 97, c is 99 and d is 100, the pattern cad has hash ((99 × 31 + 97) × 31 + 100) mod 101 = 74. The first window of abracadabra is abr, with hash 15. Rolling forward drops a and adds a, giving bra with hash 41, then rac with hash 45 and aca with hash 29. None of these equals 74, so not a single character is compared. The fifth window, starting at index 4, is cad, and its hash is 74. Now the window is compared with the pattern character by character, the three characters agree, and the search returns 4. Rolling uses a stored factor of 31 squared mod 101, which is 52, to remove the leading character.",
        ),
        invariant=dict(
            title="The window hash is always current",
            text="Before window i is examined, hw equals the hash of the m text characters starting at i, and hp equals the hash of the pattern. The roll keeps this true: the hash is a sum of each character times a power of B, the leading character carries B to the power m - 1, so subtracting it times that stored power, multiplying by B and adding the new character gives exactly the hash of the next window. All arithmetic is done modulo M, with M added before taking the remainder so that Java's remainder of a negative number cannot leave a negative hash. Because equal strings always have equal hashes, no occurrence is missed, and the character check stops a collision from being reported as a match.",
        ),
        tradeoff=dict(
            title="Fast on average, collisions decide the worst case",
            text="With a good modulus, collisions are rare, so the expected time is O(n + m) and the extra space O(1). The worst case is O(nm): if many windows share the pattern's hash, every one needs a full comparison. This lesson's modulus of 101 keeps the numbers readable but collides often on large inputs; real code uses a large prime, a 64-bit modulus, or two independent hashes. For a single pattern, KMP gives a guaranteed O(n + m) with no probability involved. Rabin-Karp's strength is elsewhere: hashes of all windows of one length can be put in a set and compared against many patterns or many documents at once, which is how duplicate passages and repeated substrings are found.",
        ),
        pitfall="Do not treat equal hashes as a match. Two different strings can share a hash, so always compare the characters before reporting. In Java, also watch the subtraction when rolling: the remainder operator keeps the sign of a negative number, so add M before taking the remainder, and keep every intermediate product small enough not to overflow an int.",
        objectives=[
            "Update a window hash in constant time as the window slides.",
            "Verify every hash match, because different strings can share a hash.",
        ],
        prerequisiteNotes={
            'concept-strings': "The search compares the pattern with windows of the text and reads characters by position.",
            'concept-hashing': "The method relies on hashing: equal strings give equal hashes, but equal hashes need an equality check.",
            'concept-fixed-window': "Each step drops one character and adds one, like updating a fixed-size window sum.",
        },
    ),
    'lesson-monotonic-stack': dict(
        body="For every value in a list, what is the first larger value to its right? Scanning ahead from each position can take O(n squared) when the list falls for a long time. A monotonic stack answers every position in one pass. It holds the indices that are still waiting for a larger value, and their values never increase from bottom to top. When a new value arrives, it is the answer for every smaller value on top of the stack, so those are popped and resolved; then the new index is pushed to wait for its own answer. Anything still on the stack at the end has no larger value to its right. In the animation, watch the stack shrink in bursts: one large value can resolve several waiting positions at once.",
        worked=dict(
            title="Six values, four answers found",
            text="The values are 2, 1, 5, 6, 2, 3, and every answer starts at -1. Index 0 with value 2 is pushed. Value 1 is not larger than 2, so index 1 is pushed on top. Value 5 is larger than 1, so index 1 is popped with answer 5; it is also larger than 2, so index 0 is popped with answer 5. The stack is empty and index 2 is pushed. Value 6 pops index 2 with answer 6, and index 3 is pushed. Value 2 is not larger than 6, so index 4 waits on top. Value 3 pops index 4 with answer 3, stops at 6, and index 5 is pushed. The scan ends with indices 3 and 5 still waiting, so their answers stay -1. The result is [5, 5, 6, -1, 3, -1].",
        ),
        invariant=dict(
            title="Waiting values only decrease upwards",
            text="At every moment the stack holds, from bottom to top, exactly the indices seen so far that have no larger value after them yet, and their values never increase from bottom to top. A new value pops precisely the waiting values smaller than it, and for each of them it is the first larger value to the right, since any value between them was smaller, or it would already have resolved them. The pops stop at the first value that is at least as large, so pushing the new index keeps the order. Each index is pushed once and popped at most once, which makes the total work O(n) even though one step can pop many entries.",
        ),
        tradeoff=dict(
            title="Linear time from one pass",
            text="The scan costs O(n) time and O(n) space for the stack and the answers, against O(n squared) time and O(1) extra space for scanning ahead from each position. The same skeleton adapts by changing what is stored or compared: storing indices gives distances, as in waiting days until a warmer temperature; scanning from the right or flipping the comparison gives previous or smaller values; and a popped element knows both of its limits, which is how the largest rectangle under a histogram is found. The stack only answers nearest larger or smaller questions. For the maximum over a sliding window, where old values must also leave, it needs the deque of the next lesson.",
        ),
        pitfall="Decide whether equal values pop. This lesson asks for a strictly larger value, so the loop pops while the top is less than the new value, and equal values keep waiting. With less than or equal you would answer next greater or equal instead. Push indices, not values, or you cannot write each answer to the right position.",
        objectives=[
            "Find the next greater element for every position in one pass.",
            "Explain why each index is pushed and popped at most once.",
        ],
        prerequisiteNotes={
            'concept-stacks': "The waiting indices are kept on a stack, and only the top is ever compared, popped or pushed.",
        },
    ),
    'lesson-monotonic-queue': dict(
        body="Reporting the maximum of every window of k consecutive values is easy to state and slow if done directly: scanning each window costs O(k), and a heap costs O(log k) per step. A monotonic queue does it in amortised O(1). It is a deque of indices whose values decrease from front to back, so the front is always the maximum of the current window. When a new value arrives, every value at the back that is not larger is removed, since the newcomer is both larger and will stay in the window longer, so they can never be a maximum again. Then the newcomer is added, and if the front index has fallen out of the window it is removed from the front. In the animation, watch both ends: values leave the back when beaten and the front when they expire.",
        worked=dict(
            title="Six windows of three",
            text="The values are 1, 3, -1, -3, 5, 3, 6, 7 and k is 3. 1 enters. 3 removes 1 from the back, since 1 can never be a maximum while 3 is present. -1 enters behind 3, and the first full window reports 3. -3 enters behind -1, and the window from index 1 to 3 reports 3 again. When 5 arrives at index 4, it is at least as large as -3, -1 and 3, so all three are dropped from the back; the 3 at index 1 was about to leave the window anyway. The window from index 2 to 4 reports 5. 3 enters behind 5, and the window reports 5. 6 removes 3 and then 5, reporting 6. 7 removes 6 and reports 7. The maxima are [3, 3, 5, 5, 6, 7].",
        ),
        invariant=dict(
            title="The front is the window maximum",
            text="After each step, the deque holds indices inside the current window, in increasing order, with strictly decreasing values from front to back. Every index removed from the back was followed by a value at least as large that stays in the window at least as long, so it could never again be the maximum. Every index removed from the front has left the window. So any value in the window that could still be the maximum, now or later, is in the deque, and the largest of them sits at the front. Each index enters the deque once and leaves at most once, which is why the total work is O(n) even though one new value can clear several entries.",
        ),
        tradeoff=dict(
            title="Linear time, values must arrive in order",
            text="The method takes O(n) time and O(k) extra space for the deque, against O(nk) for rescanning each window and O(n log k) for a heap or a balanced tree. It needs the window to slide forward and old values to leave in arrival order; for arbitrary range queries a segment tree or sparse table is required instead. Flipping the comparison gives sliding minima, and keeping two deques gives both, which also supports variable-size windows whose validity depends on max minus min. The same idea speeds up some dynamic programs whose transition takes the best of the last k states, cutting O(nk) to O(n).",
        ),
        pitfall="Store indices, not values. With values alone you cannot tell when the front has left the window, and duplicates make it worse. Check expiry against i - k before reading the front, after the back pops, and only report once the first full window exists, at index k - 1, or the first outputs come from partial windows.",
        objectives=[
            "Report the maximum of every window of size k in O(n) total.",
            "Maintain a deque whose front is always the current window maximum.",
        ],
        prerequisiteNotes={
            'concept-queues': "The structure is a double-ended queue, removing old entries from the front and beaten ones from the back.",
            'concept-fixed-window': "The question is about every window of k consecutive values as the window slides one step at a time.",
        },
    ),
    'lesson-knapsack': dict(
        body="A knapsack holds at most a fixed weight. Each item has a weight and a value, and can be taken once or left behind. Which items give the largest total value? Trying all subsets doubles the work with every item, and greedy rules such as best value per weight can miss the optimum. Dynamic programming builds a table instead. Row i, column c holds the best value using only the first i items with capacity c. Each cell makes one decision about item i: skip it and copy the cell above, or take it, adding its value to the best of the row above at the capacity that remains. The answer sits in the bottom-right cell. In the animation, follow the two arrows into each cell, one straight up and one up and to the left by the item's weight.",
        worked=dict(
            title="Four items, capacity 7",
            text="The items are (1,1), (3,4), (4,5) and (5,7), written as weight and value, and the capacity is 7. Row 1 uses only the first item, so every capacity from 1 to 7 holds 1. Row 2 adds the item of weight 3 and value 4: capacity 3 holds 4, and capacity 4 holds 4 + 1 = 5 by taking both. Row 3 adds weight 4 and value 5: capacity 5 reaches 6 with the items of weights 1 and 4, and capacity 7 reaches 9 by taking the items of weights 3 and 4 together, 4 + 5 = 9. Row 4 adds weight 5 and value 7: capacity 5 rises to 7, capacity 6 to 8, but at capacity 7 taking it gives 7 + 1 = 8, less than the 9 above, so 9 stays. The best value is 9.",
        ),
        invariant=dict(
            title="Each row extends the previous best",
            text="After row i is filled, every cell dp[i][c] equals the best value of any subset of the first i items with total weight at most c. Row 0 is all zeros, the value of choosing nothing. For row i, any best subset either leaves out item i, so its value is already in dp[i-1][c], or includes it once, so the rest is a subset of the first i - 1 items with weight at most c minus w, whose best value is dp[i-1][c - w]. Taking the larger of the two covers every subset. Because both cells come from the previous row, item i can never be counted twice, which is exactly the 0/1 rule.",
        ),
        tradeoff=dict(
            title="Pseudo-polynomial time",
            text="The table has (n + 1) times (W + 1) cells, each filled in O(1), so the time is O(nW) and the space O(nW). Keeping only one row cuts the space to O(W), as long as capacities are processed from high to low so each cell still reads the previous item's values. The catch is that W is a number, not a count of input items: doubling the capacity doubles the work, and for capacities in the billions the table is hopeless. The general problem is NP-hard, and the dynamic program is fast only when weights are small integers. If items can be split, the fractional knapsack is solved exactly by the value-per-weight greedy. If items can be reused, read the current row instead of the previous one.",
        ),
        pitfall="With a single row, the inner loop over capacity must run downwards. Running it upwards lets a cell read a value that already includes the current item, so the item is counted again and you have solved the unbounded knapsack by accident. With the full table, make sure the take option reads row i - 1, not row i.",
        objectives=[
            "Define the state as the best value from the first i items within capacity c.",
            "Fill the table with the take-or-skip choice and read off the answer.",
        ],
        prerequisiteNotes={
            'concept-dynamic-programming': "The lesson defines a state, its base case and its dependency order, then fills a table bottom-up.",
        },
    ),
    'lesson-lcs': dict(
        body="A subsequence keeps the order of characters but may skip some, so ace is a subsequence of abcde while aec is not. The longest common subsequence of two strings is the longest string that is a subsequence of both, and it measures how much two sequences agree once insertions and deletions are allowed. Dynamic programming over prefixes solves it. Cell (i, j) holds the answer for the first i characters of one string and the first j of the other. If the last characters match, they extend the answer from the cell diagonally above and to the left; otherwise one of them is unused, so take the larger of the cell above and the cell to the left. In the animation, a matching pair lights up the diagonal arrow, and every other cell copies its larger neighbour.",
        worked=dict(
            title="Filling a 5 by 3 table",
            text="The strings are abcde and ace, with an extra row and column of zeros for empty prefixes. Row a matches the a of ace in column 1, so that cell is 0 + 1 = 1, and the rest of the row copies 1 from the left. Row b matches nothing, so it copies 1 from above in every column. Row c matches the c in column 2: the diagonal holds 1, so the cell becomes 2, and column 3 copies 2 from the left. Row d matches nothing and copies 1, 2, 2. Row e matches the e in column 3: the diagonal holds 2, so the bottom-right cell becomes 3. Walking back from that cell along the matched diagonals picks e, then c, then a, which read forwards give the common subsequence ace of length 3.",
        ),
        invariant=dict(
            title="Every cell is a finished prefix pair",
            text="When cell (i, j) is written, it equals the LCS length of the first i characters of a and the first j characters of b. Row 0 and column 0 are 0, since an empty prefix shares nothing. If a[i-1] equals b[j-1], some longest common subsequence ends with that character, so the answer is one more than for the two shorter prefixes, the diagonal cell. If they differ, at least one of the two last characters is not used, so the answer is the larger of dropping a's last character, the cell above, or b's, the cell to the left. Filling rows left to right guarantees that those three cells are already final.",
        ),
        tradeoff=dict(
            title="Quadratic table, flexible recurrence",
            text="For lengths n and m the table has (n + 1)(m + 1) cells, so the time is O(nm) and the space O(nm). The length alone needs only two rows, O(min(n, m)) space, but rebuilding the subsequence then needs Hirschberg's divide-and-conquer method. Small changes to the recurrence give related measures: edit distance charges for insertions, deletions and replacements, and alignment scoring in bioinformatics weights matches and gaps. Practical diff tools use Myers' algorithm, which is fast when the two inputs are similar. If the common part must be contiguous, that is the longest common substring, a different recurrence that resets to 0 on a mismatch.",
        ),
        pitfall="Keep the extra row and column for empty prefixes, and remember that cell (i, j) compares a[i-1] with b[j-1]. Indexing the strings with i and j directly shifts every comparison by one. Do not confuse subsequence with substring: copying the diagonal plus one on a match is right for both, but on a mismatch a substring resets to 0.",
        objectives=[
            "Define a two-dimensional state over prefixes of both strings.",
            "Recover one common subsequence by walking the table backwards.",
        ],
        prerequisiteNotes={
            'concept-dynamic-programming': "The answer comes from a recurrence over smaller prefix pairs filled in dependency order.",
            'concept-strings': "Every cell compares one character of each string by position and reasons about prefixes.",
        },
    ),
    'lesson-interval-dp': dict(
        body="Multiplying a chain of matrices gives the same result however the products are bracketed, but the cost can differ enormously. Multiplying a p by q matrix with a q by r one costs p times q times r scalar multiplications, and the number of bracketings grows exponentially with the length of the chain. Interval dynamic programming solves every contiguous range of matrices once. The cost of a range is decided by its final multiplication, which splits it at some point k into a left range and a right range. Try every k, add the two range costs and the cost of the final product, and keep the minimum. Because every split uses shorter ranges, filling ranges in order of length makes their costs available. In the animation, the table fills diagonal by diagonal, one range length at a time.",
        worked=dict(
            title="Two bracketings, very different costs",
            text="The dimensions 10, 30, 5, 60 describe three matrices: A is 10 by 30, B is 30 by 5 and C is 5 by 60. Ranges of one matrix cost 0. For length 2, AB costs 10 × 30 × 5 = 1500, and BC costs 30 × 5 × 60 = 9000. For the whole chain there are two splits. Splitting after A means A times (BC): 0 for A, 9000 for BC, and 10 × 30 × 60 = 18000 for the final product, 27000 in total. Splitting after B means (AB) times C: 1500 for AB, 0 for C, and 10 × 5 × 60 = 3000 for the final product, 4500 in total. The table keeps the minimum, so the cheapest order costs 4500, six times less than the other bracketing.",
        ),
        invariant=dict(
            title="Shorter ranges are already final",
            text="When the range from matrix i to matrix j is filled, every shorter range inside it already holds its minimum cost. Ranges are filled in increasing length, and each split at k produces two ranges, i to k and k + 1 to j, both strictly shorter. Any bracketing of the range ends with one final multiplication, at some split k, and its cost is the cost of the two sides plus p[i] × p[k+1] × p[j+1]. The best bracketing of each side can be chosen independently, so the minimum over all k of the stored side costs plus that product is the true optimum. The same structure, last split over a contiguous range, appears in optimal binary search trees, polygon triangulation and choosing the last balloon to burst.",
        ),
        tradeoff=dict(
            title="Cubic time over all ranges",
            text="There are about n squared over 2 ranges, and each tries up to n splits, so the time is O(n cubed) and the space O(n squared). For chains of tens or hundreds of matrices that is negligible compared with the multiplications it saves; NumPy's multi_dot uses this method. Specialised algorithms solve matrix chain ordering in O(n log n), but they are rarely worth the complexity. Recording the best k for each range lets you print the bracketing. The fixed cost of interval DP is the third loop: when a problem's best split can be found without trying all k, other techniques such as Knuth's optimisation can bring the time down to O(n squared).",
        ),
        pitfall="Filling the table row by row, with i and j in plain order, reads ranges that have not been computed yet and silently uses zeros. Loop over the range length first. Also compute the product of three dimensions in a long: three values of a few thousand each already overflow an int.",
        objectives=[
            "Solve a problem over every contiguous range, from short ranges to long ones.",
            "Choose the best split point for each range and explain why both sides are already optimal.",
        ],
        prerequisiteNotes={
            'concept-dynamic-programming': "The cost of each range is a recurrence over shorter ranges, filled in an order that makes them ready first.",
        },
    ),
}

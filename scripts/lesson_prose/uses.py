"""Why each lesson matters and where its idea is used in real systems. Read by lesson_content.enrich()."""

USES = {
    'lesson-two-pointers': dict(
        why="Checking every pair of n items costs about n²/2 comparisons, which is too slow once n reaches the hundreds of thousands. On ordered data, two cursors rule out whole groups of pairs per step and finish in one pass.",
        uses=[
            dict(where="Sort-merge joins", how="A database joins two inputs sorted on the join key by advancing a cursor in each, always stepping the side with the smaller key."),
            dict(where="Unix comm", how="comm compares two sorted files line by line with one position in each file, reporting lines unique to either file or common to both."),
            dict(where="C++ std::unique and std::remove", how="Both compact a range in place with a read position and a write position, copying forward only the elements that should stay."),
        ],
    ),
    'lesson-sliding-window': dict(
        why="Recomputing the sum of every window of size k from scratch costs O(nk). Adding the value that enters and subtracting the value that leaves makes each step O(1).",
        uses=[
            dict(where="rsync rolling checksum", how="rsync slides a fixed-size block over a file and updates a weak checksum in constant time per byte to find blocks the receiver already has."),
            dict(where="pandas rolling means", how="Series.rolling(k).mean() keeps a running total, adding the newest value and removing the oldest instead of summing each window again."),
            dict(where="Box blur in image processing", how="A box blur averages a fixed-width neighbourhood, and fast implementations slide a running sum along each row and column."),
        ],
    ),
    'lesson-binary-search': dict(
        why="A linear scan of a million sorted items can take a million comparisons, while halving the range needs about twenty. The same halving works on any yes/no question that flips once, not only on arrays.",
        uses=[
            dict(where="git bisect", how="git bisect checks out a commit roughly halfway between a known good and a known bad commit, halving the suspects until the first bad commit remains."),
            dict(where="PostgreSQL B-tree indexes", how="Keys inside each B-tree page are kept sorted, and the lookup binary-searches the page to choose which child page to read next."),
            dict(where="Python bisect and Java Arrays.binarySearch", how="These library functions return a match or the insertion point in a sorted sequence, which keeps lists sorted and answers range queries."),
        ],
    ),
    'lesson-merge-sort': dict(
        why="Merge sort guarantees O(n log n) time on every input and keeps equal items in their original order. Its merge step reads data sequentially, so it also sorts data far larger than memory.",
        uses=[
            dict(where="Timsort in Python and Java", how="Python's list.sort and Java's object-array sort use Timsort, which finds already sorted runs and merges them pairwise."),
            dict(where="Database external sorts", how="When a sort does not fit in memory, PostgreSQL writes sorted runs to disk and merges them, shown as 'external merge' in EXPLAIN ANALYZE."),
            dict(where="LSM-tree compaction", how="Stores such as RocksDB merge several sorted files into one sorted file, the same merge step applied to files on disk."),
        ],
    ),
    'lesson-quick-sort': dict(
        why="Quicksort sorts in place with little extra memory and is usually fast in practice because its partition scan is cache-friendly. Knowing its O(n²) worst case explains why libraries guard against bad pivots.",
        uses=[
            dict(where="Java Arrays.sort for primitives", how="Since Java 7, sorting int, long and double arrays uses Dual-Pivot Quicksort, which partitions around two pivots instead of one."),
            dict(where="C++ std::sort", how="libstdc++ implements std::sort as introsort: quicksort that switches to heapsort when recursion gets too deep, capping the worst case at O(n log n)."),
            dict(where="Go's sort package", how="Since Go 1.19, sort.Sort uses pattern-defeating quicksort, which detects bad pivot patterns and falls back to heapsort; slices.Sort, added in Go 1.21, does too."),
        ],
    ),
    'lesson-linked-list': dict(
        why="Arrays must shift elements to insert or delete in the middle, which costs O(n). A linked list does it in O(1) once you hold the neighbouring node, at the cost of no random access.",
        uses=[
            dict(where="Java LinkedHashMap", how="LinkedHashMap threads a doubly linked list through its entries to remember insertion or access order, which makes it a simple LRU cache."),
            dict(where="Hash table chaining", how="Java's HashMap stores colliding entries in a bucket as a linked list of nodes, converting long chains to trees."),
            dict(where="Linux kernel lists", how="The kernel's list_head embeds next and prev pointers inside structures, so processes, modules and devices are linked without separate allocations."),
        ],
    ),
    'lesson-stack': dict(
        why="Many problems need to resume the most recently started task first, such as returning from nested calls or matching nested brackets. A stack gives that last-in, first-out order with O(1) push and pop.",
        uses=[
            dict(where="Program call stack", how="Each function call pushes a frame holding its locals and return address, and returning pops it, so the latest call always finishes first."),
            dict(where="JVM bytecode", how="The JVM is a stack machine: instructions such as iadd pop their operands from the operand stack and push the result back."),
            dict(where="Undo in editors", how="Each edit is pushed onto an undo stack, so undo reverses the most recent change first."),
        ],
    ),
    'lesson-queue': dict(
        why="When work must be handled in the order it arrived, a queue gives that first-in, first-out order with O(1) enqueue and dequeue. A deque adds O(1) access at both ends, which some schedulers rely on.",
        uses=[
            dict(where="Java ThreadPoolExecutor", how="Submitted tasks wait in a BlockingQueue, and worker threads take them from the front as they become free."),
            dict(where="Java ForkJoinPool", how="Each worker keeps a deque of tasks, working from one end while idle workers steal from the other end."),
            dict(where="Router packet buffers", how="Packets waiting for an outgoing link are held in a FIFO queue, and the simplest policy drops new arrivals when it is full."),
        ],
    ),
    'lesson-recursion': dict(
        why="Nested data such as folders, expressions and documents is defined in terms of smaller copies of itself, and recursion lets the code follow that shape directly. Every call uses stack space, so deep inputs can overflow the stack.",
        uses=[
            dict(where="Recursive descent parsers", how="Clang parses C and C++ with a hand-written recursive descent parser, where each grammar rule is a function that calls the functions for its parts."),
            dict(where="Python's json module", how="Encoding a nested dict or list calls the encoder again for each nested value, so very deep nesting raises RecursionError."),
            dict(where="Directory tools", how="du totals a folder as its own files plus the totals of its subfolders, applying the same rule at every level until only plain files remain."),
        ],
    ),
    'lesson-backtracking': dict(
        why="Some problems can only be solved by trying choices, but listing every complete combination grows exponentially. Backtracking abandons a partial choice as soon as it cannot work, pruning whole branches of the search.",
        uses=[
            dict(where="Backtracking regex engines", how="Engines such as java.util.regex and PCRE try one alternative, and on failure undo it and try the next, which is why some patterns backtrack catastrophically."),
            dict(where="SAT solvers", how="DPLL-style solvers assign a variable, propagate consequences, and undo assignments when a clause becomes false."),
            dict(where="Prolog", how="Prolog answers a query by trying clauses in order and backing up to the latest choice point whenever a goal fails."),
        ],
    ),
    'lesson-bst': dict(
        why="A sorted array makes inserts O(n), and a hash table loses key order. A binary search tree keeps keys ordered while supporting search, insert and nearest-key queries in time proportional to its height.",
        uses=[
            dict(where="Java TreeMap", how="TreeMap is a red-black tree, a balanced binary search tree, which gives sorted iteration and floorKey or ceilingKey lookups."),
            dict(where="C++ std::map", how="The common standard library implementations store std::map as a red-black tree, so iteration visits keys in sorted order."),
            dict(where="Linux CFS scheduler", how="Until Linux 6.6, the Completely Fair Scheduler kept runnable tasks in a red-black tree keyed by virtual runtime and ran the leftmost task next."),
        ],
    ),
    'lesson-avl': dict(
        why="Inserting sorted keys into a plain BST builds a chain, and every operation degrades to O(n). AVL rotations keep the height at O(log n), so the worst case stays logarithmic.",
        uses=[
            dict(where="OpenZFS", how="OpenZFS ships the AVL tree library inherited from Solaris and uses it for many of the file system's in-memory sorted structures."),
            dict(where="OCaml Map and Set", how="OCaml's standard Map and Set are height-balanced binary trees in the AVL style, rebalancing by rotation when child heights differ by more than two."),
            dict(where="LLVM immutable containers", how="LLVM's ImmutableMap and ImmutableSet are built on persistent AVL trees, which the Clang Static Analyzer uses to store program states cheaply."),
        ],
    ),
    'lesson-tree-traversal': dict(
        why="Most work on a tree is a visit to every node in a specific order, such as children before parent for evaluation or left-node-right for sorted output. Choosing the order is often the whole algorithm.",
        uses=[
            dict(where="Compilers", how="Code generation and constant folding walk the syntax tree in post-order, handling operands before the operator that uses them."),
            dict(where="Browser DOM", how="querySelectorAll returns matches in document order, which is a pre-order depth-first traversal of the element tree."),
            dict(where="Ordered map iteration", how="Iterating a Java TreeMap visits its search tree in-order, which is why keys come out sorted."),
        ],
    ),
    'lesson-heap': dict(
        why="Many programs repeatedly need the smallest or largest item while new items keep arriving. A heap gives the top item in O(1) and insert or remove in O(log n), without sorting everything.",
        uses=[
            dict(where="Timer queues", how="Event loops such as libevent keep pending timeouts in a min-heap, so the next timer to fire is always at the root."),
            dict(where="Top-k selection", how="Python's heapq.nlargest keeps a heap of only k items while scanning, so it handles long streams in O(n log k)."),
            dict(where="Merging sorted inputs", how="heapq.merge holds the current head of each sorted input in a heap and repeatedly emits the smallest."),
        ],
    ),
    'lesson-bfs': dict(
        why="When every edge counts as one step, BFS finds the fewest-hop path from a source to every reachable vertex in O(V + E). It explores in rings of increasing distance, so the first time it reaches a vertex is the shortest.",
        uses=[
            dict(where="Web crawlers", how="A breadth-first crawler keeps a FIFO frontier of discovered URLs, so pages one link from the seeds are fetched before pages two links away."),
            dict(where="Degrees of separation", how="Counting the fewest friendship links between two people is a shortest path in an unweighted graph, which BFS answers."),
            dict(where="Cheney's copying garbage collector", how="Cheney's algorithm copies reachable objects breadth-first, using the copied region itself as the queue."),
        ],
    ),
    'lesson-dfs': dict(
        why="DFS follows one path as far as it goes before backing up, which exposes structure such as cycles, dependency order and connected regions in O(V + E). It is the basis of topological sort and cycle detection.",
        uses=[
            dict(where="Make", how="make builds a target by first visiting each prerequisite depth-first, and reports a circular dependency when it meets a target already in progress."),
            dict(where="Mark-and-sweep garbage collection", how="The mark phase follows references from roots, often with an explicit stack, marking every reachable object before unmarked ones are freed."),
            dict(where="Flood fill", how="A paint program's bucket tool can fill a region by depth-first visiting neighbouring pixels of the same colour."),
        ],
    ),
    'lesson-dijkstra': dict(
        why="When edges have different costs, the fewest-hop path is often not the cheapest, so BFS is not enough. Dijkstra finds cheapest paths from a source when no edge cost is negative.",
        uses=[
            dict(where="OSPF and IS-IS routing", how="Each router runs Dijkstra's shortest-path-first over its link-state database to build its routing table."),
            dict(where="Road routing engines", how="Engines such as OSRM answer route queries with Dijkstra-style search, sped up by preprocessing like contraction hierarchies."),
            dict(where="A* pathfinding in games", how="A* is Dijkstra with a heuristic added to the priority, steering the search toward the goal on game maps."),
        ],
    ),
    'lesson-max-flow': dict(
        why="Many allocation problems ask how much can move from a source to a sink through limited capacities. Max flow answers them exactly, and its minimum cut shows the bottleneck that limits the total.",
        uses=[
            dict(where="Bipartite matching", how="Assigning workers to jobs they can do becomes a flow network with capacity one per edge, and the maximum flow is the largest matching."),
            dict(where="Image segmentation", how="Graph-cut segmentation splits foreground from background by computing a minimum cut between source and sink terminals."),
            dict(where="Open-pit mine planning", how="Choosing which blocks to dig for most profit, when each block needs the blocks above it removed, is project selection solved by a minimum cut."),
        ],
    ),
    'lesson-memoization': dict(
        why="Naive recursion can solve the same subproblem many times, as in Fibonacci where the work grows exponentially. Caching each result after its first computation makes the cost proportional to the number of distinct states.",
        uses=[
            dict(where="Python functools.lru_cache", how="Decorating a function with lru_cache or cache stores results keyed by arguments, so repeat calls return the stored value."),
            dict(where="Bazel build cache", how="Bazel keys each build action by a hash of its inputs and command, and reuses the stored output when that key has been seen."),
            dict(where="Packrat parsers", how="A packrat parser memoizes the result of each grammar rule at each input position, which makes PEG parsing linear time."),
        ],
    ),
    'lesson-tabulation': dict(
        why="Tabulation computes the same dynamic program bottom-up in a loop, so it avoids recursion depth limits and call overhead. Filling in dependency order also makes it easy to see when only the last row needs to be kept.",
        uses=[
            dict(where="Spelling suggestions", how="Levenshtein edit distance, used to rank spelling suggestions, fills a table where each cell depends on its left, upper and upper-left neighbours."),
            dict(where="Sequence alignment", how="Needleman-Wunsch and Smith-Waterman align DNA or protein sequences by filling a scoring table cell by cell."),
            dict(where="Viterbi decoding", how="The Viterbi algorithm fills a table of best path scores over time steps to decode hidden Markov models and convolutional codes."),
        ],
    ),
    'lesson-trie': dict(
        why="Searching a word list for every entry that starts with a prefix scans the whole list. A trie walks one node per character to the prefix and finds all matches below it.",
        uses=[
            dict(where="Autocomplete", how="Typing a prefix walks the trie to that prefix's node, and the completions are the words stored in its subtree."),
            dict(where="Linux IP routing", how="The kernel's IPv4 forwarding table is an LC-trie over address bits, so a lookup finds the longest matching prefix."),
            dict(where="Ethereum state", how="Ethereum stores account state in a Merkle Patricia trie, a compressed trie whose root hash commits to the entire state."),
        ],
    ),
    'lesson-set-cover': dict(
        why="Finding the fewest sets that cover everything is NP-hard, so exact search becomes impractical at scale. Greedy set cover is fast and provably within a logarithmic factor of the best answer.",
        uses=[
            dict(where="Test suite minimisation", how="Choosing the fewest tests that still cover every requirement or code line is set cover, and greedy selection is a standard heuristic."),
            dict(where="Facility and sensor placement", how="Picking the fewest sites, such as cell towers, whose coverage areas include every region is a set-cover problem."),
            dict(where="Airline crew scheduling", how="Selecting crew pairings so every flight is staffed is formulated as set covering and solved with integer programming."),
        ],
    ),
    'lesson-quickselect': dict(
        why="Finding the median or the k-th smallest value does not require sorting all n items. Quickselect recurses into only one side of each partition, giving O(n) expected time instead of O(n log n).",
        uses=[
            dict(where="C++ std::nth_element", how="std::nth_element places the k-th element in its sorted position with smaller elements before it, typically using introselect."),
            dict(where="NumPy partition and median", how="np.partition uses introselect by default, and np.median relies on partitioning rather than a full sort."),
            dict(where="k-d tree construction", how="Building a balanced k-d tree splits points at the median along an axis, which selection finds without sorting."),
        ],
    ),
    'lesson-bloom-filter': dict(
        why="Checking whether a key exists can mean an expensive disk or network read even when the answer is no. A Bloom filter answers 'definitely not present' from a small bit array, accepting occasional false positives.",
        uses=[
            dict(where="LSM-tree stores", how="RocksDB and Cassandra keep a Bloom filter per sorted file, skipping files that cannot contain the key before reading from disk."),
            dict(where="Cache admission", how="A cache can record keys in a Bloom filter and store an object only on its second request, so one-time requests do not evict useful entries."),
            dict(where="PostgreSQL bloom index", how="The bloom extension builds an index of per-row signatures that can filter rows on equality tests over many columns at once."),
        ],
    ),
    'lesson-complexity': dict(
        why="Code that runs instantly on test data can become unusable when the input grows, and growth rates predict that before it happens. Comparing O(n) with O(n²) tells you which design will still work at a million items.",
        uses=[
            dict(where="Query planners", how="PostgreSQL's planner estimates the cost of sequential scans, index scans and join methods from row counts and picks the cheapest plan."),
            dict(where="Library documentation", how="Java's collections docs and the C++ standard state operation costs, such as O(log n) for TreeMap get, so users can choose structures."),
            dict(where="Hash-flooding defences", how="Attackers sent keys that collide to turn O(1) lookups into O(n), so Python and others adopted randomised string hashing."),
        ],
    ),
    'lesson-arrays': dict(
        why="An array stores items contiguously, so any index is reached in O(1) and scans run at memory speed. Most other structures, including heaps, hash tables and matrices, are built on top of arrays.",
        uses=[
            dict(where="Dynamic arrays", how="Java's ArrayList and Python's list are arrays that grow by reallocating to a larger capacity, giving amortised O(1) appends."),
            dict(where="NumPy", how="An ndarray stores values of one fixed type in a single memory buffer, so vectorised operations run as C loops without per-element Python objects."),
            dict(where="Linux io_uring", how="io_uring passes requests and completions through ring buffers, arrays whose head and tail indexes wrap around modulo the size."),
        ],
    ),
    'lesson-strings': dict(
        why="Strings look simple, but repeated concatenation can copy the whole text each time and turn a loop into O(n²). Knowing how characters are stored also avoids bugs with text outside basic ASCII.",
        uses=[
            dict(where="Java StringBuilder", how="StringBuilder appends into a growable character buffer, avoiding the new string each += creates on an immutable String."),
            dict(where="Java StringBuilder.reverse", how="Java strings are UTF-16, and reverse keeps each surrogate pair together so emoji survive, though combining accents can still detach from their letters."),
            dict(where="GNU grep", how="For a fixed search string, GNU grep uses Boyer-Moore, which checks the pattern's last character first and skips ahead on a mismatch instead of reading every byte."),
        ],
    ),
    'lesson-hashing': dict(
        why="Finding whether a value was seen before by scanning a list costs O(n) per lookup. A hash table answers in expected O(1) time, which turns many O(n²) algorithms into O(n).",
        uses=[
            dict(where="Hash joins", how="A database builds a hash table on the join key of the smaller input, then probes it once for each row of the larger input."),
            dict(where="Key-value caches", how="Redis and memcached look up keys in in-memory hash tables, so a get takes about the same time however many keys are stored."),
            dict(where="Deduplicating backups", how="Tools such as restic and Borg split files into chunks and store each chunk once, finding duplicates by looking up its hash."),
        ],
    ),
    'lesson-prefix-sums': dict(
        why="Summing a range from scratch costs O(n) per query, which adds up when there are many queries. After one O(n) pass, any range sum is the difference of two prefix values in O(1).",
        uses=[
            dict(where="Integral images", how="Viola-Jones face detection uses a 2-D prefix sum, the integral image, so the sum of any rectangle of pixels takes four lookups."),
            dict(where="Weighted random choice", how="Python's random.choices with weights builds cumulative weights and binary-searches a random number into them."),
            dict(where="GPU parallel scan", how="Parallel prefix sum is a basic GPU primitive used for stream compaction and radix sort, computing all prefix values in parallel."),
        ],
    ),
    'lesson-variable-window': dict(
        why="Many questions ask for the longest or shortest run that satisfies a condition, and checking every start and end pair is O(n²). Growing the right edge and shrinking the left only when needed visits each item at most twice.",
        uses=[
            dict(where="TCP sliding window", how="The sender may have bytes in flight up to the window, whose left edge advances on acknowledgements and whose size is capped by the receiver's window and the congestion window."),
            dict(where="Sliding-log rate limiting", how="A limiter stores timestamps of recent requests, dropping those older than the time limit from the front before counting."),
            dict(where="Prometheus range queries", how="rate(metric[5m]) uses the samples inside a trailing five-minute range, so how many samples the window holds varies."),
        ],
    ),
    'lesson-intervals': dict(
        why="Ranges of time, memory or positions often overlap, and comparing every pair is O(n²). Sorting by start lets one pass merge overlaps or find gaps in O(n log n).",
        uses=[
            dict(where="Calendar free/busy", how="Finding a meeting time merges each person's busy intervals and reports the gaps between merged intervals as free slots."),
            dict(where="Memory allocators", how="Allocators such as dlmalloc coalesce a freed block with adjacent free blocks, merging touching address ranges into one."),
            dict(where="bedtools merge", how="bedtools merge combines overlapping or adjacent genomic intervals from a sorted file into single intervals."),
        ],
    ),
    'lesson-matrices': dict(
        why="Grids appear in images, maps, games and spreadsheets, and most bugs come from swapping row and column or stepping outside the bounds. Knowing how (row, col) maps to memory also explains why scan order affects speed.",
        uses=[
            dict(where="Image rotation", how="Rotating an image 90 degrees clockwise is a transpose of its pixel grid followed by reversing each row."),
            dict(where="NumPy transpose", how="Calling .T on a NumPy array returns a view with its strides swapped, so element [r][c] appears at [c][r] without copying."),
            dict(where="Grid pathfinding", how="Tile-based game maps treat each cell as (row, col) with up to four or eight neighbours and run BFS or A* over them."),
        ],
    ),
    'lesson-graphs': dict(
        why="Networks of roads, dependencies or friendships are graphs, and the representation decides how fast you can list a vertex's neighbours. Adjacency lists suit sparse graphs, while matrices suit dense ones and O(1) edge checks.",
        uses=[
            dict(where="NetworkX", how="NetworkX stores a graph as a dict of dicts, an adjacency list where each vertex maps to its neighbours and their edge data."),
            dict(where="Package managers", how="pip and npm treat packages as vertices and dependencies as directed edges, then traverse that graph to resolve versions and install order."),
            dict(where="OpenStreetMap routing", how="Routing engines convert OpenStreetMap ways into a sparse graph of intersections and road segments before running shortest-path search."),
        ],
    ),
}

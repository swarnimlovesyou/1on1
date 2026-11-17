PROSE = {
    'lesson-avl': dict(
        body="A plain binary search tree is only as good as its shape. Feed it keys in sorted or nearly sorted order and it turns into a long chain, so a search walks past almost every key. An AVL tree keeps the ordering rule of a search tree and adds one duty: every node remembers its height, and after each insertion the nodes on the way back to the root check whether their two subtrees differ in height by more than one. When one does, a rotation, a small relinking of two or three nodes, lowers the taller side without disturbing the sorted order. In the animation, watch where each repair happens: it is anchored at the lowest node on the insertion path that went out of balance, and a double rotation first turns that node's child.",
        worked=dict(
            title="One single rotation, two double ones",
            text="The keys arrive as 30, 20, 10, 25, 28, 27. After 30 and 20 the tree is a two-node chain of height 2. Inserting 10 makes the chain three long, and 30 sees a balance of 2: its left side is two levels taller. One right rotation at 30 lifts 20 to the root with 10 and 30 as children. 25 then settles as the left child of 30, and the height becomes 3. Inserting 28 as the right child of 25 unbalances 30 again, but now the extra height sits in the inner grandchild, so two rotations are needed: left at 25, then right at 30, leaving 28 above 25 and 30. Last, 27 goes under 25 and the root 20 is too heavy on the right. A right rotation at 28 and a left rotation at 20 make 25 the new root. The final tree has 25 on top, 20 with 10 on the left, 28 with 27 and 30 on the right, and height 3.",
        ),
        invariant=dict(
            title="Balanced heights, unchanged order",
            text="Two facts hold after every insertion. First, the search-tree order: every key in a left subtree is smaller than its ancestor and every key in a right subtree is larger, so an in-order walk lists the keys sorted. A rotation only changes which of the nodes involved is the parent, and the middle subtree is reattached on the other side, so the in-order sequence is the same before and after. Second, the balance rule: at every node the two subtree heights differ by at most one. An insertion changes heights only along its own path, by at most one each, so the lowest node that reaches a difference of two is the only place that needs repair. After the rotation that subtree is back to its height before the insertion, so nothing above it needs work.",
        ),
        tradeoff=dict(
            title="Logarithmic height for a little bookkeeping",
            text="Because subtree heights differ by at most one everywhere, the sparsest AVL tree of a given height grows like the Fibonacci numbers, which keeps the height below about 1.44 log2 n. Search, insert and delete therefore cost O(log n) in the worst case, not only on friendly inputs. Each node stores one extra integer, and an insertion needs at most one single or double rotation plus height updates along its path. The cost is code: four rotation cases, careful height updates, and deletions that may rotate at several levels. Red-black trees accept looser balance, up to about 2 log2 n, and need only a constant number of rotations even on deletion; Java's TreeMap is one. If the data never changes after loading, a sorted array with binary search is simpler still.",
        ),
        pitfall="A single rotation does not fix a zig-zag. When the new key went left and then right (or right and then left) below the unbalanced node, rotating only at that node moves the imbalance to the other side. Check which way the child leans first and rotate the child before the node. After any rotation, recompute the lower node's height before the upper one, because the upper height is built from it.",
        objectives=[
            "Find the lowest node whose subtree heights differ by two after an insertion.",
            "Choose a single or double rotation and explain why key order survives it.",
        ],
        prerequisiteNotes={},
    ),
    'lesson-trie': dict(
        body="Autocomplete keeps asking one question: which stored words begin with what has been typed so far? Keeping the words in a list means comparing the prefix with every one of them. A trie spreads the words over a tree instead, one character per edge, so all words that start the same way share the same opening path. Looking up a prefix of length L follows at most L edges, however many words are stored, and every word below the node you reach is a completion. A flag on each node records whether a word actually ends there, because a path can be a stored word, a prefix of longer words, or both. In the animation, notice how later words reuse the edges earlier words created and only branch off where they first differ.",
        worked=dict(
            title="Four words, one shared stem",
            text="The words are tree, trie, try and track. Inserting tree starts at the empty root, creates one node each for t, r, e and e, and marks the last one as a word end: 1 word stored. Inserting trie follows the existing t and r edges, so the only new nodes are i and e, and the count becomes 2. try follows t and r again and creates just y, giving 3 words. track follows t and r, branches at a, and creates a, c and k, so the count reaches 4. The trie holds only 10 nodes below the root, fewer than the letters in the four words, because the stem tr is stored once and shared by every word. A query for the prefix tr would stop at that shared node and find all four words beneath it.",
        ),
        invariant=dict(
            title="Every path spells one prefix",
            text="Each node stands for exactly one string: the characters on the edges from the root down to it. No two nodes stand for the same string, because insertion follows an existing edge whenever one matches and creates a new edge only where the stored paths stop. That is why a lookup can be a plain walk. If the walk for a prefix falls off the tree, no stored word starts with that prefix; if it reaches a node, every stored word with that prefix lies in the subtree below. The word-end flag records what the shape cannot: here a node for tr exists, yet tr was never inserted, so its flag stays off and an exact lookup for tr answers false.",
        ),
        tradeoff=dict(
            title="Fast prefixes, many small nodes",
            text="With constant-time child lookup, insert and lookup cost O(L) for a word or prefix of length L, independent of how many words are stored. Listing completions costs extra, in proportion to the subtree you walk, so a short prefix over a large dictionary can still produce a lot of output. Space is the weak point: every node carries a map or array of children, which is heavy next to the characters themselves. A sorted list with binary search answers the same prefix questions in O(L log n) time with far less memory, and a hash set answers exact membership with less memory. A trie earns its memory when prefix queries are frequent and the stored words share long stems.",
        ),
        pitfall="Reaching a node is not the same as finding a word. Walking t, r, y proves that some stored word starts with try, not that try itself was inserted; only the word-end flag says that. The opposite slip also happens: forgetting to set the flag on a word that is a prefix of a longer one, such as adding car after cart, makes car invisible to exact lookups.",
        objectives=[
            "Insert words so that shared prefixes reuse existing edges.",
            "Separate prefix lookup from exact-word lookup with the word-end flag.",
        ],
        prerequisiteNotes={},
    ),
    'lesson-dijkstra': dict(
        body="Breadth-first search finds the fewest edges, but road maps, networks and schedules put a cost on each edge, and the cheapest route can use more edges than the shortest one. Dijkstra's algorithm handles nonnegative costs. It keeps a tentative distance for every vertex, 0 at the source and infinity elsewhere, and grows a set of settled vertices whose distances are final. Each round it settles the unsettled vertex with the smallest tentative distance, then relaxes that vertex's outgoing edges: if going through it gives a neighbour a cheaper route, the neighbour's estimate drops and its parent changes. In the animation, watch the distance row. A number can shrink while its vertex is unsettled, but once the vertex is settled the number never changes again.",
        worked=dict(
            title="Settling six vertices in order",
            text="The source is vertex 0 at distance 0. Its edges reach 1 with weight 5 and 2 with weight 6, so those estimates become 5 and 6, and 0 is settled. The smallest unsettled estimate is 5, so 1 is settled next. Its edge to 3 gives 5 + 4 = 9, while its edge to 2 would give 5 + 3 = 8, which does not beat 6. Vertex 2 is settled at 6, and its edge to 4 gives 6 + 4 = 10; reaching 3 through 2 would cost 6 + 8, worse than 9. Vertex 3 is settled at 9 and offers 5 a route of 9 + 3 = 12, while 9 + 2 does not beat the 10 already held by 4. Then 4 is settled at 10 and 5 at 12. The final distances are [0, 5, 6, 9, 10, 12], and following parents back from 5 gives the route 0, 1, 3, 5.",
        ),
        invariant=dict(
            title="Settled means final",
            text="When a vertex is settled, its tentative distance is its true shortest distance from the source. Suppose a cheaper route to it existed. That route starts in the settled set, so let u be its first unsettled vertex, reached by an edge from a settled one. Relaxing that edge already gave u an estimate no larger than the route's cost up to u, and with nonnegative weights the rest of the route can only add cost. So u's estimate would be smaller than the picked vertex's, contradicting the choice of the minimum. That argument is why the greedy choice is safe, and it is exactly where a negative edge breaks things: a later edge could subtract cost and make a settled distance wrong.",
        ),
        tradeoff=dict(
            title="Scanning versus a heap",
            text="This version finds the next vertex by scanning every unsettled estimate, which costs O(V) per round and O(V²) overall, plus O(E) relaxations. On a dense graph, where E is close to V², that is as good as it gets and the code stays short. On a sparse graph, a binary heap keyed by tentative distance finds the minimum in O(log V) and brings the total to O((V + E) log V); stale heap entries are simply skipped when popped. Space is O(V) for distances and parents, plus the graph itself. If every edge has the same weight, plain BFS gives the same answer more cheaply. If weights can be negative, use Bellman-Ford, which is slower but also detects negative cycles.",
        ),
        pitfall="Do not finalise a vertex the moment it is first reached. A first estimate is only an upper bound: a route with more edges but lighter weights can still beat it, and only the smallest-estimate rule guarantees nothing cheaper is on the way. Keep weights nonnegative too; a single negative edge can leave a settled distance wrong without any error being raised.",
        objectives=[
            "Settle vertices in order of smallest tentative distance and relax their edges.",
            "Explain why nonnegative weights make a settled distance final.",
        ],
        prerequisiteNotes={},
    ),
    'lesson-max-flow': dict(
        body="Picture pipes from a reservoir to a city, each with a limit on how much water it can carry per second. How much can arrive in total? A flow network models this with directed edges that have capacities, a source, a sink, and the rule that every inner vertex passes on exactly what it receives. Edmonds-Karp builds the answer in rounds. Each round runs a breadth-first search in the residual network, the edges that still have spare capacity plus reverse edges that allow earlier flow to be cancelled, and pushes as much as the narrowest edge on the found path allows. When no path from source to sink remains, the flow is maximum. In the animation, watch reverse edges appear after each augmentation, and the reachable set at the end, which marks a minimum cut.",
        worked=dict(
            title="Two paths, then a cut",
            text="The source is vertex 0 and the sink is vertex 5. The first search finds the path 0, 1, 3, 5 with capacities 5, 4 and 3. The narrowest is 3, so 3 units flow and the total is 3, and each of those edges gains a reverse residual edge of 3. The second search finds 0, 2, 4, 5 with capacities 6, 4 and 4, which carries 4 more units, so the total becomes 7. Now the edges from 3 to 5 and from 4 to 5 are both full. From the source the residual network still reaches 1, 2, 3 and 4, but not 5, so the search fails and the algorithm stops at 7. The edges leaving that reachable set are exactly those two full edges into the sink, with capacities 3 + 4 = 7, matching the flow: a minimum cut. This run never needed a reverse edge, but they are what lets other inputs reroute earlier choices.",
        ),
        invariant=dict(
            title="Capacity, conservation, residuals",
            text="Throughout the run, the flow on each edge stays between zero and its capacity, and every vertex other than the source and sink sends out exactly what comes in. An augmentation keeps both facts. It adds the same amount along one path, so every inner vertex on it gains equal inflow and outflow, and that amount is the smallest residual capacity on the path, so no edge overflows. The residual network records for each edge how much more can be pushed forward and how much already sent could be pushed back. When the sink is unreachable, the vertices the source can still reach form a cut whose outgoing edges are full and whose incoming edges carry nothing, so the flow equals the cut's capacity and no flow can be larger.",
        ),
        tradeoff=dict(
            title="Shortest paths bound the rounds",
            text="Any augmenting path keeps the answer correct, but careless choices can need a huge number of tiny augmentations. Choosing the path with the fewest edges, via BFS, guarantees at most O(VE) rounds, each costing O(E) for the search, so Edmonds-Karp runs in O(VE²) time. This lesson keeps capacities in a V by V matrix, which costs O(V²) space and suits small dense graphs; adjacency lists with paired reverse edges suit large sparse ones. Dinic's algorithm pushes many shortest paths per phase and is often much faster in practice. Whichever you use, the final failed search also hands you a minimum cut, which answers bottleneck questions directly.",
        ),
        pitfall="Do not leave out the reverse edges. Without them, a path chosen early can block a better arrangement, and the search stops while more flow is still possible. Also take the bottleneck over residual capacities, not the original ones: an edge that already carries flow has less room left than its label says.",
        objectives=[
            "Augment flow along a shortest residual path by its bottleneck capacity.",
            "Read a minimum cut from the vertices still reachable when the search fails.",
        ],
        prerequisiteNotes={},
    ),
    'lesson-set-cover': dict(
        body="Suppose you want a short study plan that touches every topic on your list, and each practice question covers a few topics. Finding the smallest set of questions that covers everything is hard in general: no known method solves large cases exactly in reasonable time. The greedy rule is a practical compromise. In each round, score every candidate by how many still-uncovered topics it would add, take the best one, and repeat until everything is covered or no candidate adds anything. It never revisits a choice. In the animation, watch the scores change from round to round: a candidate's value depends on what is already covered, not on how many topics it lists.",
        worked=dict(
            title="Three rounds to cover five topics",
            text="The goals are Arrays, Hashing, Trees, Graphs and DP, so 5 topics start uncovered. Candidate 1 covers Arrays and Hashing, candidate 2 covers Graphs and Trees, candidate 3 covers Arrays and DP, and candidate 4 covers only Trees. In the first round candidates 1, 2 and 3 each add 2 topics and candidate 4 adds 1; the tie goes to the first, so candidate 1 is chosen and Trees, Graphs and DP remain. In the second round candidate 1 adds nothing, candidate 2 still adds 2, and candidates 3 and 4 add 1 each, so candidate 2 is chosen and only DP remains. In the third round only candidate 3 adds anything, and it covers DP. Three candidates were chosen and nothing is left uncovered. Here three is also the true minimum, since no two candidates together cover all five topics.",
        ),
        invariant=dict(
            title="Coverage only grows",
            text="After each round, the covered set is exactly the union of the chosen candidates, and the remaining set is the goals minus that union. A candidate is chosen only when its gain is positive, so every round strictly shrinks what remains, and the loop runs at most once per goal. When it stops there are two honest outcomes: everything is covered, or the leftover goals appear in no candidate at all, and the algorithm reports them instead of hiding them. What this invariant does not promise is minimality. Gains are measured against the current remaining set only, so a choice that looked best early can force extra picks later.",
        ),
        tradeoff=dict(
            title="A guarantee, not an optimum",
            text="Each round scores every candidate against the remaining goals. With P candidates and T goals, a straightforward version spends up to O(P·T) per round over at most min(P, T) rounds. Finding the exact minimum cover is NP-hard, so for large inputs a fast heuristic is the realistic option. Greedy comes with a proven bound: with equal costs it uses at most H(T) times as many sets as the optimum, where the harmonic number H(T) is below ln T + 1. On small inputs like this one, trying every subset of candidates is affordable and gives the true minimum. When candidates have different costs, score by uncovered topics per unit of cost instead.",
        ),
        pitfall="Do not score a candidate by how many topics it lists. Its value is only what it adds now: in the second round, candidate 3 still lists two topics but adds one, because Arrays is already covered. And do not read the greedy result as proof that no smaller plan exists.",
        objectives=[
            "Score each candidate by the uncovered goals it adds and pick the largest gain.",
            "Explain why a greedy cover can be larger than the optimum.",
        ],
        prerequisiteNotes={},
    ),
    'lesson-quickselect': dict(
        body="Sometimes you need one value by rank, such as the median or the third smallest, not a fully sorted list, and sorting does more work than the question asks for. Quickselect borrows the partition step from quicksort: choose a pivot, move the values not larger than it to its left and the larger ones to its right, and the pivot lands exactly where it would sit after sorting. If that position is the requested rank, you are done. Otherwise only one side can contain the answer, and the other side is dropped for good. Choosing the pivot at random makes it unlikely that the split is lopsided round after round. In the animation, watch the range of interest shrink, and notice the values outside it that are never put in order.",
        worked=dict(
            title="Finding the third smallest",
            text="The input is 4, 2, 7, 1, 3, 6 and the requested rank is 3, which is index 2 once sorted. The first random pivot is 7. It is moved to the end, every other value is at most 7, so the boundary advances past all of them and 7 is placed at index 5. Index 2 lies to its left, so the search continues on indices 0 to 4. The second pivot is 1, the smallest value: no scanned value is at most 1, so the pivot lands at index 0, giving 1, 2, 6, 3, 4, 7. The range is now indices 1 to 4. The third pivot is 3. Only 2 is at most 3, so the boundary moves once and 3 is placed at index 2. That is the requested position, and the answer is 3. The values 4 and 6 were never compared with each other; that they end up in order is luck.",
        ),
        invariant=dict(
            title="The pivot's index is its rank",
            text="After a partition of the range from low to high, the pivot sits at some index p, every value from low up to p minus one is at most the pivot, and every value after p up to high is larger. So the pivot is exactly the value that would sit at index p in sorted order. The requested index always stays inside the current range: if it equals p the search stops, if it is smaller only the left part can hold the answer, and if it is larger only the right part can. Each round removes at least the pivot from the range, so the loop must end. Values outside the range are already on the correct side of the answer, which is why they never need sorting.",
        ),
        tradeoff=dict(
            title="Expected linear, worst quadratic",
            text="Each partition is one pass over the current range. With random pivots the range shrinks by a constant fraction on average, so the passes add up like n + n/2 + n/4 and the expected time is O(n). A run that keeps drawing the largest or smallest value, as the first two pivots here did, costs O(n²), but over many runs that is very unlikely. If a worst-case bound is required, the median-of-medians pivot rule guarantees O(n) at the price of a much larger constant. Sorting first costs O(n log n) and pays off only when you need many ranks from the same data. This version works on a copy of the input, using O(n) space, so the caller's array is left untouched.",
        ),
        pitfall="Mixing up ranks and indexes is the classic bug: rank 3 means index 2. The expected bound also depends on the pivots being random; a fixed first or last pivot on sorted input discards only one value per round. With many repeated values a two-way partition can degrade as well, which is why many implementations, including this app's own Quickselect class, split into less, equal and greater.",
        objectives=[
            "Partition around a random pivot and continue only into the side that holds the rank.",
            "Distinguish quickselect's expected O(n) time from its O(n²) worst case.",
        ],
        prerequisiteNotes={},
    ),
    'lesson-bloom-filter': dict(
        body="Before an expensive lookup on disk or across a network, it helps to learn cheaply that an item is definitely not there. A Bloom filter does this with a fixed array of bits and a few hash functions. Inserting an item sets the bits its hashes point to. A query checks those same bits: if any is zero, the item was never inserted; if all are one, it might have been, because other items may have set the same bits. The filter never stores the items, so it is far smaller than a set, but it cannot list its contents or delete safely. In the animation, watch bits turn on as words arrive, and notice that a later word can land entirely on bits that are already set.",
        worked=dict(
            title="A false positive for sheep",
            text="The filter starts with every bit at zero, and each word sets two positions. tree hashes to bits 14 and 9, so those turn on. graph happens to hash to the same two bits, 14 and 9, so the bit array does not change at all, even though the exact set now holds 2 words. heap hashes to 12 and 11, which turns those bits on; 4 bits are now set and the exact count is 3. The query sheep hashes to 11 and 12. Both are already one, set by heap, so the filter answers possibly present. The exact set shows that sheep was never inserted: this is a false positive. A query whose bits had included any position that is still zero would have been rejected at once, with certainty.",
        ),
        invariant=dict(
            title="No false negatives",
            text="Bits are only ever switched on, never off. So once an item has been inserted, every bit its hashes name stays one for the rest of the filter's life, and a query for it always answers possibly present. That is the guarantee a Bloom filter sells: a no is always right. A yes is weaker; it only says that each of the item's bits was set by some insertion, not necessarily by this item. The exact set kept beside the filter in this lesson exists to show that difference. In real use the confirmation comes from the authoritative store the filter protects. Clearing a bit to delete an item would break the guarantee, because the same bit may belong to other items.",
        ),
        tradeoff=dict(
            title="Tiny, fast and approximate",
            text="Insert and query each compute k hashes and touch k bits, so both cost O(k), however many items are stored. Space is m bits, about 9.6 bits per item for a one percent false-positive rate with the best k, far less than storing the items. The price is that rate, which rises as bits fill: with n items and well-mixed hashes a bit is still zero with probability about e^(-kn/m), so an absent item passes all k checks with probability about (1 - e^(-kn/m))^k, which is lowest near k = (m/n) ln 2. A filter cannot shrink, list its items or delete; a counting Bloom filter swaps bits for small counters to allow deletion, at several times the space. Put one in front of a slow lookup, never in place of exact membership.",
        ),
        pitfall="Do not act on a positive answer as if it were exact: in this trace sheep was never inserted, yet both of its bits are set. Do not size the filter for today's data only, either. As more items arrive, more bits turn on and the false-positive rate climbs until almost every query says possibly present.",
        objectives=[
            "Explain why a zero bit proves absence while all-ones only suggests presence.",
            "Relate filter size, hash count and item count to the false-positive rate.",
        ],
        prerequisiteNotes={},
    ),
}

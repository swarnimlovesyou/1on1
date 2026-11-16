"""Phase 1 teaching source. Imported by generate_content.py; no database edits here."""
import textwrap


def block(name, title, text):
    return dict(id=name, kind='explanation', title=title, text=text, lines=[])


def enrich(lessons, problems):
    settings = {
        'sliding-window': dict(
            input='2,1,5,1,3,2', target=3, topics=['Arrays', 'Sliding window'],
            body='Imagine a frame that holds exactly three readings. Slide it one place to the right: two readings stay inside, one leaves, and one enters. The previous sum already contains almost everything you need. Remove the outgoing reading and add the incoming one. The frame represents a contiguous interval; it cannot skip an inconvenient reading. Try changing one value before looking at the code, then predict which windows it will affect.',
            sections=[
                block('worked', 'Reuse the work you already did', 'For 2, 1, 5, 1, 3, 2 with k = 3, the first full window sums to 8. Moving right removes 2 and adds 1, so the next sum is 7. The following windows sum to 9 and 6. The answer is 9. The largest element alone is not the answer: the problem asks for three consecutive readings.'),
                block('invariant', 'The frame and the sum agree', 'After processing index right, the running sum contains exactly the readings from max(0, right-k+1) through right. Only compare with best once the frame contains k readings. Initializing best to zero breaks all-negative inputs. Keep best unset, or at the smallest representable value, until the first full window exists.'),
                block('tradeoff', 'What the constraint tells you', 'Recomputing each of n-k+1 sums takes O(nk). Reusing the sum takes O(n) time and O(1) extra space. This fixed-size technique works with negative readings. A variable-size window that shrinks whenever a sum is too large needs additional assumptions; negative values can break that shrinking rule.'),
            ],
            code=['int sum = 0, best = Integer.MIN_VALUE;', 'for (int right = 0; right < a.length; right++) { sum += a[right];', '  if (right >= k) sum -= a[right - k];', '  if (right >= k - 1) best = Math.max(best, sum); }', 'return best;'],
            predict=('Slide the first full window one place right. What is the new sum?', ['8: keep the previous sum', '7: subtract 2 and add 1', '9: take the largest window immediately'], 1, 'The retained 1 and 5 already belong to the sum. Only the outgoing and incoming readings change it.'),
            pattern=('You have up to 100000 signed readings and need the largest sum of exactly k consecutive values. Which approach fits?', ['Sort, then take the k largest: O(n log n)', 'Try every subset: O(2^n)', 'Maintain a fixed window sum: O(n)'], 2, 'Contiguity and a fixed k let us reuse work. Sorting destroys the required order.'),
            dry_step=4, fields=[('left', 'Left index'), ('right', 'Right index'), ('sum', 'Current sum'), ('best', 'Best full-window sum')],
            dry_prompt='Fill the state table after processing right = 3, using the original input and k = 3.',
            dry_hint='Start from the first full sum, 8. The next operation removes index 0 and adds index 3.',
            goal='Change the readings so the largest sum of exactly three consecutive values is 12. Keep k = 3.', rule=dict(path='variables.best', equals=12), requiredTarget=3,
            linked=['three-window', 'distinct-windows'], prerequisites=['lesson-two-pointers'],
        ),
        'bst': dict(
            input='8,3,10,1,6,14,4,7,13', target=3, topics=['Trees'],
            body='Imagine a branching set of signposts. At each node, smaller keys go left and larger keys go right. A search never needs to inspect both branches. Build a tree by inserting the values one at a time, and notice that insertion order determines the shape. A binary search tree describes an ordering rule; it does not promise that the two sides have similar heights.',
            sections=[
                block('worked', 'A decision at each branch', 'Insert 8, then 3, then 10. The first value becomes the root; 3 goes left and 10 goes right. To insert 6, compare with 8 and move left, then compare with 3 and move right. The new node is the right child of 3. An in-order traversal visits 1, 3, 4, 6, 7, 8, 10, 13, 14 for this lesson\'s complete input.'),
                block('invariant', 'The rule covers whole subtrees', 'Every key in the left subtree is smaller than its ancestor, not merely smaller than its immediate parent. The corresponding right subtree contains larger keys. Our implementation ignores duplicate keys. Watch whether a repeated insertion changes the node count or shape; it should do neither.'),
                block('tradeoff', 'Shape determines the cost', 'Searching and inserting cost O(h), where h is the height. A balanced tree has logarithmic height; inserting an increasing sequence into an ordinary BST makes a chain with linear height. An AVL tree adds rotations to maintain balance. Do not silently claim O(log n) for every unbalanced BST operation.'),
            ],
            code=['if (node == null) return new Node(value);', 'if (value < node.value) node.left = insert(node.left, value);', 'else if (value > node.value) node.right = insert(node.right, value);', 'return node; // an equal key leaves the tree unchanged'],
            predict=('After inserting 8, 3, 10, and 1, where will 6 be inserted?', ['Left child of 8', 'Right child of 10', 'Right child of 3'], 2, '6 is smaller than 8, then larger than 3. Follow those two comparisons.'),
            pattern=('You need ordered traversal as well as repeated insertions and searches. Which structure fits, and what controls its operation cost?', ['A queue; every operation is O(log n)', 'A BST; search and insertion cost O(height)', 'A hash table; its iteration is always sorted'], 1, 'A BST preserves ordered relationships. Its height determines how many comparisons a path needs.'),
            dry_step=11, fields=[('inserted', 'Just-inserted key'), ('root', 'Root key'), ('height', 'Height in nodes')],
            dry_prompt='Fill the table after inserting the first five values: 8, 3, 10, 1, 6.', dry_hint='Height counts nodes on the longest root-to-leaf path. Insertion into an ordinary BST does not move the root.',
            goal='Create an insertion order whose unbalanced BST has height 4. Duplicate keys are ignored.', rule=dict(path='variables.height', equals=4),
            linked=['bst-inorder', 'tree-height'], prerequisites=['lesson-binary-search'],
        ),
        'bfs': dict(
            input='4,2,7,1,3,6', target=3, topics=['Graphs'],
            body='Imagine ripples moving out from a starting room. Breadth-first search explores the nearest discovered rooms before moving farther away. Its queue is the boundary between what has been discovered and what still needs processing. In this small directed network we start at vertex 0; each input value helps derive an edge weight, but BFS ignores weights and follows discovery order.',
            sections=[
                block('worked', 'The queue makes the layers', 'Start with queue [0] and mark 0 discovered. Remove 0, discover neighbours 1 and 2, and enqueue them in that order. Processing 1 next can discover 3. Processing 2 must not enqueue 3 again if 1 already discovered it. The graph drawing shows the exact edges used by the Java execution; vertex labels are the same numeric IDs used in code.'),
                block('invariant', 'Discover once, process once', 'Mark a vertex when it enters the queue, rather than when it leaves. Otherwise two parents can enqueue the same vertex. A vertex can be discovered without having been processed yet; those are different states. Maintain a visited/discovered set even when a graph has cycles or self-loops.'),
                block('tradeoff', 'When the first route is shortest', 'For unweighted edges, the first discovery of a vertex gives its minimum number of edges from the source. This does not find the cheapest weighted route. With adjacency lists, BFS uses O(V+E) time and O(V) auxiliary state. Unreachable vertices remain undiscovered. The small teaching network is generated and directed; the linked problems accept explicit graph input.'),
            ],
            code=['queue.add(0); seen[0] = true;', 'while (!queue.isEmpty()) { int u = queue.remove();', '  for (int v : neighbours[u]) if (!seen[v]) {', '    seen[v] = true; queue.add(v); }', '} // every reachable vertex was processed once'],
            predict=('After expanding vertex 0, its newly discovered neighbours are 1 and 2. What is the queue?', ['[1, 2]', '[2, 1]', '[0, 1, 2]'], 0, 'Vertex 0 has already left the queue. A FIFO queue retains the discovery order of 1 and 2.'),
            pattern=('A directed, unweighted graph has up to 100000 vertices. You need minimum edge counts from one source. Which approach fits?', ['Depth-first search always gives shortest paths: O(V+E)', 'BFS with a queue: O(V+E)', 'Sort all edges by weight: O(E log E)'], 1, 'BFS explores by edge-distance layers. DFS can discover a longer route first.'),
            dry_step=3, fields=[('visiting', 'Currently processing vertex'), ('discovered', 'Just-discovered vertex'), ('frontier', 'Queue, front to back')],
            dry_prompt='Fill the table immediately after vertex 0 discovers and enqueues neighbour 2.', dry_hint='The earlier neighbour is still waiting. Enter queue IDs separated by commas.',
            goal='Change the input length so exactly five vertices are processed in this generated teaching graph.', rule=dict(path='variables.visited', equals=5),
            linked=['reachable-rooms', 'fewest-doors'], prerequisites=['lesson-queue'],
        ),
        'tabulation': dict(
            input='0,1', target=7, topics=['Dynamic programming'],
            body='Imagine a row of small solved questions. A later cell can depend on earlier cells, but never on a value that has not been computed. For Fibonacci, each cell is the sum of its two predecessors. Tabulation chooses an order that makes these dependencies available. Start by changing n and tracing the dependency arrows; the table is a record of reusable results, not a formula to memorize without understanding its base cases.',
            sections=[
                block('worked', 'Build the answer from the beginning', 'Set F(0)=0 and F(1)=1. Then F(2)=1, F(3)=2, F(4)=3, and F(5)=5. Computing F(7) reads 5 and 8 from the two preceding cells and stores 13. Each write highlights both dependencies and the destination so you can see why that computation is valid.'),
                block('invariant', 'Dependencies come before their users', 'Before iteration i, every table entry below i is final. The two dependencies at i-1 and i-2 are therefore available. Decide what a state means before writing a recurrence. Counting staircase routes has a similar recurrence but a different interpretation and base case: there is one empty route for zero steps.'),
                block('tradeoff', 'What the table saves', 'Naive recursive Fibonacci repeats the same subproblems many times. This table computes each state once, using O(n) time and O(n) storage. When only the final value is needed, retain two previous values for O(1) extra storage. Keeping the full table is useful here because it makes the dependency order visible.'),
            ],
            code=['int[] dp = new int[n + 1];', 'if (n > 0) dp[1] = 1;', 'for (int i = 2; i <= n; i++) dp[i] = dp[i - 1] + dp[i - 2];', '// every dependency was computed before its user', 'return dp[n];'],
            predict=('F(4)=3 and F(5)=5 are final. Which value belongs in F(6)?', ['5', '8', '13'], 1, 'Read F(5) and F(4), then add 5 + 3. F(7), not F(6), is 13.'),
            pattern=('A recurrence repeatedly requests the same smaller states and you can order those dependencies. Which approach avoids repeating the work?', ['Compute each state once in a table', 'Recompute both branches every time', 'Sort the resulting answers'], 0, 'Tabulation stores each state after its dependencies. A correct state definition and base cases come first.'),
            dry_step=4, fields=[('i', 'Destination index'), ('value', 'Stored value')], dry_prompt='Fill the state table immediately after computing F(5).', dry_hint='F(3)=2 and F(4)=3. Use the destination index, not the count of animation steps.',
            goal='Choose n so the stored Fibonacci result is 21. The teaching table supports n from 0 to 16.', rule=dict(path='variables.result', equals=21),
            linked=['fibonacci-station', 'staircase'], prerequisites=['lesson-recursion'],
        ),
    }
    for lesson in lessons:
        alg = lesson['experiment']['algorithm']
        if alg not in settings:
            continue
        spec = settings[alg]
        scene = dict(algorithm=alg, input=spec['input'], target=spec['target'], seed=42)
        lesson.update(body=spec['body'], blocks=spec['sections'], code=spec['code'], experiment=scene, topics=spec['topics'], prerequisites=spec['prerequisites'], referenceJourney=True, minutes=15,
                      linkedProblems=['problem-' + name for name in spec['linked']])
        challenges = []
        for kind, key, title in [('prediction', 'predict', 'Predict the next change'), ('pattern', 'pattern', 'Spot the pattern')]:
            prompt, options, answer, explanation = spec[key]
            challenges.append(dict(id=f'challenge-{alg}-{kind}', kind=kind, title=title, prompt=prompt, options=options, answer=answer, explanation=explanation, hint=lesson['invariant']))
        challenges.append(dict(id=f'challenge-{alg}-manipulation', kind='manipulation', title='Make the model your own', prompt=spec['goal'], scene=scene, rule=spec['rule'], explanation='The Java-computed final state meets the goal. Try a second input to test the same idea.', hint=lesson['pitfall'], **({'requiredTarget': spec['requiredTarget']} if 'requiredTarget' in spec else {})))
        challenges.append(dict(id=f'challenge-{alg}-dry-run', kind='dry-run', title='Dry-run the state', prompt=spec['dry_prompt'], scene=scene, traceStep=spec['dry_step'], fields=[dict(key=key, label=label) for key, label in spec['fields']], explanation='Your entries agree with the actual Java trace for this fixed input.', hint=spec['dry_hint']))
        lesson['challenges'] = challenges

    enrich_problems(problems)


def enrich_problems(problems):
    py = {
        'three-window': 'a = list(map(int, input().split()))\nk = min(3, len(a))\nwindow = sum(a[:k])\nbest = window\nfor right in range(k, len(a)):\n    window += a[right] - a[right-k]\n    best = max(best, window)\nprint(best)',
        'distinct-windows': 'a = list(map(int, input().split()))\nprint(*(1 if x == y else 2 for x, y in zip(a, a[1:])))',
        'bst-inorder': 'a = list(map(int, input().split()))\nprint(*sorted(set(a)))',
        'tree-height': '''a = list(map(int, input().split()))
nodes = []
for value in a:
    if not nodes:
        nodes.append([value, None, None])
        continue
    at = 0
    while nodes[at][0] != value:
        side = 1 if value < nodes[at][0] else 2
        if nodes[at][side] is None:
            nodes[at][side] = len(nodes)
            nodes.append([value, None, None])
            break
        at = nodes[at][side]
stack = [(0, 1)]
height = 0
while stack:
    at, depth = stack.pop()
    height = max(height, depth)
    for child in nodes[at][1:]:
        if child is not None:
            stack.append((child, depth + 1))
print(height)''',
        'fibonacci-station': 'n = int(input())\na, b = 0, 1\nfor _ in range(n):\n    a, b = b, a+b\nprint(a)',
        'staircase': 'n = int(input())\na, b = 1, 1\nfor _ in range(n):\n    a, b = b, a+b\nprint(a)',
    }
    graph_python = '''data = list(map(int, open(0).read().split()))
n, m = data[:2]
graph = [[] for _ in range(n)]
for i in range(m):
    u, v = data[2+2*i:4+2*i]
    graph[u].append(v)
distance = [-1] * n
distance[0] = 0
queue = [0]
head = 0
while head < len(queue):
    u = queue[head]
    head += 1
    for v in graph[u]:
        if distance[v] == -1:
            distance[v] = distance[u] + 1
            queue.append(v)
'''
    py['reachable-rooms'] = graph_python + 'print(sum(d >= 0 for d in distance))'
    py['fewest-doors'] = graph_python + 'print(*distance)'
    cpp = {
        'three-window': 'vector<long long>a;long long x;while(cin>>x)a.push_back(x);int k=min(3,(int)a.size());long long sum=0,best=LLONG_MIN;for(int i=0;i<(int)a.size();i++){sum+=a[i];if(i>=k)sum-=a[i-k];if(i>=k-1)best=max(best,sum);}cout<<best;',
        'distinct-windows': 'vector<long long>a;long long x;while(cin>>x)a.push_back(x);for(int i=0;i+1<(int)a.size();i++)cout<<(a[i]==a[i+1]?1:2)<<" ";',
        'bst-inorder': 'set<long long>s;long long x;while(cin>>x)s.insert(x);for(auto value:s)cout<<value<<" ";',
        'tree-height': 'struct N{long long v;int l=-1,r=-1;};vector<N>t;long long x;while(cin>>x){if(t.empty()){t.push_back({x});continue;}int at=0;while(t[at].v!=x){int child=x<t[at].v?t[at].l:t[at].r;if(child<0){int next=t.size();if(x<t[at].v)t[at].l=next;else t[at].r=next;t.push_back({x});break;}at=child;}}vector<pair<int,int>>st{{0,1}};int h=0;while(!st.empty()){auto entry=st.back();int at=entry.first,d=entry.second;st.pop_back();h=max(h,d);if(t[at].l>=0)st.push_back({t[at].l,d+1});if(t[at].r>=0)st.push_back({t[at].r,d+1});}cout<<h;',
        'fibonacci-station': 'int n;cin>>n;long long a=0,b=1;while(n--){long long c=a+b;a=b;b=c;}cout<<a;',
        'staircase': 'int n;cin>>n;long long a=1,b=1;while(n--){long long c=a+b;a=b;b=c;}cout<<a;',
    }
    graph_cpp = 'int n,m;cin>>n>>m;vector<vector<int>>g(n);for(int i=0,u,v;i<m;i++){cin>>u>>v;g[u].push_back(v);}vector<int>d(n,-1);queue<int>q;d[0]=0;q.push(0);while(!q.empty()){int u=q.front();q.pop();for(int v:g[u])if(d[v]<0){d[v]=d[u]+1;q.push(v);}}'
    cpp['reachable-rooms'] = graph_cpp + 'cout<<count_if(d.begin(),d.end(),[](int x){return x>=0;});'
    cpp['fewest-doors'] = graph_cpp + 'for(int x:d)cout<<x<<" ";'
    teaching = {
        'three-window': ('Maintain the sum of the last min(3,n) values and update best only for full windows. Initialize best from the first real window so negative arrays work.', ['Exactly three means contiguous positions, not the three largest values.', 'After the first window, subtract the outgoing value before adding the incoming one.', 'Initialize best from a complete window; zero is not a safe baseline for all-negative input.']),
        'distinct-windows': ('A window contains exactly two values. It has one distinct value when both are equal, otherwise two. Compare each neighbouring pair without sorting.', ['There is no complete pair for a one-value input.', 'A two-value window needs only an equality check.', 'Output one result per adjacent pair, retaining the original order.']),
        'bst-inorder': ('In-order traversal of a BST yields its distinct keys in sorted order. A sorted set is an equivalent output-oriented reference for this problem; the lesson separately demonstrates explicit BST insertion. An explicit traversal is also valid.', ['Duplicates are ignored, not counted.', 'In-order means left subtree, node, then right subtree.', 'Output-oriented approaches can use a sorted set; explicit BST insertion has O(nh) worst-case cost over n insertions.']),
        'tree-height': ('Build the unbalanced BST in input order, ignoring duplicates. Traverse it with depth starting at one for the root, then return the largest depth. Sorting first changes the tree and is incorrect.', ['A root alone has height one in this problem.', 'Insertion order changes the shape; do not sort the readings.', 'Repeated values create no node. An iterative stack can measure height without deep recursive calls.']),
        'reachable-rooms': ('Build directed adjacency lists. Start a queue at vertex 0 and mark vertices when enqueued. Count processed vertices. Cycles, repeated edges, and self-loops must not enqueue a discovered vertex again.', ['Directed reachability does not automatically include the reverse edge.', 'The source counts as reachable even with no edges.', 'Mark on enqueue, then each vertex enters the queue at most once.']),
        'fewest-doors': ('Initialize all distances to -1 and the source to 0. When BFS first discovers v from u, set distance[v]=distance[u]+1. Queue order makes the first distance minimal for unweighted edges.', ['Keep -1 for vertices never discovered.', 'The source distance is zero, not one.', 'Assign the distance when enqueuing a vertex for the first time.']),
        'fibonacci-station': ('Start with the consecutive pair F(0)=0 and F(1)=1. Advance the pair n times. The first value is then F(n). A table is equally valid; two variables reduce extra storage.', ['Handle n=0 before assuming a positive index.', 'Keep two consecutive Fibonacci values.', 'Update both values using the old pair, not an overwritten first variable.']),
        'staircase': ('Let ways[i] count ordered routes to step i. The last move is either one step or two, so ways[i]=ways[i-1]+ways[i-2]. ways[0]=1 represents the empty route; ways[1]=1.', ['There is one way to climb zero steps: take no steps.', 'Partition routes by whether their final move has length one or two.', 'This recurrence resembles Fibonacci but starts from 1,1.']),
    }
    for problem in problems:
        slug = problem['id'].removeprefix('problem-')
        if slug not in py:
            continue
        problem['referenceJourney'] = True
        problem['references'] = dict(java=problem['reference'], python='import sys\n' + py[slug].replace('list(map(int, input().split()))', 'list(map(int, sys.stdin.read().split()))').replace('open(0).read()', 'sys.stdin.read()').replace('int(input())', 'int(sys.stdin.read())') + '\n', cpp='#include <bits/stdc++.h>\nusing namespace std;\nint main(){ios::sync_with_stdio(false);cin.tie(nullptr);' + cpp[slug] + '\n}\n')
        text, hints = teaching[slug]
        problem['hints'] = hints
        problem['editorial'] = text + '\n\nTest the smallest valid input, repeated values, and the relevant disconnected or all-negative case. Compare against the stated output format; hidden cases use the same rules.'
        if slug in ('reachable-rooms', 'fewest-doors'):
            problem['inputFormat'] = 'Read n m, followed by m directed edges u v. Values may be separated by spaces or newlines.'
        elif slug in ('fibonacci-station', 'staircase'):
            problem['inputFormat'] = 'Read one integer n from 0 through 30.'

        # Independent adversarial cases and whitespace parsing apply equally to all languages.
        cases = {
            'three-window': [('-5 -2 -9 -4', '-15'), ('0 0 0 0', '0')],
            'distinct-windows': [('7 7 7 7', '1 1 1'), ('1 2 2 3', '2 1 2')],
            'bst-inorder': [('4 4 4 4', '4'), ('5 4 3 2 1', '1 2 3 4 5')],
            'tree-height': [('4 4 4 4', '1'), ('5 4 3 2 1', '5')],
            'reachable-rooms': [('5 4 0 1 1 0 2 3 3 4', '2'), ('3 5 0 0 0 1 0 1 1 2 2 0', '3')],
            'fewest-doors': [('5 4 0 1 1 0 2 3 3 4', '0 1 -1 -1 -1'), ('3 5 0 0 0 1 0 1 1 2 2 0', '0 1 2')],
            'fibonacci-station': [('30', '832040')], 'staircase': [('30', '1346269')],
        }
        for source, expected in cases[slug]:
            problem['tests'].append(dict(input=source+'\n', output=expected+'\n', public=False))
        example=problem['tests'][3]
        problem['tests'].append(dict(input='\n'.join(example['input'].split())+'\n',output=example['output'],public=False))

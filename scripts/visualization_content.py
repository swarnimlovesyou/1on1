"""Execution-backed model configurations; no frontend-generated algorithm results."""
SCENES = {
    'complexity':dict(input='8',target=8),
    'arrays':dict(input='2,1,5',target=0),
    'strings':dict(input='',target=0,words='cat'),
    'hashing':dict(input='2,1,6,2,5',target=0),
    'prefix-sums':dict(input='2,1,5',target=0,words='1,3'),
    'variable-window':dict(input='',target=0,words='abba'),
    'intervals':dict(input='1,3,2,6,8,10',target=0),
    'matrices':dict(input='1,2,3,4,5,6',target=3),
    'graphs':dict(input='0,1,0,2,2,3',target=4),
    # Phase 3: fixed contract with the board traces (algorithm id = lesson slug)
    'union-find':dict(input='0,1,2,3,1,2,4,5',target=6),
    'topological-sort':dict(input='0,2,1,2,2,3,3,4,1,4',target=5),
    'kruskal':dict(input='0,1,4,0,2,1,1,2,2,1,3,5,2,3,8,3,4,3',target=5),
    'bellman-ford':dict(input='0,1,6,0,2,7,1,2,8,1,3,5,2,3,-3,3,1,-2',target=4),
    'floyd-warshall':dict(input='0,1,3,1,2,1,0,2,7,2,3,2',target=4),
    'segment-tree':dict(input='5,2,7,1,3,6|1,4',target=0),
    'fenwick':dict(input='5,2,7,1,3,6',target=4),
    'interval-scheduling':dict(input='1,4,3,5,0,6,5,7,3,9,5,9,6,10,8,11',target=0),
    'bits':dict(input='4,1,2,1,2',target=0),
    'kmp':dict(input='',target=0,words='abxabcabcaby|abcaby'),
    'rabin-karp':dict(input='',target=0,words='abracadabra|cad'),
    'monotonic-stack':dict(input='2,1,5,6,2,3',target=0),
    'monotonic-queue':dict(input='1,3,-1,-3,5,3,6,7',target=3),
    'knapsack':dict(input='1,1,3,4,4,5,5,7',target=7),
    'lcs':dict(input='',target=0,words='abcde|ace'),
    'interval-dp':dict(input='10,30,5,60',target=0),
}

def enrich(lessons,curriculum):
    code={
      'bst':['start at root; duplicate keys reuse a node;','compare key; descend into the ordered subtree;','AVL: rotate local subtree if its balance bound is exceeded;','return the updated subtree;'],
      'linked-list':['previous=null; current=head;','save next=current.next;','reverse current.next; advance previous and current;','return previous as the new head;'],
      'recursion':['if n==0: return 1;','call factorial(n-1); suspend frame n;','resume the smaller result;','return n * smaller;'],
      'merge-sort':['split a nontrivial range at mid;','sort the left half;','sort the right half;','merge ordered fronts into a buffer; commit the run;'],
      'quick-sort':['stop at a trivial candidate range;','choose a pivot;','compare values and partition at the boundary;','place pivot; continue in the appropriate subranges;','selection returns when the requested rank is fixed;'],
      'heap':['create an empty max-heap;','compare the inserted child with its parent;','swap upward until parent >= child;','read the maximum at the root;'],
      'memoization':['enter F(n); test the base cases;','reuse a known cached value;','compute smaller dependencies;','store the result and return to the caller;','read the requested answer;'],
      'backtracking':['start with an empty path;','snapshot the current subset;','choose a next input position and explore;','undo the last choice;','return to the parent branch;'],
      'trie':['start at the shared root;','follow or create one prefix edge;','mark the endpoint as a complete word;','return to root for the next word;'],
      'bloom-filter':['zero the bit array;','set the first hash position;','set the second hash position;','query bits; verify positives with an exact set;'],
      'set-cover':['define goals and candidate topic sets;','count each candidate’s uncovered gain;','choose the largest gain; remove those goals;','stop if no positive gain exists;','report selected sets and uncovered goals;'],
      'dijkstra':['distance[source]=0; others=infinity;','choose the smallest unsettled tentative cost;','finalize the vertex and relax its outgoing edges;','keep predecessor and cost updates;','repeat until no reachable unsettled vertex remains;'],
    }
    code['avl']=code['bst'];code['quickselect']=code['quick-sort']
    for lesson in lessons:
        slug=lesson['id'].removeprefix('lesson-')
        if slug in SCENES:lesson['experiment']=dict(algorithm=slug,seed=42,**SCENES[slug])
        if slug=='tree-traversal':lesson['experiment'].update(input='4,2,7,1,3,6',words='inorder')
        if slug=='avl':lesson['experiment']['input']='30,20,10,25,28,27'
        if slug=='bloom-filter':lesson['experiment']['words']='tree,graph,heap | sheep'
        if slug=='set-cover':lesson['experiment']['words']='Arrays,Hashing,Trees,Graphs,DP'
        if slug in code:lesson['code']=code[slug]
        lesson['interactiveStatus']='interactive'
        lesson['traceRevision']=3
    by_id={l['id']:l for l in lessons}
    for concept in curriculum['concepts']:
        visual=concept['visualization']
        visual['scene']=by_id[concept['lessonIds'][0]]['experiment']
        visual['interactiveStatus']='interactive'
        visual['traceRevision']=3
        visual['gaps']=['This is bounded authored execution, not tracing arbitrary student code.']
        if concept['id'] in ['concept-bfs','concept-dfs']:
            visual['gaps'].append('Traversal graphs are generated from numeric inputs; arbitrary grid/multi-source practice is outside this scene.')
        if concept['id']=='concept-dynamic-programming':visual['gaps'].append('The interactive dependency example is Fibonacci; staircase and House Robber practice remain distinct Phase 2 applications.')
    curriculum['visualizationRevision']=3

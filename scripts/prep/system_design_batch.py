"""System design guides for the System design track (Prep). Checked by check_prep.py."""

GUIDES = [
    dict(
        id='guide-system-design-scaling-basics', kind='guide', track='system-design',
        title='Scaling basics and estimation', order=1,
        summary="Scaling means adding capacity either by buying a bigger machine or by adding more machines, and quick estimates of traffic, storage and bandwidth tell you which you need.",
        sections=[
            dict(title='Vertical versus horizontal scaling', text=(
                "Vertical scaling (scaling up) means giving one machine more CPU, memory or faster disks. "
                "It needs no code changes, which makes it the natural first step. Its limits are hard ones: "
                "the biggest machine you can buy has a ceiling, prices rise steeply near the top end, and the one machine is still a single point of failure. "
                "Upgrading it often means downtime too.\n\n"
                "Horizontal scaling (scaling out) means running many ordinary machines side by side and spreading the work across them, usually behind a load balancer. "
                "Capacity grows roughly in step with the number of machines, and losing one machine removes only a slice of capacity instead of the whole service.\n\n"
                "The price of scaling out is complexity. Requests for the same user may land on different machines, so any state kept on one machine becomes a problem. "
                "Data must be split or copied, and you now have a distributed system with network failures between its parts. "
                "In interviews, a good answer usually starts simple, scales up while that is cheap, and explains what has to change before scaling out."
            )),
            dict(title='Stateless services', text=(
                "A service is stateless when any instance can handle any request, because nothing a request needs is stored only in that instance's memory or local disk. "
                "Session data, uploaded files and shopping carts live in a shared store instead: a database, a cache such as Redis, or object storage.\n\n"
                "Consider a login session kept in the memory of server A. If the load balancer sends the user's next request to server B, "
                "B has never heard of that session and the user appears logged out. "
                "Move the session into a shared cache, or into a signed token the client sends with every request, and A and B become interchangeable.\n\n"
                "Statelessness is what makes horizontal scaling easy. You can add instances when traffic rises, remove them when it falls, "
                "and replace a crashed instance without losing anything. "
                "The state has not disappeared; it has moved to a layer built to be shared and replicated, which then becomes the part you have to scale carefully."
            )),
            dict(title='Back-of-the-envelope estimation', text=(
                "Estimates turn vague requirements into numbers you can design around. Round aggressively; the goal is the right order of magnitude, not three decimal places. "
                "A day has 86,400 seconds, and treating it as about 100,000 is fine for quick mental maths.\n\n"
                "Traffic: suppose 5 million daily active users each make 30 requests a day. "
                "That is 150 million requests ÷ 86,400 s ≈ 1,700 requests per second on average. "
                "Traffic is not flat, so assume a peak of about 3× the average, roughly 5,200 requests per second.\n\n"
                "Storage: if users create 2 million posts a day at about 1 KB each, that is 2 GB a day, 730 GB a year and about 3.65 TB over five years. "
                "Keeping three copies for safety brings it to roughly 11 TB.\n\n"
                "Bandwidth: 1,700 responses per second at 50 KB each is about 85 MB/s, roughly 680 Mbit/s of outgoing traffic.\n\n"
                "Servers: if one application server comfortably handles 800 requests per second, the 5,200 peak needs 5,200 ÷ 800 ≈ 6.5, so 7 servers, plus spares for failures."
            )),
            dict(title='Using the numbers to make decisions', text=(
                "Numbers matter only if they change the design. A few hundred writes per second fits easily on one well-tuned database, "
                "so sharding at that level is premature. Tens of thousands of reads per second for the same popular items points straight at caching. "
                "Several terabytes of images suggests object storage plus a CDN rather than database rows.\n\n"
                "Separate reads from writes when you estimate, because they scale differently. A read-heavy system with a 100:1 ratio "
                "can lean on caches and read replicas; a write-heavy one needs partitioning sooner.\n\n"
                "State your assumptions out loud, such as the number of users, requests per user, object size and peak factor, so the interviewer can correct one of them "
                "without throwing away the whole calculation. "
                "Finally, sanity-check the result: if the estimate says one user generates a gigabyte a day of text, an assumption is probably off by a factor of a thousand."
            )),
        ],
        keyPoints=[
            'Vertical scaling is simple but has a hardware ceiling and stays a single point of failure.',
            'Horizontal scaling adds machines and needs stateless services to work smoothly.',
            'Keep session and user state in a shared store so any instance can serve any request.',
            'Average QPS = daily requests ÷ 86,400; plan for a peak several times higher.',
            'Estimate traffic, storage and bandwidth separately, and let the numbers drive the design.',
        ],
        challenges=[
            dict(id='challenge-system-design-scaling-basics-q1', kind='prediction', title='Average requests per second',
                 prompt="An app has 4 million daily active users, and each makes 15 requests per day spread evenly across the day. Roughly what is the average request rate?",
                 options=['About 70 requests/s', 'About 700 requests/s', 'About 7,000 requests/s', 'About 70,000 requests/s'], answer=1,
                 explanation="4 million × 15 = 60 million requests a day, and 60,000,000 ÷ 86,400 ≈ 694, so about 700 per second. About 7,000 comes from dividing by roughly 8,640 instead of 86,400, a factor-of-ten slip in the seconds per day.",
                 hint='Find the requests per day first, then divide by the number of seconds in a day.'),
            dict(id='challenge-system-design-scaling-basics-q2', kind='prediction', title='Storage for uploads',
                 prompt="Users upload 500,000 files a day, each 2 MB on average. Files are kept for 3 years (use 365 days a year) and you ignore replication. Roughly how much storage is needed?",
                 options=['About 110 TB', 'About 365 TB', 'About 11 PB', 'About 1.1 PB'], answer=3,
                 explanation="500,000 × 2 MB = 1,000,000 MB = 1 TB per day. Over 1,095 days that is about 1,095 TB, or roughly 1.1 PB. 365 TB is only one year of uploads, forgetting the 3-year retention.",
                 hint='Work out the daily volume in terabytes before multiplying by the retention period.'),
            dict(id='challenge-system-design-scaling-basics-q3', kind='prediction', title='Session in local memory',
                 prompt="Two app servers sit behind a round-robin load balancer with no sticky sessions. Login sessions are stored only in each server's local memory. A user logs in through server A. What happens on the next request?",
                 options=['If it goes to server B, the user appears logged out', 'Server B fetches the session from server A automatically', 'The load balancer copies the session to server B', 'Nothing changes, because the browser keeps the session'],
                 answer=0,
                 explanation="Round robin can send the user's next request to B, and B has no copy of a session that lives only in A's memory, so the user looks logged out. Servers do not share memory or fetch sessions from each other unless you build that; the usual fix is a shared session store.",
                 hint='Ask where the session data actually lives and which machines can see it.'),
            dict(id='challenge-system-design-scaling-basics-q4', kind='prediction', title='The limit of scaling up',
                 prompt="A team keeps upgrading its single database server to a larger machine. Which problem does this approach leave unsolved, however much money they spend?",
                 options=['Queries need to be rewritten for each new machine', 'Data has to be split across machines', 'There is still one machine whose failure takes the service down'],
                 answer=2,
                 explanation="A bigger machine adds capacity but not redundancy: it remains a single point of failure, and there is also a ceiling on how big it can get. Splitting data across machines is what horizontal scaling requires, which vertical scaling specifically avoids.",
                 hint='Think about what happens on the day that one machine breaks.'),
            dict(id='challenge-system-design-scaling-basics-q5', kind='prediction', title='Servers for peak',
                 prompt="Average traffic is 2,000 requests/s and peak is 3× the average. One server handles 500 requests/s at its target load. Ignoring spares, what is the minimum number of servers to cover peak?",
                 options=['4', '6', '12', '18'], answer=2,
                 explanation="Peak is 3 × 2,000 = 6,000 requests/s, and 6,000 ÷ 500 = 12 servers. Four servers covers only the average load, which would overload during the peak.",
                 hint='Size for the busiest moment, not for the typical one.'),
        ],
    ),
    dict(
        id='guide-system-design-load-balancing', kind='guide', track='system-design',
        title='Load balancing', order=2,
        summary="A load balancer spreads incoming requests across healthy servers, choosing a target with an algorithm and removing servers that fail health checks.",
        sections=[
            dict(title='Layer 4 versus layer 7', text=(
                "A load balancer sits in front of a pool of servers and decides which one handles each request. "
                "The main design choice is how much of the request it looks at.\n\n"
                "A layer 4 balancer works at the transport level. It sees IP addresses, ports and the TCP or UDP connection, but not what is inside the stream. "
                "It picks a server when a connection opens and then forwards bytes. Because it does so little, it is fast and cheap, "
                "but it cannot route by URL, header or cookie.\n\n"
                "A layer 7 balancer understands the application protocol, usually HTTP. It can terminate TLS, read the path and headers, "
                "send /images to one pool and /api to another, rewrite headers, and retry a failed request on another server. "
                "That flexibility costs more CPU per request, and the balancer must hold the TLS certificates.\n\n"
                "Many setups use both: a layer 4 tier spreading connections across several layer 7 balancers, which then route by content. "
                "Tools such as NGINX, HAProxy and Envoy can act at either level."
            )),
            dict(title='Choosing a server', text=(
                "Round robin hands requests to servers in turn: A, B, C, A, B, C. It is simple and works well when servers are identical and requests cost about the same. "
                "Weighted round robin gives a bigger server a larger share.\n\n"
                "Least connections sends the next request to the server with the fewest active connections. "
                "If A has 10 open connections, B has 4 and C has 7, the next one goes to B. "
                "This adapts when some requests are slow, such as long uploads, because busy servers naturally receive less new work.\n\n"
                "Hash-based routing picks the server from a hash of something in the request, such as the user ID, so the same key keeps reaching the same server. "
                "That helps when servers hold per-key caches. Plain modulo hashing (hash mod N) breaks badly when N changes: "
                "going from 4 servers to 5 sends about 80% of keys to a different server. "
                "Consistent hashing places servers and keys on a ring, so adding a fifth server moves only about 1/5 of the keys, the ones that now fall in its slice. "
                "Virtual nodes, many points per server on the ring, keep the slices even."
            )),
            dict(title='Health checks', text=(
                "A load balancer must stop sending traffic to servers that cannot serve it. "
                "Active health checks probe each server on a schedule, for example an HTTP request to /health every 5 seconds. "
                "To avoid reacting to a single slow reply, a server is usually marked unhealthy only after several consecutive failures, "
                "and marked healthy again only after several successes.\n\n"
                "The trade-off is detection time. With a 5 second interval and a threshold of 3 failures, a server that dies just after a passing check "
                "is removed about 15 seconds later, and requests sent to it in that window fail or must be retried. "
                "Shorter intervals detect faster but add probe traffic and risk flapping.\n\n"
                "Passive checks watch real traffic instead: if a server keeps returning errors or timing out, it is pulled out. "
                "A good /health endpoint checks what the server really needs, such as its database connection, "
                "but should not fail just because one optional dependency is slow, or a single shared problem could empty the entire pool at once."
            )),
            dict(title='Sticky sessions and why to avoid them', text=(
                "Sticky sessions (session affinity) make the balancer send all requests from one client to the same server, usually via a cookie or the client's IP. "
                "They are a quick patch for servers that keep session data in local memory.\n\n"
                "The patch has costs. Load becomes uneven, because a few heavy users can pin themselves to one server while others sit idle. "
                "When that server crashes or is redeployed, every user stuck to it loses their session. "
                "Scaling out does not help existing users, since they stay attached to their old server, and draining a server for maintenance takes as long as its longest session.\n\n"
                "The better fix is to make servers stateless: keep sessions in a shared store or in a signed token, "
                "and then any server can handle any request and the balancer is free to use its best algorithm. "
                "Hash-based routing for cache efficiency is different: it is an optimisation, and correctness does not depend on it if a request lands elsewhere."
            )),
        ],
        keyPoints=[
            'Layer 4 balances connections by IP and port; layer 7 reads HTTP and can route by path or header.',
            'Round robin suits identical servers; least connections adapts to uneven request cost.',
            'Modulo hashing remaps most keys when servers change; consistent hashing moves only about 1/N.',
            'Health checks trade detection speed against probe load and flapping.',
            'Prefer stateless servers over sticky sessions, which cause uneven load and lost sessions on failure.',
        ],
        challenges=[
            dict(id='challenge-system-design-load-balancing-q1', kind='prediction', title='Routing by path',
                 prompt="Requests to /video/* must go to a video server pool and everything else to a web pool, all on the same host and port over HTTPS. Which kind of load balancer can do this routing?",
                 options=['A layer 4 balancer', 'A layer 7 balancer', 'Either, since both see the port'], answer=1,
                 explanation="The path is part of the HTTP request, so only a balancer that terminates TLS and parses HTTP (layer 7) can see it. A layer 4 balancer sees only addresses and ports, which are identical for both kinds of request here.",
                 hint='Decide which layer the URL path belongs to.'),
            dict(id='challenge-system-design-load-balancing-q2', kind='prediction', title='Least connections',
                 prompt="A balancer uses least connections. Server A has 12 active connections, B has 5 and C has 9. All servers have equal weight. Where does the next request go?",
                 options=['Server A', 'Server C', 'Server B', 'Whichever is next in round-robin order'], answer=2,
                 explanation="Least connections picks the server with the fewest active connections, which is B with 5. Round-robin order is irrelevant to this algorithm; it only counts current connections.",
                 hint='The algorithm name tells you what it compares.'),
            dict(id='challenge-system-design-load-balancing-q3', kind='prediction', title='Modulo hashing on resize',
                 prompt="Keys are uniformly spread and assigned with hash(key) mod N. The pool grows from 4 servers to 5. Roughly what fraction of keys now map to a different server?",
                 options=['About 20%', 'About 50%', 'About 80%', 'About 25%'], answer=2,
                 explanation="A key stays put only when hash mod 4 equals hash mod 5, which happens for 4 out of every 20 hash values, so about 20% stay and about 80% move. 20% is what consistent hashing would move, not modulo hashing.",
                 hint='Check a run of consecutive hash values, say 0 to 19, under both moduli.'),
            dict(id='challenge-system-design-load-balancing-q4', kind='prediction', title='Consistent hashing on resize',
                 prompt="A consistent-hashing ring with many virtual nodes per server has 10 equally weighted servers. An 11th is added. Roughly what fraction of keys move?",
                 options=['About 9%', 'About 50%', 'About 91%'], answer=0,
                 explanation="The new server takes over an even share of the ring, 1/11 ≈ 9% of keys, and only those move. About 91% is the behaviour of naive modulo hashing, which consistent hashing is designed to avoid.",
                 hint='Ask what share of the ring the newcomer ends up owning.'),
            dict(id='challenge-system-design-load-balancing-q5', kind='prediction', title='Detection time',
                 prompt="Health checks run every 10 seconds and a server is removed after 3 consecutive failed checks. Probe timeouts are negligible. A server crashes immediately after passing a check. In the worst case, how long until it is removed?",
                 options=['10 seconds', '20 seconds', '3 seconds', '30 seconds'], answer=3,
                 explanation="The next three checks happen at 10, 20 and 30 seconds after the crash, and only the third failure crosses the threshold, so removal happens at about 30 seconds. 10 seconds would be right only if a single failure were enough.",
                 hint='Count how many probes must fail and when each one runs.'),
        ],
    ),
    dict(
        id='guide-system-design-caching', kind='guide', track='system-design',
        title='Caching', order=3,
        summary="A cache keeps copies of frequently read data in fast storage, and its write strategy, expiry and eviction policy decide how fresh, safe and effective it is.",
        sections=[
            dict(title='Cache-aside, write-through and write-back', text=(
                "Cache-aside (lazy loading) is the most common pattern. On a read, the application checks the cache; on a miss it reads the database, "
                "stores the result in the cache and returns it. On a write, it updates the database and deletes the cached entry so the next read reloads it. "
                "Only data that is actually read gets cached, and a cache outage slows the system down without breaking correctness, "
                "provided the database can absorb the extra reads.\n\n"
                "Write-through writes to the cache and the database together as part of every write, so recently written data is already cached and normally fresh "
                "(a failure between the two writes can still leave them out of step), "
                "at the cost of slower writes and caching data that may never be read.\n\n"
                "Write-back (write-behind) writes only to the cache and flushes changes to the database later, often in batches. "
                "Writes become very fast and repeated updates to the same key collapse into one database write. "
                "The danger is durability: if the cache node fails before flushing, those writes are lost. "
                "Use write-back only where losing a few recent updates is acceptable, such as view counters, or where the cache itself is replicated and persisted."
            )),
            dict(title='Expiry and eviction', text=(
                "A time-to-live (TTL) makes an entry expire after a fixed period, bounding how stale it can get. "
                "Short TTLs mean fresher data and more misses; long TTLs mean fewer misses and older data. "
                "TTLs are also a safety net when an invalidation is missed.\n\n"
                "Eviction is different: it decides what to throw out when the cache is full. "
                "Least recently used (LRU) removes the entry that has gone longest without being read. "
                "With room for three entries and the access sequence A, B, C, A, D, the cache evicts B, because A was touched again after B.\n\n"
                "Least frequently used (LFU) removes the entry with the fewest reads, which protects steadily popular items from a one-off scan "
                "of many cold keys, but can keep formerly popular items too long unless counts decay over time. "
                "LRU is a sensible default; LFU helps when popularity is stable and skewed. "
                "Real caches often approximate these policies; Redis, for example, approximates LRU by sampling a few keys and evicting the best candidate among them, which is cheaper than exact bookkeeping."
            )),
            dict(title='Hit rate and database load', text=(
                "The hit rate is the fraction of reads the cache answers. Small changes in it make large differences to the database, because what matters is the miss rate.\n\n"
                "Take 10,000 reads per second. At a 90% hit rate, 10% miss, so the database sees 1,000 reads per second. "
                "At 99%, only 1% miss, and the database sees 100 per second. Going from 90% to 99% sounds like a small gain but cuts database reads by a factor of ten.\n\n"
                "Latency improves the same way. If a hit costs 1 ms and a miss costs 21 ms (the cache check plus a 20 ms query), "
                "the average at 90% is 0.9 × 1 + 0.1 × 21 = 3 ms, and at 99% it is 0.99 × 1 + 0.01 × 21 = 1.2 ms.\n\n"
                "The flip side is fragility: a database sized for 100 reads per second cannot survive the cache going cold. "
                "After a cache restart, warm it gradually or limit the rate of misses that reach the database."
            )),
            dict(title='Cache stampedes', text=(
                "A stampede, also called a thundering herd, happens when a very popular key expires and many requests miss at the same moment. "
                "Each one goes to the database to rebuild the same value.\n\n"
                "Suppose a key is read 5,000 times per second and rebuilding it takes 200 ms. Without protection, every read in that 200 ms window misses, "
                "so roughly 5,000 × 0.2 = 1,000 identical queries hit the database at once, which can slow it down enough to cause further expiries and misses.\n\n"
                "Common defences: request coalescing, where only one request rebuilds the key while the others wait for its result or are served the old value; "
                "a short lock in the cache so only the lock holder queries the database; "
                "refreshing hot keys early, before they expire, sometimes with a probability that rises as expiry approaches; "
                "and adding random jitter to TTLs so keys written together do not all expire together. "
                "Serving slightly stale data for a moment is usually far better than overloading the database."
            )),
        ],
        keyPoints=[
            'Cache-aside loads on a miss and invalidates on write; it is the usual default.',
            'Write-back makes writes fast but can lose data if the cache fails before flushing.',
            'TTL bounds staleness; eviction (LRU, LFU) decides what goes when the cache is full.',
            'Database load is driven by the miss rate: 90% to 99% hit rate cuts misses tenfold.',
            'Prevent stampedes with request coalescing, early refresh and TTL jitter.',
        ],
        challenges=[
            dict(id='challenge-system-design-caching-q1', kind='prediction', title='Load behind the cache',
                 prompt="A service receives 20,000 reads per second and its cache-aside cache has a 95% hit rate. Every miss causes exactly one database read. How many database reads per second does this produce?",
                 options=['1,000', '19,000', '5,000', '950'], answer=0,
                 explanation="The miss rate is 5%, and 5% of 20,000 is 1,000 database reads per second. 19,000 is the number of hits, which the cache answers without touching the database.",
                 hint='Only the reads the cache cannot answer reach the database.'),
            dict(id='challenge-system-design-caching-q2', kind='prediction', title='LRU eviction',
                 prompt="An LRU cache holds 3 entries and starts empty. Keys are read in the order A, B, C, B, A, D. Which key is evicted when D is inserted?",
                 options=['A', 'B', 'C', 'D'], answer=2,
                 explanation="After A, B, C the least recently used is A. Reading B and then A makes C the least recently used, so C is evicted for D. A would be the answer only if re-reads did not update recency, which is first-in-first-out, not LRU.",
                 hint='After each read, move that key to the most recent position and track the order.'),
            dict(id='challenge-system-design-caching-q3', kind='prediction', title='Risk of write-back',
                 prompt="A system uses a write-back cache: writes go to a single, non-replicated cache node and are flushed to the database every 30 seconds. What is the main risk compared with write-through?",
                 options=['Reads become slower because the cache is bypassed', 'Recent writes are lost if the cache node fails before flushing', 'The database receives more writes than before'],
                 answer=1,
                 explanation="Until a flush, the only copy of a recent write is in the cache node, so a crash loses up to about 30 seconds of writes. The database actually receives fewer writes with write-back, because repeated updates to a key are combined.",
                 hint='Ask where the only copy of a fresh write lives during the 30 seconds.'),
            dict(id='challenge-system-design-caching-q4', kind='prediction', title='Cache-aside on a miss',
                 prompt="An application uses the cache-aside pattern. A read finds no entry in the cache. What happens next?",
                 options=['The cache fetches the row from the database by itself', 'The request fails until a writer fills the cache', 'The cache returns an empty value and the database is never read', 'The application reads the database, stores the result in the cache and returns it'],
                 answer=3,
                 explanation="In cache-aside the application owns the logic: it reads the database on a miss and populates the cache. A cache that loads from the database by itself is the read-through pattern, where the cache library or service does that work.",
                 hint='In this pattern the cache is a passive store sitting beside the database.'),
            dict(id='challenge-system-design-caching-q5', kind='prediction', title='Size of a stampede',
                 prompt="A hot key is read 4,000 times per second. It expires, and rebuilding it from the database takes 250 ms. There is no locking or request coalescing. Roughly how many database queries for this key arrive before the rebuilt value is cached?",
                 options=['1', '250', '1,000', '4,000'], answer=2,
                 explanation="Every read during the 250 ms rebuild window misses: 4,000 × 0.25 = 1,000 queries. Only one query would be sent if requests were coalesced, which this setup does not do.",
                 hint='Multiply the read rate by the length of the window in which the key is missing.'),
        ],
    ),
    dict(
        id='guide-system-design-databases-at-scale', kind='guide', track='system-design',
        title='Databases at scale', order=4,
        summary="Replication copies data to spread reads and survive failures, sharding splits data to spread writes and storage, and indexes keep each lookup cheap.",
        sections=[
            dict(title='Leader and follower replication', text=(
                "In leader-follower replication, one node (the leader) accepts all writes and streams its changes to one or more followers, also called replicas. "
                "Followers apply those changes in the same order and can serve reads. If the leader fails, a follower is promoted.\n\n"
                "Read replicas are the standard way to scale a read-heavy database, but every replica must still apply every write. "
                "Suppose each node handles 5,000 queries per second, applying one replicated write costs about as much as one query, "
                "the workload is 12,000 reads and 1,500 writes per second, and reads go only to replicas. "
                "The naive answer is 12,000 ÷ 5,000 = 2.4, so 3 replicas. "
                "But each replica spends 1,500 of its capacity applying writes, leaving 3,500 for reads, so you need 12,000 ÷ 3,500 ≈ 3.4, which means 4 replicas.\n\n"
                "Replication can be synchronous, where the leader waits for a follower to confirm before acknowledging a write, or asynchronous, where it does not wait. "
                "Asynchronous is faster and more available, but a leader that crashes may lose writes its followers never received."
            )),
            dict(title='Replication lag', text=(
                "With asynchronous replication, followers trail the leader by some amount, usually milliseconds but sometimes seconds under heavy load. "
                "That delay is replication lag, and it creates visible anomalies.\n\n"
                "The classic one: a user edits their profile, the write goes to the leader, then the page reloads and reads from a replica that has not yet applied the change. "
                "The user sees their old profile and assumes the save failed. "
                "Fixes for this read-your-writes problem include reading a user's own data from the leader for a short time after they write, "
                "or tracking the position of the user's last write and only reading from replicas that have caught up to it.\n\n"
                "Another anomaly is time appearing to go backwards: two reads hit two replicas with different lag, and the second shows older data than the first. "
                "Routing each user consistently to the same replica avoids that. "
                "Monitor lag as a first-class metric, and stop sending reads to a replica that falls too far behind."
            )),
            dict(title='Sharding and hot keys', text=(
                "Sharding (partitioning) splits one dataset across several databases, each holding a subset of rows. "
                "It spreads writes and storage, which replication alone cannot do. If you have 4 TB of data and want each shard to hold at most 400 GB, you need 10 shards.\n\n"
                "Range sharding assigns contiguous key ranges to shards, for example names A to F on shard 1. Range queries stay on one shard, "
                "but sequential keys such as timestamps send all new writes to the last shard. "
                "Hash sharding applies a hash to the key and spreads rows evenly, at the cost of turning range queries into scatter-gather queries across every shard. "
                "A lookup directory that maps keys to shards gives full control but is one more component to keep available.\n\n"
                "Even with good hashing, one key can be hot: a celebrity account or a viral item gets far more traffic than its shard can take. "
                "Remedies include caching that key aggressively, splitting it across several sub-keys such as item_42#0 to item_42#7 and combining results on read, "
                "or moving it to a dedicated shard. Choose the shard key from the queries you run most."
            )),
            dict(title='Indexes recap', text=(
                "An index is a separate structure, usually a B-tree, that keeps a column's values sorted with pointers to the rows. "
                "Without one, finding a row means scanning the table. With one, the database walks a shallow tree.\n\n"
                "B-tree nodes hold many keys each, so the tree is very flat. With about 100 keys per node, 100 million rows need only log base 100 of 10^8 = 4 levels, "
                "compared with roughly 27 levels for a binary tree. The top levels usually sit in memory, so a lookup costs very few disk reads.\n\n"
                "Indexes are not free. Every insert, update or delete must also update each index on the table, so heavy write tables should carry only the indexes their queries need. "
                "A composite index on (user_id, created_at) serves queries that filter on user_id, or on user_id and created_at, "
                "but generally cannot serve queries on created_at alone efficiently, because the index is sorted by user_id first. "
                "At scale, check slow queries with the database's query plan before reaching for sharding: a missing index is a far cheaper fix."
            )),
        ],
        keyPoints=[
            'Leader-follower replication scales reads, but every replica must still apply every write.',
            'Asynchronous replication causes lag; protect read-your-writes by reading recent writers from the leader.',
            'Sharding spreads writes and storage; hash sharding balances load, range sharding keeps ranges together.',
            'Hot keys need caching, key splitting or dedicated capacity.',
            'B-trees are flat, so indexed lookups touch few nodes; each index slows writes.',
        ],
        challenges=[
            dict(id='challenge-system-design-databases-at-scale-q1', kind='prediction', title='Sizing read replicas',
                 prompt="Each database node can process 5,000 queries/s. The workload is 10,000 reads/s and 1,500 writes/s. Writes go to the leader, reads go only to replicas, and every replica must also apply all 1,500 writes/s, each costing as much as one query. What is the minimum number of replicas?",
                 options=['2', '3', '4', '5'], answer=1,
                 explanation="Each replica has 5,000 − 1,500 = 3,500 queries/s left for reads, and 10,000 ÷ 3,500 ≈ 2.9, so 3 replicas. Two replicas comes from ignoring the write load on each replica and dividing 10,000 by 5,000.",
                 hint='Subtract the replicated writes from each replica before dividing up the reads.'),
            dict(id='challenge-system-design-databases-at-scale-q2', kind='prediction', title='The vanishing edit',
                 prompt="A user saves a profile change, which is written to the leader. The page reloads at once and reads from an asynchronous read replica. The old profile is shown. The leader and network are healthy. What is the cause?",
                 options=['The write was rejected by the leader', 'The replica had not yet applied the change because of replication lag', 'The browser cached the old page', 'The index on the profile table is missing'],
                 answer=1,
                 explanation="Asynchronous replicas apply writes after a delay, so a read immediately after a write can hit a replica that is still behind. The write was not rejected; it is on the leader and will appear on the replica shortly.",
                 hint='Compare where the write went with where the read came from.'),
            dict(id='challenge-system-design-databases-at-scale-q3', kind='prediction', title='Range query on hash shards',
                 prompt="Orders are hash-sharded by order_id across 16 shards, with no secondary index or routing table. A report needs all orders placed yesterday, filtered by a created_at column. How many shards must the query touch?",
                 options=['Exactly 1', 'About 2, the shards for yesterday', 'All 16'], answer=2,
                 explanation="Hashing order_id scatters orders without regard to date, so yesterday's orders can be on any shard and the query must ask all 16. The idea that one or two shards hold a given day applies to range sharding by date, not to hashing by ID.",
                 hint='Think about whether the shard key tells you anything about the date.'),
            dict(id='challenge-system-design-databases-at-scale-q4', kind='prediction', title='One overloaded shard',
                 prompt="Posts are sharded by author_id with a good hash. One author has tens of millions of followers, and their shard is overloaded while others are idle. Which change targets this problem directly?",
                 options=['Switch from hash sharding to range sharding by author_id', 'Double the number of shards', 'Split that author\'s key into several sub-keys or serve their posts from a cache', 'Add an index on author_id'],
                 answer=2,
                 explanation="The overload comes from one hot key, and all of its traffic still lands on one shard however many shards exist. Splitting the key or caching it spreads that one key's load. Doubling the shards only rebalances many keys, which were never the problem.",
                 hint='Count how many shards a single key can ever live on.'),
            dict(id='challenge-system-design-databases-at-scale-q5', kind='prediction', title='Depth of a B-tree',
                 prompt="In a B-tree index every internal node has exactly 200 children and every leaf holds exactly 200 keys. The index holds 8 million keys, all in the leaves. How many levels does the tree have, counting the root and the leaves?",
                 options=['3', '8', '23'], answer=0,
                 explanation="8,000,000 ÷ 200 = 40,000 leaves, 40,000 ÷ 200 = 200 internal nodes, and one root above them: three levels, since 200 × 200 × 200 = 8,000,000. 23 is close to log base 2 of 8 million, which is the depth of a binary tree, not a B-tree with 200 keys per node.",
                 hint='Multiply the fan-out by itself until you reach the number of keys.'),
        ],
    ),
    dict(
        id='guide-system-design-consistency-and-cap', kind='guide', track='system-design',
        title='Consistency, CAP and quorums', order=5,
        summary="CAP says a replicated system cut by a network partition must choose between linearizable answers and always answering, while PACELC adds the latency trade-off that applies even without partitions.",
        sections=[
            dict(title='CAP stated precisely', text=(
                "The CAP theorem talks about three properties of a replicated data store.\n\n"
                "Consistency here means linearizability: the system behaves as if there were a single copy of the data, "
                "so once a write completes, every later read, from any client and any node, returns that value or a newer one. "
                "This is much stronger than the C in ACID, which is about keeping invariants inside a transaction.\n\n"
                "Availability means every request received by a node that has not crashed gets a non-error response, without waiting forever.\n\n"
                "Partition tolerance means the system keeps operating even when the network drops or delays messages between nodes.\n\n"
                "The theorem: when a partition happens, a node that cannot reach the others must either refuse or delay some requests, giving up availability, "
                "or answer with data that may be out of date, giving up linearizability. "
                "Partitions are not optional in a real network, so the slogan 'pick two of three' is misleading. "
                "The real choice is what to give up during a partition. When the network is healthy, a system can provide both."
            )),
            dict(title='PACELC', text=(
                "CAP says nothing about normal operation, yet that is where systems spend most of their time. PACELC fills the gap. "
                "It reads: if there is a Partition, choose between Availability and Consistency; Else, choose between Latency and Consistency.\n\n"
                "The else half matters because keeping replicas in sync costs time even on a healthy network. "
                "If a write must be confirmed by replicas in another region, 80 ms away as a round trip, before it is acknowledged, every write pays at least those 80 ms. "
                "Acknowledging after one local copy is faster, but a read elsewhere may briefly see the old value.\n\n"
                "Systems are often described with labels such as PA/EL (stay available during partitions, favour low latency otherwise) "
                "or PC/EC (favour consistency in both cases). "
                "Many databases let you tune this per request, so treat the labels as a description of default behaviour rather than a fixed property. "
                "In an interview, saying which side you choose for each feature, and why, is more convincing than naming a category."
            )),
            dict(title='Strong versus eventual consistency', text=(
                "Strong consistency, in the linearizable sense, makes a distributed store look like one machine. "
                "It suits data where a stale read causes real harm: account balances, inventory reservations, unique usernames, leader election.\n\n"
                "Eventual consistency promises only that if writes stop, all replicas will converge to the same value at some point. "
                "In the meantime, reads may return older values, and two replicas may disagree. "
                "It suits data where a short delay is harmless: like counts, view counts, social feeds, product reviews.\n\n"
                "Between the two are useful middle guarantees. Read-your-writes ensures a user always sees their own updates. "
                "Monotonic reads ensure a user never sees data go backwards in time. Causal consistency ensures that if one write could have influenced another, "
                "everyone sees them in that order, so a reply never appears before the message it answers.\n\n"
                "A practical design often mixes them: strong consistency for the few operations that need it, "
                "and eventual consistency plus a session guarantee for everything else."
            )),
            dict(title='Quorum reads and writes', text=(
                "Leaderless replicated stores often use quorums. Each item is stored on N replicas. A write is acknowledged once W replicas confirm it, "
                "and a read asks R replicas and returns the newest version among their answers.\n\n"
                "If R + W > N, the set of replicas a read contacts must overlap with the set that acknowledged the latest write, "
                "so at least one replica in every read has that write. "
                "With N = 3, W = 2 and R = 2, 2 + 2 = 4 > 3. With N = 3, W = 1 and R = 1, a read can hit a replica that missed the write and return stale data.\n\n"
                "Quorums also set fault tolerance. With N = 5 and W = 3, writes still succeed with 2 replicas down; with R = 3, reads also survive 2 failures. "
                "Lowering W speeds up writes, and lowering R speeds up reads, at the cost of overlap.\n\n"
                "One caution: overlap alone does not make a system fully linearizable. Concurrent writes, failed partial writes and clock-based conflict resolution "
                "can still produce surprises, so real systems add version numbers, read repair or consensus on top."
            )),
        ],
        keyPoints=[
            "CAP's consistency is linearizability: every read sees the latest completed write, as if there were one copy.",
            'During a partition a node must choose between answering (availability) and staying linearizable.',
            'PACELC: with a Partition choose A or C; Else choose Latency or Consistency.',
            'Eventual consistency only promises convergence once writes stop.',
            'Quorums with R + W > N make every read overlap the latest acknowledged write; overlap alone is not linearizability.',
        ],
        challenges=[
            dict(id='challenge-system-design-consistency-and-cap-q1', kind='prediction', title="CAP's C",
                 prompt="In the CAP theorem, what does the C (consistency) property mean?",
                 options=['Transactions never violate database constraints', 'All replicas eventually hold the same data', 'Every read returns the result of the latest completed write, as if there were a single copy', 'Data is written to disk before acknowledging'],
                 answer=2,
                 explanation="CAP's consistency is linearizability: a single-copy illusion where a completed write is visible to every later read. Keeping constraints valid is the C in ACID, a different idea that is often confused with it.",
                 hint='CAP is about replicas and what readers see, not about transactions or disks.'),
            dict(id='challenge-system-design-consistency-and-cap-q2', kind='prediction', title='Picking a quorum',
                 prompt="A store keeps N = 5 replicas of each item. Which read and write quorum guarantees that every read overlaps the latest acknowledged write?",
                 options=['R = 2, W = 3', 'R = 3, W = 3', 'R = 1, W = 4', 'R = 2, W = 2'], answer=1,
                 explanation="Overlap needs R + W > N, so more than 5. Only R = 3, W = 3 gives 6. R = 2, W = 3 adds up to exactly 5, which allows a read set and a write set that share no replica.",
                 hint='Look for the read and write sets that can never be chosen without sharing a replica.'),
            dict(id='challenge-system-design-consistency-and-cap-q3', kind='prediction', title='Write fault tolerance',
                 prompt="A store keeps N = 5 replicas and requires W = 3 acknowledgements per write. Replicas fail by crashing. How many replicas can be down at the same time while writes still succeed?",
                 options=['1', '2', '3'], answer=1,
                 explanation="A write needs 3 live replicas out of 5, so up to 5 − 3 = 2 can be down. With 3 down only 2 remain, which is fewer than W.",
                 hint='Count how many live replicas a write needs.'),
            dict(id='challenge-system-design-consistency-and-cap-q4', kind='prediction', title='PACELC without a partition',
                 prompt="With the network healthy, a database acknowledges a write only after every replica, including ones in distant regions, has confirmed it. In PACELC terms, what is it choosing in the no-partition case?",
                 options=['Latency over consistency', 'Availability over consistency', 'Consistency over latency'], answer=2,
                 explanation="Waiting for every replica makes writes slower but keeps replicas in step, which is the EC choice: consistency over latency. Availability versus consistency is the choice PACELC describes during a partition, not when the network is healthy.",
                 hint='The E half of PACELC covers normal operation; ask what is being paid and what is gained.'),
            dict(id='challenge-system-design-consistency-and-cap-q5', kind='prediction', title='A CP node in a partition',
                 prompt="A system is designed to stay linearizable during partitions (it chooses C over A). A node is cut off from the majority of its peers and receives a read. How does it respond?",
                 options=['It returns an error or waits, rather than risk returning stale data', 'It returns its local copy immediately', 'It returns its local copy and repairs it later'],
                 answer=0,
                 explanation="An isolated node cannot know whether newer writes happened on the other side, so to stay linearizable it must refuse or delay the read. Returning the local copy immediately is the availability choice, which can return stale data.",
                 hint='Ask what the node can know about writes on the other side of the partition.'),
        ],
    ),
    dict(
        id='guide-system-design-queues-and-async', kind='guide', track='system-design',
        title='Queues and asynchronous processing', order=6,
        summary="Message queues and pub/sub let services hand off work without waiting, which needs idempotent consumers, back-pressure and a plan for messages that keep failing.",
        sections=[
            dict(title='Queues versus pub/sub', text=(
                "Asynchronous messaging lets a producer hand work to someone else and move on. "
                "A sign-up request can return in milliseconds while welcome emails and analytics happen in the background.\n\n"
                "In a message queue, each message is delivered to one consumer out of a group. Several workers pull from the same queue, "
                "and adding workers increases throughput because they share the messages. This is the work-queue model: resize images, send emails, process payments.\n\n"
                "In publish/subscribe, a message published to a topic is delivered to every subscriber. "
                "An OrderPlaced event can reach the inventory, email and analytics services, each getting its own copy, "
                "and the producer does not need to know who is listening. Adding a new subscriber needs no change to the producer.\n\n"
                "Many systems combine the two: each subscribing service gets its own copy of the stream and spreads it among its own workers. "
                "RabbitMQ, Amazon SQS and Kafka are common examples of messaging tools, with different models for storing and replaying messages."
            )),
            dict(title='At-least-once delivery and idempotency', text=(
                "Delivery guarantees describe what happens when something fails between receiving a message and confirming it. "
                "With at-most-once, the message is removed before processing, so a crash loses it. "
                "With at-least-once, the message is removed only after the consumer acknowledges it, so a crash causes redelivery and nothing is lost, but some messages are processed twice.\n\n"
                "At-least-once is the usual choice, which means consumers must be idempotent: processing the same message twice must have the same effect as processing it once. "
                "Picture a consumer that charges a card, then crashes before acknowledging. The message comes back, and without protection the customer is charged twice.\n\n"
                "Common techniques: give each message a unique ID and, when the work is a write to your own database, record processed IDs in the same transaction as that write, skipping any ID already seen; "
                "make operations naturally idempotent, such as 'set status to shipped' instead of 'add one to the count'; "
                "or, when the work is a call to another service such as a payment provider, pass the message ID as an idempotency key so that service ignores the repeat. "
                "Exactly-once delivery is not something the network can promise; exactly-once effects (often called effectively-once) come from at-least-once delivery plus idempotent processing."
            )),
            dict(title='Back-pressure and backlog', text=(
                "A queue absorbs bursts, but only if consumers eventually catch up. Size consumers for the sustained rate: "
                "if producers send 1,200 messages per second and one worker handles 150, you need 1,200 ÷ 150 = 8 workers just to keep up.\n\n"
                "When producers outrun consumers, the backlog grows by the difference. Producers at 1,200 per second against consumers at 1,000 per second "
                "add 200 messages every second; after 10 minutes, 200 × 600 = 120,000 messages are waiting. "
                "If producers then drop to 600 per second, the backlog shrinks at 1,000 − 600 = 400 per second and takes 120,000 ÷ 400 = 300 seconds, five minutes, to clear.\n\n"
                "An unbounded backlog eventually runs out of memory or disk, and messages grow so old they are useless. "
                "Back-pressure pushes the problem back to the source: bound the queue and make producers slow down, "
                "return a 'try later' error, or drop low-value messages. "
                "Watch queue depth and the age of the oldest message, and scale consumers automatically on those signals."
            )),
            dict(title='Retries and dead-letter queues', text=(
                "Some messages fail for temporary reasons, such as a timeout from a downstream service, and succeed on retry. "
                "Retry with exponential backoff so a struggling dependency gets breathing room: waits of 1, 2, 4 and 8 seconds before the second to fifth attempts add up to 15 seconds.\n\n"
                "Other messages will never succeed: a malformed payload, or a reference to a record that was deleted. "
                "These poison messages can block a queue, or burn resources forever, if they are retried without limit.\n\n"
                "A dead-letter queue (DLQ) solves this. After a set number of failed attempts, the message moves to a separate queue instead of being retried again. "
                "Normal traffic keeps flowing, and the failed message is kept rather than discarded, so an engineer can inspect it, fix the bug, and replay it.\n\n"
                "Alert on DLQ growth; a silent DLQ is just data loss with extra steps. "
                "Keep the original message, the error and the attempt count together so that diagnosing the failure later does not require guesswork."
            )),
        ],
        keyPoints=[
            'A queue gives each message to one consumer; pub/sub gives every subscriber its own copy.',
            'At-least-once delivery can redeliver, so consumers must be idempotent.',
            'Backlog grows at producer rate minus consumer rate; size consumers for the sustained load.',
            'Back-pressure bounds the queue and slows or rejects producers instead of growing forever.',
            'Dead-letter queues park messages that keep failing so they stop blocking normal work.',
        ],
        challenges=[
            dict(id='challenge-system-design-queues-and-async-q1', kind='prediction', title='Fan-out to services',
                 prompt="When an order is placed, the inventory, email and analytics services must each receive the event. Which messaging model fits this requirement directly?",
                 options=['A single work queue shared by the three services', 'Publish/subscribe with one subscription per service', 'A direct synchronous call to one service, which forwards to the others'], answer=1,
                 explanation="Pub/sub delivers a copy to every subscriber, so each service gets the event. A single shared work queue delivers each message to only one consumer, so each order would reach just one of the three services.",
                 hint='Ask how many receivers should get each individual message.'),
            dict(id='challenge-system-design-queues-and-async-q2', kind='prediction', title='The double charge',
                 prompt="A consumer uses at-least-once delivery. It charges a card through a payment provider that supports idempotency keys, then crashes before acknowledging, so the message is redelivered. Which change prevents a second charge without risking a lost payment?",
                 options=['Acknowledge the message before charging the card', 'Increase the queue retention period', 'Add more consumers', 'Send the message ID as the idempotency key on the charge'],
                 answer=3,
                 explanation="Using the message ID as the idempotency key makes the charge idempotent: the redelivered message reaches the provider with the same key, and the provider returns the first result instead of charging again. Acknowledging before charging avoids duplicates only by switching to at-most-once, where a crash at the wrong moment loses the payment instead.",
                 hint='You want redelivery to stay, but you want its second arrival to do nothing.'),
            dict(id='challenge-system-design-queues-and-async-q3', kind='prediction', title='Growing backlog',
                 prompt="Producers send 900 messages/s and consumers process 750 messages/s, starting from an empty queue. Assuming both rates hold steady, how many messages are waiting after 20 minutes?",
                 options=['15,000', '180,000', '1,080,000', '900,000'], answer=1,
                 explanation="The backlog grows by 900 − 750 = 150 messages each second, and 20 minutes is 1,200 seconds, so 150 × 1,200 = 180,000. 1,080,000 is the total number of messages produced, ignoring that consumers removed most of them.",
                 hint='Only the gap between the two rates accumulates.'),
            dict(id='challenge-system-design-queues-and-async-q4', kind='prediction', title='How many workers',
                 prompt="A queue receives a steady 2,400 messages/s. One worker processes 180 messages/s and workers scale linearly. What is the minimum number of workers that keeps the queue from growing?",
                 options=['14', '13', '12', '24'], answer=0,
                 explanation="2,400 ÷ 180 ≈ 13.3, so 13 workers handle only 2,340 per second and the queue still grows; 14 is the minimum. Rounding down to 13 is the usual mistake.",
                 hint='A fractional worker does not exist, so think about which way to round.'),
            dict(id='challenge-system-design-queues-and-async-q5', kind='prediction', title='The poison message',
                 prompt="One message has a malformed payload and fails every time it is processed. The queue retries failed messages forever. What does a dead-letter queue change?",
                 options=['It fixes the payload automatically', 'It deletes the message after the first failure', 'After a limited number of attempts it moves the message aside, keeping it for inspection'],
                 answer=2,
                 explanation="A dead-letter queue caps the retries and parks the message somewhere else, so normal traffic continues and the message can be examined and replayed later. It does not delete it; keeping the failed message is the point.",
                 hint='Think about both the queue and the engineer who will investigate later.'),
        ],
    ),
    dict(
        id='guide-system-design-rate-limiting-and-apis', kind='guide', track='system-design',
        title='Rate limiting and API design', order=7,
        summary="Rate limiters cap how fast clients can call an API, and well-designed APIs add stable pagination, safe retries through idempotency keys, and versioning.",
        sections=[
            dict(title='Token bucket and leaky bucket', text=(
                "A token bucket holds up to C tokens and is refilled at a steady rate r. Each request takes one token; if the bucket is empty, the request is rejected, "
                "usually with HTTP 429 Too Many Requests and a Retry-After header.\n\n"
                "The key property is that it allows bursts. With C = 10 and r = 2 per second, a client that has been idle has a full bucket and can send 10 requests at once. "
                "After that it is held to 2 per second. Over the first 5 seconds starting from full, it can send at most 10 + 2 × 5 = 20 requests. "
                "This suits real users, whose traffic is naturally bursty, while still capping the long-run rate.\n\n"
                "A leaky bucket, in its queue form, puts incoming requests into a fixed-size queue that drains at a constant rate; requests that find the queue full are dropped. "
                "Output is perfectly smooth, which protects a downstream service that cannot handle spikes, but a burst is delayed or dropped rather than served quickly. "
                "Choose token bucket to allow bursts, leaky bucket to smooth them."
            )),
            dict(title='Fixed and sliding windows', text=(
                "A fixed window counter counts requests per client in calendar-aligned windows, such as each clock minute, and rejects requests once the count passes the limit. "
                "It is cheap: one counter per client per window. "
                "Its flaw is the boundary. With a limit of 100 per minute, a client can send 100 requests at 12:00:59 and another 100 at 12:01:00, "
                "200 requests in about two seconds, all allowed.\n\n"
                "A sliding window log stores the timestamp of every request and counts those within the last 60 seconds. It is exact, but memory grows with traffic.\n\n"
                "A sliding window counter approximates it with just two counters. It weights the previous window by how much of it still overlaps the last 60 seconds. "
                "If the previous minute had 80 requests, the current minute has 30 so far, and we are 25% of the way into the current minute, "
                "the estimate is 80 × 0.75 + 30 = 90, under a limit of 100, so the request is allowed. "
                "The estimate assumes the previous minute's requests were spread evenly, so it can be slightly off, which is usually acceptable. "
                "In a system with many servers, keep the counters in a shared store such as Redis, and update them atomically."
            )),
            dict(title='Pagination', text=(
                "List endpoints should never return an unbounded result. Pagination returns a page at a time.\n\n"
                "Offset pagination uses parameters such as ?limit=20&offset=40. It is easy to build and lets users jump to page 50. "
                "It has two problems. Deep pages are slow, because the database still walks past all the skipped rows: offset 1,000,000 reads a million rows to discard them. "
                "And it is unstable under writes: in a newest-first list, if one item is inserted at the top between page 1 and page 2, every item shifts down by one, "
                "so the last item of page 1 appears again at the top of page 2.\n\n"
                "Cursor pagination (also called keyset pagination) returns an opaque cursor that encodes where the page ended, for example the created_at and id of the last item. "
                "The next request asks for items after that position, which an index serves directly. "
                "Pages stay correct as items are added, and deep pages are as fast as the first. "
                "The trade-off is that users cannot jump to an arbitrary page number, which feeds and timelines rarely need."
            )),
            dict(title='Idempotency keys and versioning', text=(
                "Networks fail in an awkward way: a client can send a request, the server can process it, and the response can be lost. "
                "Retrying a GET is harmless, but retrying a POST that creates a payment could charge twice.\n\n"
                "An idempotency key fixes this. The client generates a unique key per logical operation and sends it in a header with the request. "
                "The server stores the key with the result. If the same key arrives again, the server returns the stored response instead of performing the operation again. "
                "Keys are kept for a limited time, such as a day, and a reused key with a different request body should be rejected as an error.\n\n"
                "Versioning lets an API evolve without breaking existing clients. Additive changes, such as a new optional field, are usually safe. "
                "Removing or renaming a field, or changing its meaning, is breaking and needs a new version, "
                "commonly in the path (/v2/orders) or in a header. "
                "Run old and new versions side by side, announce a deprecation date, and measure who still calls the old version before turning it off."
            )),
        ],
        keyPoints=[
            'Token bucket allows bursts up to its capacity while capping the long-run rate.',
            'Leaky bucket smooths output to a constant rate; bursts are queued or dropped.',
            'Fixed windows allow up to double the limit across a boundary; sliding windows fix this.',
            'Cursor pagination stays fast and stable under inserts; offset pagination does not.',
            'Idempotency keys make retried POSTs safe; version breaking changes, not additive ones.',
        ],
        challenges=[
            dict(id='challenge-system-design-rate-limiting-and-apis-q1', kind='prediction', title='Token bucket burst',
                 prompt="A token bucket has capacity 20 and refills continuously at 5 tokens per second. It is full at t = 0, and the client sends requests as fast as it is allowed. How many requests can succeed between t = 0 and t = 4 seconds?",
                 options=['20', '25', '40', '100'], answer=2,
                 explanation="The full bucket allows 20 requests immediately, and refills add 5 × 4 = 20 more over the 4 seconds, for 40 in total. 20 ignores the refill, treating the bucket as a one-time allowance.",
                 hint='Add what is already in the bucket to what flows in during the interval.'),
            dict(id='challenge-system-design-rate-limiting-and-apis-q2', kind='prediction', title='Fixed window boundary',
                 prompt="A fixed window limiter allows 50 requests per client per calendar minute. What is the largest number of requests a client can get accepted within a 2-second span?",
                 options=['50', '100', '25', '2'], answer=1,
                 explanation="The client sends 50 in the last second of one minute and 50 in the first second of the next; both windows are within their limit, so 100 are accepted in about 2 seconds. 50 would be the cap under an exact sliding window log.",
                 hint='Place the 2-second span so that it straddles two windows.'),
            dict(id='challenge-system-design-rate-limiting-and-apis-q3', kind='prediction', title='Sliding window estimate',
                 prompt="A sliding window counter limits clients to 100 requests per minute. The previous minute had 60 requests, the current minute has 40 so far, and we are exactly halfway through the current minute. What is the estimated count for the last 60 seconds?",
                 options=['40', '70', '100'], answer=1,
                 explanation="Half of the previous window still overlaps the last 60 seconds, so the estimate is 60 × 0.5 + 40 = 70. 100 comes from adding both windows in full, which overcounts requests from more than a minute ago.",
                 hint='Weight the previous window by how much of it is still inside the last minute.'),
            dict(id='challenge-system-design-rate-limiting-and-apis-q4', kind='prediction', title='Offset pages under inserts',
                 prompt="A feed is sorted newest first and paginated with limit=10 and offset. A client loads page 1 (offset 0). Before it loads page 2 (offset 10), exactly one new item is added at the top. Nothing is deleted. What does the client see on page 2?",
                 options=['One item it already saw on page 1 appears again', 'One item is skipped and never shown', 'Exactly the items it would have seen without the insert'],
                 answer=0,
                 explanation="The insert pushes every item down one place, so the item that was 10th is now 11th and opens page 2, a duplicate. A skipped item happens in the opposite case, when an item above the cut is deleted.",
                 hint='Track where the old 10th item ends up after everything shifts.'),
            dict(id='challenge-system-design-rate-limiting-and-apis-q5', kind='prediction', title='Retrying with an idempotency key',
                 prompt="A client sends POST /payments with an idempotency key. The server charges the card and stores the key with the response, but the response is lost. The client retries with the same key and identical body. What should the server do?",
                 options=['Charge the card again and return a new response', 'Reject the request with an error because the key was used', 'Return a rate-limit error', 'Return the stored response without charging again'],
                 answer=3,
                 explanation="The key identifies the same logical operation, so the server replays the stored result and the client learns that the payment succeeded. Rejecting a matching retry with an error defeats the purpose; errors are for a reused key with a different body.",
                 hint='The client still needs to find out how the first attempt went.'),
        ],
    ),
    dict(
        id='guide-system-design-case-study-url-shortener', kind='guide', track='system-design',
        title='Case study: URL shortener', order=8,
        summary="An end-to-end design of a URL shortener, from requirements and estimates through ID generation, storage and caching to the choice of redirect status code.",
        sections=[
            dict(title='Requirements and estimates', text=(
                "Start by pinning down scope. Functional requirements: given a long URL, return a short one; visiting the short URL redirects to the long one; "
                "optionally, custom aliases, expiry dates and click analytics. "
                "Non-functional requirements: redirects must be fast and highly available, short codes must not collide, and codes should not be trivially guessable if links can be private.\n\n"
                "Now the numbers. Assume 40 million new short URLs per month. A 30-day month has 2,592,000 seconds, so writes average 40,000,000 ÷ 2,592,000 ≈ 15 per second. "
                "Shorteners are read-heavy; assume 200 redirects per creation, about 3,100 redirects per second on average, with peaks a few times higher.\n\n"
                "Storage: keeping links for 6 years gives 40 million × 72 months ≈ 2.9 billion records. At roughly 400 bytes per record (code, long URL, owner, timestamps), "
                "that is 2.9 × 10^9 × 400 B ≈ 1.2 TB. "
                "The conclusion: writes are light, the data fits comfortably on a few machines, and the real job is serving redirects quickly."
            )),
            dict(title='Generating short codes', text=(
                "Codes use base62: the characters 0-9, a-z and A-Z. Six characters give 62^6 ≈ 56.8 billion codes, and seven give about 3.5 trillion. "
                "Our 2.9 billion records fit within six characters with room to spare.\n\n"
                "Counter approach: give every URL a unique integer and convert it to base62, much like converting to binary but dividing by 62. "
                "With the alphabet ordered 0-9, a-z, A-Z, the number 1,000,000 becomes 4c92. "
                "A single counter is a bottleneck, so each application server leases a block of IDs, say 1,000 at a time, from a coordinating store and hands them out locally. "
                "There are no collisions, but codes are sequential and easy to enumerate; scrambling the number with a reversible permutation before encoding hides the order.\n\n"
                "Hash approach: hash the long URL and keep the first 7 base62 characters. No coordination is needed, but at this scale collisions are practically certain. "
                "With 2.9 billion codes in a space of 3.5 trillion, the birthday estimate n² ÷ 2M predicts about 1.2 million colliding pairs, "
                "so every insert must check for an existing code and retry with a tweaked input."
            )),
            dict(title='Storage and caching', text=(
                "The core table is simple: short code as the primary key, plus the long URL, creation time, expiry and owner. "
                "Access is almost entirely by exact key, with no joins, so a key-value store or a relational database with a primary key index both work. "
                "At about 1.2 TB, a relational database with read replicas is enough for years; if growth demands it, hash-shard by short code, which spreads keys evenly.\n\n"
                "Redirect traffic is highly skewed: a small share of links receives most clicks. Put a cache such as Redis in front of the database using cache-aside. "
                "Caching 10 million hot mappings at about 400 bytes each needs around 4 GB of memory, easily held on one node, with replicas for availability. "
                "With a high hit rate, the database sees only a small fraction of the 3,100 redirects per second.\n\n"
                "Mappings rarely change, so long TTLs are safe. When a link is deleted or expires, delete its cache entry too, "
                "and cache 'not found' results briefly so repeated lookups for invalid codes do not all reach the database."
            )),
            dict(title='Redirects: 301 versus 302', text=(
                "The redirect itself is an HTTP response with a Location header. The status code choice has real consequences.\n\n"
                "301 Moved Permanently tells the client the move is permanent. Browsers cache a 301 by default, unless cache headers on the response say otherwise, so after the first visit, "
                "later clicks on the same short link in that browser may go straight to the long URL without contacting your service. "
                "That cuts load, but you lose click counts for those visits, and you cannot reliably change or disable the link for users who have cached it.\n\n"
                "302 Found and 307 Temporary Redirect mark the move as temporary, so browsers cache them only if the response explicitly allows it, and by default every click passes through your service. "
                "That is what analytics, link editing and expiry need. 307 also guarantees the browser keeps the request method, which matters little for links clicked as GETs.\n\n"
                "A design that needs accurate click counts or editable links is therefore better served by 302 or 307, accepting the extra traffic and keeping redirects cheap with server-side caching. "
                "A service that values lower load over exact counts may reasonably choose 301 instead; state the trade-off either way. "
                "Record clicks asynchronously: push an event to a queue and return the redirect at once, so analytics never slows the user down."
            )),
        ],
        keyPoints=[
            'Estimate first: about 15 writes/s and 3,100 reads/s make this a read-heavy, cache-friendly system.',
            'Base62 with 6 characters gives about 56.8 billion codes; 7 characters about 3.5 trillion.',
            'Counters avoid collisions but are guessable; truncated hashes need collision checks.',
            'Cache hot mappings and invalidate on delete or expiry; also cache misses briefly.',
            'Without cache headers browsers cache 301 but not 302 or 307, so analytics and editable links favour 302 or 307.',
        ],
        challenges=[
            dict(id='challenge-system-design-case-study-url-shortener-q1', kind='prediction', title='Code length',
                 prompt="Short codes use base62 (0-9, a-z, A-Z) and all codes have the same length. The service must support 100 billion distinct codes. What is the shortest length that works?",
                 options=['6', '7', '8', '11'], answer=1,
                 explanation="62^6 ≈ 56.8 billion is not enough, while 62^7 ≈ 3.5 trillion is, so 7 characters. 6 looks close but falls short by about 43 billion codes.",
                 hint='Compute 62 raised to successive powers and compare with the target.'),
            dict(id='challenge-system-design-case-study-url-shortener-q2', kind='prediction', title='Write rate',
                 prompt="A shortener creates 30 million new links per 30-day month, spread evenly. Roughly what is the average write rate?",
                 options=['About 1.2 per second', 'About 120 per second', 'About 1,200 per second', 'About 12 per second'], answer=3,
                 explanation="A 30-day month has 2,592,000 seconds, and 30,000,000 ÷ 2,592,000 ≈ 11.6, about 12 per second. 120 per second would mean about 311 million links a month, ten times the stated volume.",
                 hint='Convert the month to seconds before dividing.'),
            dict(id='challenge-system-design-case-study-url-shortener-q3', kind='prediction', title='Status code for analytics',
                 prompt="The product must count every click on a short link and let owners change the destination later. No special cache headers are added to redirect responses. Which status code should redirects use?",
                 options=['301 Moved Permanently', '302 Found', '200 OK with the long URL in the body'], answer=1,
                 explanation="A 302 is not cached by browsers by default, so every click comes back to the service, where it can be counted and the current destination looked up. A 301 is cached by default, so repeat clicks can skip the service entirely and go uncounted.",
                 hint='Ask which response the browser will remember and reuse without asking again.'),
            dict(id='challenge-system-design-case-study-url-shortener-q4', kind='prediction', title='Base62 encoding',
                 prompt="Short codes are the base62 form of an integer ID, using the digits 0-9, then a-z, then A-Z, with no padding. What is the code for ID 3,844?",
                 options=['100', 'zz', 'ZZ', '1000'], answer=0,
                 explanation="3,844 = 62 × 62, which is written 100 in base 62, just as 100 in base 10 is 10 × 10. ZZ is one less, 3,843, the largest two-character code.",
                 hint='List the place values of a base-62 number (1, 62, 62 × 62, ...) and see how 3,844 splits across them.'),
            dict(id='challenge-system-design-case-study-url-shortener-q5', kind='prediction', title='Weakness of a plain counter',
                 prompt="Codes are created by base62-encoding a global counter that increases by 1 for each new link, with no scrambling. Which problem does this introduce?",
                 options=['Two links can receive the same code', 'Codes become longer than with hashing', 'Anyone can enumerate other links by trying neighbouring codes'], answer=2,
                 explanation="Sequential IDs give sequential codes, so trying the next or previous code reveals other people's links. Collisions are the weakness of truncated hashes; a counter hands each number out once, so it never repeats a code.",
                 hint='Imagine you just made a link and want to find one created a moment earlier.'),
        ],
    ),
]

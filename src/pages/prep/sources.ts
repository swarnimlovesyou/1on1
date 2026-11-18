/** Free (or clearly marked) references for each Prep subject, checked to resolve. Links only; no text is copied. */
export type Source = { title: string; by: string; url: string; note: string; paid?: boolean };

const BY_SUBJECT: Record<string, Source[]> = {
  "Operating systems": [
    { title: "Operating Systems: Three Easy Pieces", by: "Remzi and Andrea Arpaci-Dusseau", url: "https://pages.cs.wisc.edu/~remzi/OSTEP/", note: "Free textbook; the chapters on scheduling, paging, locks and file systems match these guides." },
    { title: "MIT 6.1810 Operating System Engineering", by: "MIT PDOS", url: "https://pdos.csail.mit.edu/6.1810/", note: "Lectures and labs on a small real kernel, for when you want to see it built." },
  ],
  DBMS: [
    { title: "CMU 15-445 Database Systems", by: "Carnegie Mellon University", url: "https://15445.courses.cs.cmu.edu/", note: "Free lectures on storage, indexing, transactions and concurrency control." },
    { title: "Database System Concepts (slides)", by: "Silberschatz, Korth and Sudarshan", url: "https://www.db-book.com/", note: "The standard university text; the slides are free, the book is paid." },
    { title: "Database normalization", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Database_normalization", note: "Worked examples of each normal form." },
  ],
  SQL: [
    { title: "PostgreSQL tutorial", by: "The PostgreSQL Global Development Group", url: "https://www.postgresql.org/docs/current/tutorial.html", note: "Official, short, and covers joins, aggregates and window functions." },
    { title: "SQLBolt", by: "SQLBolt", url: "https://sqlbolt.com/", note: "Interactive exercises in the browser." },
    { title: "Use The Index, Luke", by: "Markus Winand", url: "https://use-the-index-luke.com/", note: "How indexes and query plans really behave, across databases." },
  ],
  "Computer networks": [
    { title: "Computer Networks: A Systems Approach", by: "Peterson and Davie", url: "https://book.systemsapproach.org/", note: "Free online textbook covering every layer." },
    { title: "Beej's Guide to Network Programming", by: "Brian Hall", url: "https://beej.us/guide/bgnet/", note: "TCP and UDP sockets in practice." },
    { title: "An overview of HTTP", by: "MDN Web Docs", url: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview", note: "Requests, responses, headers and caching." },
  ],
  OOP: [
    { title: "Object-oriented programming concepts", by: "Oracle Java Tutorials", url: "https://docs.oracle.com/javase/tutorial/java/concepts/", note: "Objects, classes, inheritance and interfaces in Java." },
    { title: "Design patterns", by: "Refactoring.Guru", url: "https://refactoring.guru/design-patterns", note: "Patterns with diagrams and code; useful after SOLID." },
    { title: "SOLID", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/SOLID", note: "The five principles and where they came from." },
  ],
  "system-design": [
    { title: "The System Design Primer", by: "Donne Martin", url: "https://github.com/donnemartin/system-design-primer", note: "Free, broad, with practice questions." },
    { title: "The Amazon Builders' Library", by: "Amazon Web Services", url: "https://aws.amazon.com/builders-library/", note: "Engineers on timeouts, retries, caching and load shedding in production." },
    { title: "Site Reliability Engineering", by: "Google", url: "https://sre.google/sre-book/table-of-contents/", note: "Free book on running large systems; see load balancing and overload." },
    { title: "Designing Data-Intensive Applications", by: "Martin Kleppmann", url: "https://dataintensive.net/", note: "The deepest single book on replication, partitioning and consistency.", paid: true },
  ],
  aptitude: [
    { title: "Prealgebra 2e", by: "OpenStax", url: "https://openstax.org/details/books/prealgebra-2e", note: "Free textbook: ratios, percents, averages and divisibility." },
    { title: "Contemporary Mathematics", by: "OpenStax", url: "https://openstax.org/details/books/contemporary-mathematics", note: "Free textbook; its finance chapter covers simple and compound interest." },
    { title: "Pre-algebra", by: "Khan Academy", url: "https://www.khanacademy.org/math/pre-algebra", note: "Short videos and practice for the basics." },
  ],
  reasoning: [
    { title: "Introduction to Logic", by: "Stanford University", url: "http://intrologic.stanford.edu/", note: "Free course on formal reasoning, behind syllogisms." },
    { title: "The On-Line Encyclopedia of Integer Sequences", by: "OEIS Foundation", url: "https://oeis.org/", note: "Look up any number series to see the rule behind it." },
    { title: "Syllogism", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Syllogism", note: "The valid forms and the common traps." },
  ],
  puzzles: [
    { title: "Mathematics for Computer Science", by: "MIT OpenCourseWare", url: "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/", note: "Counting, pigeonhole, invariants and probability: the tools behind most puzzles." },
    { title: "Project Euler", by: "Project Euler", url: "https://projecteuler.net/", note: "Mathematical puzzles to solve with a little code." },
  ],
};

const BY_GUIDE: Record<string, Source[]> = {
  "guide-cs-fundamentals-sql-window-functions": [{ title: "Window functions tutorial", by: "PostgreSQL docs", url: "https://www.postgresql.org/docs/current/tutorial-window.html", note: "The official walkthrough." }],
  "guide-cs-fundamentals-sql-indexes-and-query-plans": [{ title: "Using EXPLAIN", by: "PostgreSQL docs", url: "https://www.postgresql.org/docs/current/using-explain.html", note: "How to read a query plan." }],
  "guide-cs-fundamentals-cn-tcp-vs-udp": [{ title: "RFC 9293: Transmission Control Protocol", by: "IETF", url: "https://www.rfc-editor.org/rfc/rfc9293", note: "The current TCP standard." }],
  "guide-cs-fundamentals-cn-dns-http": [
    { title: "RFC 9110: HTTP Semantics", by: "IETF", url: "https://www.rfc-editor.org/rfc/rfc9110", note: "Methods, status codes and caching, as standardised." },
    { title: "DNS", by: "MDN Web Docs", url: "https://developer.mozilla.org/en-US/docs/Glossary/DNS", note: "A short definition with links onward." },
  ],
  "guide-cs-fundamentals-cn-ip-subnetting": [{ title: "Subnetwork", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Subnetwork", note: "CIDR and subnet masks with examples." }],
  "guide-cs-fundamentals-cn-routing-basics": [{ title: "What is routing?", by: "Cloudflare Learning Center", url: "https://www.cloudflare.com/learning/network-layer/what-is-routing/", note: "Routing tables and protocols, plainly." }],
  "guide-cs-fundamentals-cn-osi-tcpip-layers": [{ title: "The OSI model", by: "Cloudflare Learning Center", url: "https://www.cloudflare.com/learning/ddos/glossary/open-systems-interconnection-model-osi/", note: "Each layer with an example." }],
  "guide-cs-fundamentals-cn-network-security": [{ title: "OWASP Top Ten", by: "OWASP", url: "https://owasp.org/www-project-top-ten/", note: "The most common web security risks." }],
  "guide-system-design-consistency-and-cap": [{ title: "CAP theorem", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/CAP_theorem", note: "The statement and its limits." }],
  "guide-system-design-rate-limiting-and-apis": [{ title: "Token bucket", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Token_bucket", note: "The algorithm behind most rate limiters." }],
  "guide-aptitude-interest": [{ title: "Compound interest", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Compound_interest", note: "Formulas and worked examples." }],
  "guide-puzzles-shared-birthday": [{ title: "Birthday problem", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Birthday_problem", note: "The full calculation." }],
  "guide-puzzles-bridge-and-torch": [{ title: "Bridge and torch problem", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Bridge_and_torch_problem", note: "The general solution." }],
  "guide-puzzles-water-jugs": [{ title: "Water pouring puzzle", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Water_pouring_puzzle", note: "Why it works when the gcd divides the target." }],
  "guide-puzzles-trimmed-board": [{ title: "Mutilated chessboard problem", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Mutilated_chessboard_problem", note: "The colouring argument." }],
  "guide-puzzles-pirate-vote": [{ title: "Pirate game", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Pirate_game", note: "Backward induction, step by step." }],
  "guide-puzzles-hats-in-a-line": [{ title: "Prisoners and hats puzzle", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Prisoners_and_hats_puzzle", note: "Variants and their parity strategies." }],
  "guide-puzzles-nine-coins": [{ title: "Balance puzzle", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Balance_puzzle", note: "Why each weighing splits into three." }],
  "guide-puzzles-clock-angle": [{ title: "Clock angle problem", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Clock_angle_problem", note: "The formula and its derivation." }],
  "guide-puzzles-handshakes": [{ title: "Handshaking lemma", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Handshaking_lemma", note: "The graph theory behind it." }],
  "guide-puzzles-two-eggs": [{ title: "Dynamic programming", by: "Wikipedia", url: "https://en.wikipedia.org/wiki/Dynamic_programming", note: "The egg-drop problem is a classic example." }],
};

/** References for one subject (CS fundamentals) or track (the rest). */
export function subjectSources(track: string, subject?: string): Source[] {
  return BY_SUBJECT[subject ?? track] ?? [];
}

/** References for one guide: its own first, then its subject's. */
export function guideSources(id: string, track: string, subject?: string): Source[] {
  return [...(BY_GUIDE[id] ?? []), ...subjectSources(track, subject)];
}

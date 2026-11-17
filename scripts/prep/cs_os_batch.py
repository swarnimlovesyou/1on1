"""Operating systems guides for the CS fundamentals track (orders 1-6)."""

SUBJECT = 'Operating systems'
TRACK = 'cs-fundamentals'

GUIDES = [
    dict(
        id='guide-cs-fundamentals-os-processes-threads', kind='guide', track=TRACK, subject=SUBJECT,
        title='Processes and threads', order=1,
        summary="A process is a running program with its own address space, while threads are lighter units of execution that share one process's memory.",
        sections=[
            dict(title='What a process really is', text=(
                "A program is just a file on disk. It becomes a process when the operating system loads it and starts running it. "
                "Each process gets its own private address space, which holds the code, global data, a heap for dynamic allocations and a stack for function calls. "
                "It also owns resources such as open files and sockets.\n\n"
                "The kernel tracks every process in a process control block, or PCB. The PCB stores the process ID, the current state, the saved CPU registers "
                "including the program counter, scheduling details such as priority, memory mapping information and the list of open files. "
                "When you hear that the OS paused a process and resumed it later, the PCB is where everything needed to resume was kept.\n\n"
                "Because each process has a separate address space, one process cannot read or corrupt another's memory by accident. "
                "That isolation is the main reason a crash in your browser tab does not take down your text editor."
            )),
            dict(title='Process states and context switches', text=(
                "A process moves through a small set of states. It starts as new, becomes ready once it can run, and becomes running when the scheduler gives it a CPU. "
                "If it asks for something slow, such as reading from disk, it moves to waiting (also called blocked). When the I/O finishes it goes back to ready, not straight to running. "
                "If the timer interrupt fires while it is running, it is preempted and also returns to ready. When it finishes it becomes terminated.\n\n"
                "Switching the CPU from one process to another is a context switch. The kernel saves the outgoing process's registers into its PCB, "
                "loads the incoming process's registers, and switches the memory mapping. This is pure overhead: no user work happens during it, "
                "and caches and the TLB lose much of their useful contents, so the new process starts slower. That is why switching too often hurts throughput."
            )),
            dict(title='Creating processes with fork', text=(
                "On Unix-like systems a new process is created with fork. The child is a near copy of the parent, and both continue from the line after the fork call. "
                "In code, the usual way to tell them apart is the return value: fork returns 0 in the child and the child's PID in the parent. A typical pattern is fork followed by exec in the child, "
                "which replaces the child's program with a new one.\n\n"
                "Counting is a common interview question. Each fork doubles the number of processes executing the code after it. "
                "If a program calls fork three times in a row, you end up with 2 times 2 times 2, which is 8 processes, the original included.\n\n"
                "Two edge cases matter. A zombie is a child that has exited but whose parent has not yet called wait to collect its exit status, so its PCB entry lingers. "
                "An orphan is a child whose parent exited first; it is adopted by init (PID 1) or by a designated subreaper process, which reaps it later."
            )),
            dict(title='Threads and what they share', text=(
                "A thread is a single sequence of execution inside a process. A process can have many threads, and they all share the same code, global data, heap and open files. "
                "Each thread has its own stack, its own register set and its own program counter, because each one is at a different point in the code.\n\n"
                "Sharing memory makes threads cheap to create and fast to switch between, since there is no address space change. "
                "It also makes communication easy: one thread writes to a shared object and another reads it. The cost is safety. "
                "Two threads touching the same data without coordination can produce wrong results, and a bug in one thread can crash the whole process.\n\n"
                "Threads can be managed in user space by a library or directly by the kernel. Kernel threads can run truly in parallel on multiple cores and one blocking does not stall the others. "
                "Pure user-level threads switch faster but if one makes a blocking system call, the whole process can block."
            )),
            dict(title='Choosing between processes and threads', text=(
                "Use separate processes when you want isolation. A web browser that runs each site in its own process limits the damage a crashing or malicious page can do. "
                "Processes talk to each other through inter-process communication such as pipes, message queues, sockets or explicitly shared memory, all of which cost more than a plain memory write.\n\n"
                "Use threads when tasks need to share a lot of data and you can manage the synchronization. A server handling many requests against the same in-memory cache is a natural fit.\n\n"
                "A clean way to say it in an interview: a process is the unit of resource ownership, and a thread is the unit of scheduling. "
                "The OS gives memory and files to processes, and it gives CPU time to threads."
            )),
        ],
        keyPoints=[
            'A process has its own address space; threads in a process share code, data, heap and files.',
            'Each thread keeps its own stack, registers and program counter.',
            'The PCB stores everything the kernel needs to pause and resume a process.',
            'After I/O completes, a waiting process goes to ready, not directly to running.',
            'fork returns 0 in the child and the child PID in the parent; n forks in a row give 2^n processes.',
            'Context switches are overhead, and process switches cost more than thread switches.',
        ],
        challenges=[
            dict(id='challenge-os-processes-threads-q1', kind='prediction', title='Counting forks',
                 prompt='A program runs fork(); fork(); printf("hi"); with no error checks. How many times is "hi" printed?',
                 options=['2', '3', '4', '6'], answer=2,
                 explanation="The first fork turns one process into two. Both run the second fork, so there are four processes, and each prints once, giving 4. Answer 2 forgets that the child also runs the second fork, 3 counts forks plus one instead of doubling, and 6 does not follow from any doubling pattern.",
                 hint='Every process alive at a fork call splits into two.'),
            dict(id='challenge-os-processes-threads-q2', kind='prediction', title='Not shared between threads',
                 prompt='Two threads belong to the same process. Which of these does each thread have its own copy of?',
                 options=['The heap', 'The stack', 'Global variables', 'Open file descriptors'], answer=1,
                 explanation="Each thread runs its own sequence of function calls, so it needs a private stack along with its own registers and program counter. The heap, globals and open files belong to the process and are shared by all its threads, which is exactly why threads need synchronization when they touch them.",
                 hint='Think about what records where each thread is in its own chain of function calls.'),
            dict(id='challenge-os-processes-threads-q3', kind='prediction', title='After the disk read',
                 prompt='A process is waiting for a disk read. The read completes. What state does the process move to next?',
                 options=['Running', 'Terminated', 'Ready', 'New'], answer=2,
                 explanation="Finishing I/O only makes the process eligible to run again, so it joins the ready queue and waits for the scheduler to pick it. It does not jump straight to running, because another process may already be on the CPU. It is not terminated, since it has more work to do, and new applies only to a process being created.",
                 hint='Being able to run is not the same as being given the CPU.'),
            dict(id='challenge-os-processes-threads-q4', kind='prediction', title='Zombie process',
                 prompt='Which situation creates a zombie process?',
                 options=['A child has exited but its parent has not yet called wait for it', 'A parent exits while its child is still running', 'A process is stuck waiting forever on I/O', 'A process uses too much memory and gets swapped out'], answer=0,
                 explanation="A zombie is a finished child whose exit status has not been collected, so its process table entry stays around until the parent calls wait. A parent exiting first creates an orphan, not a zombie. A process stuck on I/O is simply blocked, and being swapped out is a memory management event that has nothing to do with exit status.",
                 hint='The process is dead, but someone has not picked up its exit status yet.'),
            dict(id='challenge-os-processes-threads-q5', kind='prediction', title='Why thread switches are cheaper',
                 prompt='Why is switching between two threads of the same process usually cheaper than switching between two processes?',
                 options=['Threads do not need their registers saved', 'Threads never get preempted by the timer', 'Threads always run on separate cores', 'The address space stays the same, so no memory map switch or TLB flush is needed'], answer=3,
                 explanation="Threads of one process share the same address space, so the kernel only swaps registers and the stack pointer and keeps the memory mapping and the TLB contents. Registers still have to be saved for threads, threads can be preempted like anything else, and nothing guarantees they run on separate cores.",
                 hint='Ask what stays the same when both threads live inside the same process.'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-os-cpu-scheduling', kind='guide', track=TRACK, subject=SUBJECT,
        title='CPU scheduling', order=2,
        summary='CPU scheduling decides which ready process runs next, and each algorithm trades off waiting time, fairness and responsiveness differently.',
        sections=[
            dict(title='What the scheduler is optimising', text=(
                "When several processes are ready, the short-term scheduler picks which one gets the CPU. You will be asked to compare algorithms using a few measures. "
                "Turnaround time is completion time minus arrival time. Waiting time is turnaround time minus the CPU burst, so it is the total time spent sitting in the ready queue. "
                "Response time is the gap between arrival and the first time the process gets the CPU. Throughput is how many processes finish per unit of time.\n\n"
                "Algorithms are either non-preemptive, where a running process keeps the CPU until it finishes its burst or blocks, "
                "or preemptive, where the OS can take the CPU away, for example when a timer fires or a more urgent process arrives. "
                "Interactive systems need preemption, otherwise one long job can freeze everything behind it."
            )),
            dict(title='FCFS and SJF with a worked example', text=(
                "First come first served runs processes in arrival order. It is simple and fair in a queueing sense, but it suffers from the convoy effect: short jobs stuck behind a long one wait a long time.\n\n"
                "Take three processes that all arrive at time 0 in the order P1, P2, P3, with CPU bursts of 10, 4 and 2. Under FCFS, P1 runs from 0 to 10, P2 from 10 to 14 and P3 from 14 to 16. "
                "The waiting times are 0, 10 and 14, so the average waiting time is 24 divided by 3, which is 8.\n\n"
                "Shortest job first picks the smallest burst. The order becomes P3, P2, P1. P3 waits 0, P2 waits 2 and P1 waits 6, so the average is 8 divided by 3, about 2.67. "
                "Non-preemptive SJF gives the minimum average waiting time for a set of jobs that are all available. "
                "The catch is that the OS cannot know future burst lengths, so real systems estimate them, often with an exponential average of past bursts."
            )),
            dict(title='SRTF, the preemptive version of SJF', text=(
                "Shortest remaining time first is SJF with preemption. Whenever a new process arrives, the scheduler compares its burst with the remaining time of the running process and switches if the newcomer is shorter.\n\n"
                "Suppose P1 arrives at 0 with burst 7, P2 arrives at 2 with burst 3 and P3 arrives at 3 with burst 1. P1 runs from 0 to 2. At time 2 P1 has 5 left and P2 needs 3, so P2 takes over. "
                "At time 3 P2 has 2 left and P3 needs 1, so P3 runs from 3 to 4. Then P2 finishes from 4 to 6 and P1 finishes from 6 to 11.\n\n"
                "Waiting time is completion minus arrival minus burst. P1 waits 11 minus 0 minus 7, which is 4. P2 waits 6 minus 2 minus 3, which is 1. P3 waits 4 minus 3 minus 1, which is 0. "
                "The average is 5 divided by 3, about 1.67. Both SJF and SRTF can starve a long job if short jobs keep arriving."
            )),
            dict(title='Round robin and the time quantum', text=(
                "Round robin gives each ready process a fixed time quantum in turn. If a process is not done when its quantum expires, it goes to the back of the ready queue.\n\n"
                "Use the same bursts as before, 10, 4 and 2, all arriving at 0, with a quantum of 4. P1 runs 0 to 4 and has 6 left. P2 runs 4 to 8 and finishes. "
                "P3 runs 8 to 10 and finishes. P1 then runs 10 to 16. Completion times are 16, 8 and 10, so waiting times are 6, 4 and 8, an average of 18 divided by 3, which is 6.\n\n"
                "That average is worse than SJF, but round robin's strength is response time: no process waits more than (n minus 1) quanta before its first turn. "
                "The quantum size matters. If it is very large, round robin behaves like FCFS. If it is very small, the CPU spends a large share of its time on context switches."
            )),
            dict(title='Priority scheduling and starvation', text=(
                "Priority scheduling runs the highest priority ready process. It can be preemptive or not. SJF is really a special case where priority is the inverse of the predicted burst.\n\n"
                "The classic problem is starvation, also called indefinite blocking. A low priority process can sit in the ready queue forever if higher priority work keeps arriving. "
                "The standard fix is aging: the longer a process waits, the more its priority is raised, so eventually it must run.\n\n"
                "Real systems often combine ideas. A multilevel queue keeps separate queues, for example one for interactive jobs and one for batch jobs, each with its own algorithm. "
                "A multilevel feedback queue lets processes move between levels, so a process that keeps using its full quantum drifts down and a process that often blocks for I/O stays near the top."
            )),
        ],
        keyPoints=[
            'Waiting time = turnaround time - burst time; turnaround time = completion time - arrival time.',
            'FCFS is simple but causes the convoy effect when a long job runs first.',
            'Non-preemptive SJF minimises average waiting time when all jobs are available; SRTF is its preemptive form.',
            'Round robin gives good response time; a huge quantum makes it FCFS, a tiny one wastes time switching.',
            'SJF, SRTF and priority scheduling can starve processes; aging fixes priority starvation.',
        ],
        challenges=[
            dict(id='challenge-os-cpu-scheduling-q1', kind='prediction', title='SJF average waiting time',
                 prompt='Three processes arrive at time 0 with bursts 6, 2 and 4. Using non-preemptive SJF, what is the average waiting time?',
                 options=['4.67', '3.33', '2.67', '4'], answer=2,
                 explanation="SJF runs the bursts in the order 2, 4, 6. The waits are 0, then 2, then 2 plus 4 which is 6, for a total of 8 and an average of 8 divided by 3, about 2.67. The value 4.67 is what FCFS gives in the order 6, 2, 4 (waits 0, 6, 8). The others come from summing the wrong waits.",
                 hint='Sort the bursts, then each process waits for the sum of the bursts before it.'),
            dict(id='challenge-os-cpu-scheduling-q2', kind='prediction', title='Round robin finish time',
                 prompt='P1 (burst 5) and P2 (burst 3) both arrive at time 0, P1 first. Round robin uses a quantum of 2. At what time does P2 finish?',
                 options=['7', '5', '8', '6'], answer=0,
                 explanation="P1 runs 0 to 2 (3 left), P2 runs 2 to 4 (1 left), P1 runs 4 to 6 (1 left), then P2 runs 6 to 7 and finishes. P1 finishes at 8, which is the distractor for anyone who mixes up the two. 5 is P2's burst plus one slice of P1, and 6 is when P1's second slice ends, but P2 still needs one more unit after that.",
                 hint='Write the timeline in slices of 2 and alternate between the two processes.'),
            dict(id='challenge-os-cpu-scheduling-q3', kind='prediction', title='Huge time quantum',
                 prompt='In round robin, what happens if the time quantum is larger than every process burst?',
                 options=['It becomes SJF', 'It becomes priority scheduling', 'It becomes FCFS', 'Every process starves'], answer=2,
                 explanation="If no process ever uses up its quantum, each one runs to completion in queue order, which is exactly first come first served. It does not reorder by burst length, so it is not SJF, it ignores priorities, and since every process gets its turn in order nothing starves.",
                 hint='Ask whether a quantum ever actually expires.'),
            dict(id='challenge-os-cpu-scheduling-q4', kind='prediction', title='Fixing starvation',
                 prompt='Under priority scheduling, a low priority job has been waiting for hours. Which technique directly addresses this?',
                 options=['Making the time quantum smaller', 'Aging, which raises the priority of jobs the longer they wait', 'Switching to non-preemptive scheduling', 'Adding more memory'], answer=1,
                 explanation="Aging steadily raises a waiting job's priority, so it eventually outranks newer work and runs. A smaller quantum only matters for round robin within a priority level, non-preemptive scheduling still always picks the highest priority job, and memory has nothing to do with which job the CPU picks.",
                 hint='The fix should change something about the waiting job over time.'),
            dict(id='challenge-os-cpu-scheduling-q5', kind='prediction', title='SRTF completion',
                 prompt='Under SRTF, P1 arrives at 0 with burst 6, P2 at 1 with burst 3, P3 at 2 with burst 1. When does P2 complete?',
                 options=['4', '5', '9', '10'], answer=1,
                 explanation="P1 runs 0 to 1 and is preempted by P2 (3 versus 5 remaining). At 2 P3 arrives needing 1 while P2 has 2 left, so P3 runs 2 to 3. P2 then runs its last 2 units from 3 to 5, and P1 finishes from 5 to 10. 4 forgets that P3 preempts P2, 9 is FCFS (P1 0 to 6, then P2 6 to 9), and 10 is non-preemptive SJF (P1 0 to 6, P3 6 to 7, P2 7 to 10), which is also when P1 finishes under SRTF.",
                 hint='Recompare remaining times at every arrival, not just when a process finishes.'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-os-synchronization', kind='guide', track=TRACK, subject=SUBJECT,
        title='Synchronization', order=3,
        summary='Synchronization makes sure threads that share data take turns in critical sections, using tools such as mutexes, semaphores and condition variables.',
        sections=[
            dict(title='Race conditions and critical sections', text=(
                "A race condition happens when the result depends on the exact timing of threads that share data. The textbook case is count++ run by two threads. "
                "That one line is really three steps: load count into a register, add 1, store it back. If count is 0 and both threads load 0 before either stores, both store 1, and one increment is lost. "
                "The final value can be 1 even though you expected 2.\n\n"
                "The piece of code that touches shared data is called a critical section. A correct solution must guarantee three things. "
                "Mutual exclusion: at most one thread is inside at a time. Progress: if nobody is inside and some threads want in, the choice cannot be postponed forever. "
                "Bounded waiting: once a thread asks to enter, there is a limit on how many times others can go ahead of it."
            )),
            dict(title='Locks and mutexes', text=(
                "A mutex, short for mutual exclusion lock, is the simplest tool. A thread calls lock before the critical section and unlock after it. "
                "If the mutex is already held, the caller waits. A key property is ownership: only the thread that locked a mutex should unlock it.\n\n"
                "Locks are built on atomic hardware instructions such as test-and-set or compare-and-swap, which read and update a memory word in one indivisible step. "
                "A spinlock keeps retrying in a loop while it waits. That burns CPU, but it avoids the cost of sleeping and waking, so it suits very short critical sections on a multi-core machine. "
                "A blocking mutex instead puts the waiting thread to sleep, which is better when the wait may be long.\n\n"
                "Keep critical sections short. Holding a lock while doing slow work such as I/O forces every other thread to wait for no reason."
            )),
            dict(title='Semaphores', text=(
                "A semaphore is an integer counter with two atomic operations. Wait, also called P or down, decrements the counter and blocks the caller if no units are available. "
                "Signal, also called V or up, increments the counter and wakes a waiting thread if there is one.\n\n"
                "A counting semaphore starts at the number of identical resources. If you have 3 database connections, initialise it to 3. "
                "The first three threads that call wait get through, and a fourth or fifth caller blocks until someone signals. "
                "A binary semaphore only takes the values 0 and 1, so it can act like a lock.\n\n"
                "The interview distinction between a mutex and a binary semaphore is ownership and purpose. A mutex is a lock owned by the thread that took it. "
                "A semaphore has no owner, so one thread can wait and a different thread can signal. That makes semaphores good for signalling between threads, for example a producer telling a consumer that data is ready."
            )),
            dict(title='Producer and consumer with a bounded buffer', text=(
                "In the bounded buffer problem, producers add items to a buffer of size N and consumers remove them. You need three semaphores. "
                "Empty starts at N and counts free slots. Full starts at 0 and counts filled slots. Mutex starts at 1 and protects the buffer itself.\n\n"
                "A producer does wait on empty, wait on mutex, adds the item, signal on mutex, signal on full. A consumer does wait on full, wait on mutex, removes an item, signal on mutex, signal on empty.\n\n"
                "The order of the two waits matters. Suppose a producer takes the mutex first and then waits on empty while the buffer is full. "
                "It sleeps while holding the mutex, so no consumer can enter to free a slot, and everyone is stuck. "
                "Always wait for the resource count first and take the mutex last. This is a neat example of how a small ordering mistake becomes a deadlock."
            )),
            dict(title='Monitors and condition variables', text=(
                "Semaphores are powerful but easy to misuse, since a single missing signal can hang a program. Monitors package shared data with the procedures that use it, and the language guarantees that only one thread is active inside the monitor at a time. "
                "Java's synchronized methods follow this idea.\n\n"
                "Inside a monitor, a condition variable lets a thread wait until some state becomes true. Calling wait releases the monitor lock and sleeps atomically, so no wake-up is missed. "
                "Another thread changes the state and calls signal or notify.\n\n"
                "Always recheck the condition in a while loop after waking, not with an if. Another thread may have changed the state between the signal and your thread getting the lock back, "
                "and many systems allow spurious wake-ups. Unlike a semaphore, a condition variable has no memory: a signal sent when nobody is waiting is simply lost."
            )),
        ],
        keyPoints=[
            'count++ is load, add, store, so two unsynchronised threads can lose an update.',
            'A critical section solution needs mutual exclusion, progress and bounded waiting.',
            'A mutex has an owner; a semaphore is a counter that any thread can signal.',
            'Spinlocks suit very short waits on multi-core systems; blocking locks suit longer waits.',
            'In producer-consumer, wait on empty or full before taking the mutex, or you can deadlock.',
            'Recheck a condition variable predicate in a while loop after waking.',
        ],
        challenges=[
            dict(id='challenge-os-synchronization-q1', kind='prediction', title='Lost update',
                 prompt='Shared x starts at 0. Two threads each run x++ once with no lock. Which final values of x are possible?',
                 options=['Only 2', '1 or 2', '0, 1 or 2', 'Only 1'], answer=1,
                 explanation="If the increments do not overlap, x ends at 2. If both threads load 0 before either stores, both store 1 and one update is lost, giving 1. It cannot end at 0 because at least one store of a value of 1 or more happens last. Saying only 2 ignores the race, and only 1 ignores the safe interleaving.",
                 hint='Split x++ into load, add and store, then try interleaving them.'),
            dict(id='challenge-os-synchronization-q2', kind='prediction', title='Counting semaphore',
                 prompt='A semaphore is initialised to 3. Five threads call wait on it and nobody has called signal yet. How many threads are blocked?',
                 options=['0', '3', '5', '2'], answer=3,
                 explanation="The counter allows three threads through, one per unit. The fourth and fifth find no units left and block, so 2 are blocked. 3 confuses the threads that got in with those that are blocked, 0 ignores the limit, and 5 would only happen if the semaphore started at 0.",
                 hint='The initial value is how many can pass before anyone has to wait.'),
            dict(id='challenge-os-synchronization-q3', kind='prediction', title='Mutex versus semaphore',
                 prompt='Thread A must tell thread B that a file has finished downloading. Which primitive fits best, and why?',
                 options=['A semaphore starting at 0, because a different thread from the waiter can signal it', 'A mutex, because only the locking thread can unlock it', 'A spinlock, because downloads are short', 'No primitive is needed, since threads share memory'], answer=0,
                 explanation="B waits on a semaphore initialised to 0, and A signals it when the download is done. Semaphores have no owner, so cross-thread signalling is exactly their use. The ownership rule of a mutex is what makes it wrong here, a spinlock would waste CPU for a long wait, and sharing memory alone gives B no safe way to sleep until the event.",
                 hint='One thread waits and a different thread announces the event.'),
            dict(id='challenge-os-synchronization-q4', kind='prediction', title='Wrong order of waits',
                 prompt='A producer calls wait(mutex) and then wait(empty) while the buffer is full. What happens?',
                 options=['The producer overwrites the oldest item', 'The consumer removes an item and the producer continues normally', 'Deadlock: the producer sleeps holding the mutex, so no consumer can free a slot', 'The semaphore value goes negative and the program crashes'], answer=2,
                 explanation="The producer blocks on empty while still holding mutex. Every consumer needs the mutex before it can remove an item and signal empty, so nobody can proceed. The consumer cannot run normally for that reason, nothing overwrites items because the producer never reaches the buffer, and blocking is not a crash.",
                 hint='Ask what the consumer needs before it can free a slot.'),
            dict(id='challenge-os-synchronization-q5', kind='prediction', title='When a spinlock makes sense',
                 prompt='When is a spinlock a better choice than a blocking mutex?',
                 options=['When the lock is held during disk I/O', 'On a single-core machine with long critical sections', 'When the thread holding the lock is likely to sleep', 'On a multi-core machine where the lock is held for only a few instructions'], answer=3,
                 explanation="Spinning wastes CPU, but if the holder is running on another core and releases the lock almost immediately, spinning is cheaper than sleeping and waking. During disk I/O or when the holder sleeps, the spinner burns CPU for a long time. On a single core the spinner even prevents the holder from running to release it.",
                 hint='Spinning only pays off if the lock is about to be released by someone running in parallel.'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-os-deadlocks', kind='guide', track=TRACK, subject=SUBJECT,
        title='Deadlocks', order=4,
        summary='A deadlock is a set of processes each waiting for a resource held by another in the set, and it needs all four Coffman conditions to occur.',
        sections=[
            dict(title='What a deadlock is', text=(
                "A deadlock is a situation where a set of processes are all blocked, and each one is waiting for a resource that another process in the same set holds. "
                "None of them can move, so none of them will ever release what the others need.\n\n"
                "The simplest example uses two locks. Thread T1 takes lock A and then asks for lock B. At the same moment thread T2 takes lock B and then asks for lock A. "
                "T1 waits for T2 and T2 waits for T1, forever.\n\n"
                "Do not confuse deadlock with starvation. In starvation a process could run in principle, but the scheduler or other processes keep pushing it aside. "
                "In deadlock nobody in the set can run at all. A livelock is a third case where processes keep changing state in response to each other, like two people stepping aside in a corridor, but no real progress happens."
            )),
            dict(title='The four Coffman conditions', text=(
                "A deadlock can only happen if all four of these conditions hold at the same time.\n\n"
                "Mutual exclusion: at least one resource can be held by only one process at a time. "
                "Hold and wait: a process holds at least one resource while waiting to get more. "
                "No preemption: a resource cannot be taken away from a process; it must be released voluntarily. "
                "Circular wait: there is a cycle of processes where each waits for a resource held by the next one in the cycle.\n\n"
                "These are necessary conditions, so breaking any one of them is enough to make deadlock impossible. "
                "In a resource allocation graph, processes and resources are nodes, and edges show requests and assignments. "
                "If every resource has a single instance, a cycle in the graph means deadlock. If resources have several instances, a cycle means deadlock is possible but not certain."
            )),
            dict(title='Prevention and the four strategies', text=(
                "There are four broad ways to handle deadlock. Prevention designs the system so one Coffman condition can never hold. "
                "Avoidance checks each request at run time and refuses any that could lead to trouble. Detection and recovery lets deadlocks happen, finds them, and breaks them. "
                "Ignoring the problem, sometimes called the ostrich approach, is what most general purpose systems do for application-level locks, because deadlocks are rare and prevention is costly.\n\n"
                "Prevention in practice usually attacks circular wait. Number every lock and require each thread to acquire locks in increasing order. "
                "In the two-lock example, both threads would take A before B, so no cycle can form. "
                "Hold and wait can be removed by requesting everything at once, which wastes resources. "
                "No preemption can be removed for things like CPU registers or memory pages whose state can be saved, but not for a printer halfway through a job. Mutual exclusion usually cannot be removed for truly unsharable resources."
            )),
            dict(title="Avoidance with the Banker's algorithm", text=(
                "The Banker's algorithm needs each process to declare its maximum demand in advance. "
                "A state is safe if there is some order in which every process can get its remaining need, finish, and return its resources. Before granting a request, the OS pretends to grant it and checks whether the resulting state is still safe. If not, the process waits.\n\n"
                "Take one resource type with 10 units. P1 holds 3 with a maximum of 7, P2 holds 2 with a maximum of 4, and P3 holds 2 with a maximum of 5. That is 7 allocated, so 3 are available. "
                "The remaining needs are 4, 2 and 3. P2 can finish with 2 more, leaving 5 available. Then P3 needs 3, finishes, and leaves 7. Then P1 needs 4 and finishes. The order P2, P3, P1 shows the state is safe.\n\n"
                "Now suppose P1 asks for 2 more. Available would drop to 1 while the needs become 2, 2 and 3. Nobody could finish, so the state is unsafe and the request is postponed. "
                "Note that unsafe does not mean deadlocked yet; it means the OS can no longer guarantee avoiding one."
            )),
            dict(title='Detection and recovery', text=(
                "If you allow deadlocks to happen, you need a way to find them. With single-instance resources, the system builds a wait-for graph, where an edge from P1 to P2 means P1 waits for something P2 holds, and looks for a cycle. "
                "With multiple instances, it runs a detection algorithm similar to the Banker's safety check, but using current requests instead of declared maximums.\n\n"
                "Recovery has two main options. You can terminate processes, either all of those in the deadlock or one at a time until the cycle breaks. "
                "Or you can preempt resources, taking a resource from a victim and rolling that process back to a safe checkpoint. "
                "Victims are usually chosen by cost: how long they have run, how much they hold, and how much work rollback would lose. "
                "Databases do this all the time. When two transactions deadlock on row locks, the database aborts one of them and the application retries."
            )),
        ],
        keyPoints=[
            'Deadlock requires mutual exclusion, hold and wait, no preemption and circular wait together.',
            'Breaking any one Coffman condition prevents deadlock; global lock ordering breaks circular wait.',
            'With single-instance resources, a cycle in the allocation graph means deadlock.',
            "The Banker's algorithm grants a request only if a safe sequence still exists afterwards.",
            'An unsafe state is not necessarily a deadlock, but the OS can no longer guarantee avoiding one.',
        ],
        challenges=[
            dict(id='challenge-os-deadlocks-q1', kind='prediction', title='Lock ordering',
                 prompt='Every thread in a program must acquire locks in a fixed global order. Which Coffman condition does this break?',
                 options=['Mutual exclusion', 'Hold and wait', 'Circular wait', 'No preemption'], answer=2,
                 explanation="If everyone climbs the same ordering, no thread can hold a higher lock while waiting for a lower one, so a cycle of waits cannot form. Threads still hold locks exclusively, still hold one lock while waiting for the next, and locks still cannot be taken away, so the other three conditions remain.",
                 hint='Picture the wait-for graph and ask what shape the ordering rules out.'),
            dict(id='challenge-os-deadlocks-q2', kind='prediction', title="Banker's request",
                 prompt='10 units of one resource. P1 holds 3 (max 7), P2 holds 2 (max 4), P3 holds 2 (max 5). P1 requests 2 more. What does the Banker\'s algorithm do?',
                 options=['Grants it, because 3 units are available', 'Refuses for now, because afterwards no process could be sure to finish', 'Grants it, because P1 is still under its maximum', 'Kills P3 to free resources'], answer=1,
                 explanation="After granting, available would be 1 and the remaining needs would be 2, 2 and 3, so no process could finish and the state would be unsafe. Having enough units available and staying under the maximum are both required but not sufficient. The Banker's algorithm makes the request wait; it never kills processes.",
                 hint='Pretend to grant it, then look for any process whose remaining need fits in what is left.'),
            dict(id='challenge-os-deadlocks-q3', kind='prediction', title='Minimum resources',
                 prompt='Three processes each need at most 3 units of one resource type. What is the smallest number of units that guarantees no deadlock?',
                 options=['6', '9', '8', '7'], answer=3,
                 explanation="In the worst case each process holds 2 units and waits for its third, using 6. One more unit, 7 in total, lets one process finish and release 3, which unblocks the rest. With 6 everyone can be stuck at 2. 8 and 9 also work but are not the minimum.",
                 hint='Give every process one less than its maximum, then add just enough to break the tie.'),
            dict(id='challenge-os-deadlocks-q4', kind='prediction', title='Cycle with many instances',
                 prompt='A resource allocation graph has a cycle, but one resource type in the cycle has two instances. What can you conclude?',
                 options=['A deadlock is possible but not certain', 'The system is definitely deadlocked', 'The system is definitely not deadlocked', 'The graph is invalid'], answer=0,
                 explanation="With multiple instances, a process outside the cycle may hold the other instance and release it, breaking the wait. So a cycle is necessary but not sufficient. Only with single-instance resources does a cycle prove deadlock, and the graph is perfectly valid.",
                 hint='Could someone outside the cycle free the extra instance?'),
            dict(id='challenge-os-deadlocks-q5', kind='prediction', title='Deadlock or starvation',
                 prompt='A low priority process is ready to run but never gets the CPU because higher priority work keeps arriving. What is this?',
                 options=['Deadlock', 'Circular wait', 'Starvation', 'Livelock'], answer=2,
                 explanation="The process could run if chosen, but it keeps being passed over, which is starvation. Deadlock and circular wait need processes blocked on resources held by each other, and livelock needs processes actively reacting to each other without progress.",
                 hint='Is the process blocked on a resource, or just never picked?'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-os-memory-paging', kind='guide', track=TRACK, subject=SUBJECT,
        title='Memory management and paging', order=5,
        summary='Paging splits memory into fixed-size pages and frames, with the TLB speeding up translation and page replacement handling memory that is overcommitted.',
        sections=[
            dict(title='Logical addresses and fragmentation', text=(
                "Every address your program uses is a logical, or virtual, address. The memory management unit translates it to a physical address in RAM. "
                "This lets each process believe it has a clean address space starting at zero, while the OS places its pieces wherever there is room.\n\n"
                "Early systems gave each process one contiguous block. That leads to external fragmentation: there may be 100 MB free in total, but split into small gaps so no 50 MB process fits. "
                "Compaction can fix it but is expensive.\n\n"
                "Internal fragmentation is waste inside an allocated unit. If memory is handed out in 4 KB pages and a process needs 10,300 bytes, it gets three pages, 12,288 bytes, and wastes 1,988 bytes in the last page. "
                "Paging removes external fragmentation entirely but keeps a little internal fragmentation, at most one page minus one byte per region."
            )),
            dict(title='How paging translates an address', text=(
                "Paging cuts logical memory into fixed-size pages and physical memory into frames of the same size. Any page can go in any free frame. "
                "A per-process page table maps page numbers to frame numbers.\n\n"
                "A logical address splits into a page number and an offset. With a page size of 2 to the power d, the low d bits are the offset. "
                "For 32-bit addresses and 4 KB pages, 12 bits are the offset and 20 bits are the page number, so the page table can have 2 to the power 20 entries, about a million.\n\n"
                "Here is a small worked example with 4,096-byte pages. Logical address 8,200 is in page 8,200 divided by 4,096, which is page 2, at offset 8,200 minus 8,192, which is 8. "
                "If the page table says page 2 lives in frame 5, the physical address is 5 times 4,096 plus 8, which is 20,488. "
                "Large page tables are handled with multi-level page tables or inverted page tables."
            )),
            dict(title='The TLB and effective access time', text=(
                "With a page table in memory, every load or store would need two memory accesses: one to read the page table entry and one for the data. "
                "The translation lookaside buffer, or TLB, is a small fast cache of recent page-to-frame mappings inside the CPU. On a TLB hit, translation costs almost nothing. On a miss, the hardware or OS walks the page table and fills the TLB.\n\n"
                "You may be asked for the effective access time. Suppose a memory access takes 50 ns, a TLB lookup takes 5 ns, and the hit ratio is 90 percent. "
                "A hit costs 5 plus 50, which is 55 ns. A miss costs 5 plus 50 for the page table plus 50 for the data, which is 105 ns. "
                "The effective time is 0.9 times 55 plus 0.1 times 105, which is 49.5 plus 10.5, or 60 ns.\n\n"
                "TLBs work well because programs have locality: they keep touching the same few pages for a while."
            )),
            dict(title='Page faults and replacement', text=(
                "With demand paging, a page is loaded only when it is first touched. Each page table entry has a valid bit. Accessing an invalid page triggers a page fault: "
                "the OS finds the page on disk, picks a free frame, reads the page in, updates the table, and restarts the instruction. Faults are very expensive because disk is far slower than RAM.\n\n"
                "When no frame is free, a replacement policy chooses a victim. FIFO evicts the oldest loaded page. LRU evicts the page not used for the longest time. "
                "Optimal evicts the page that will not be needed for the longest time in the future; it cannot be built but is the yardstick for others.\n\n"
                "With 3 frames and the reference string 1, 2, 3, 1, 4, 2, 5, FIFO faults on 1, 2 and 3, hits on 1, faults on 4 and evicts 1, hits on 2, then faults on 5 and evicts 2, for 5 faults in total. "
                "FIFO can also show Belady's anomaly, where giving it more frames causes more faults. LRU and optimal never do."
            )),
            dict(title='Thrashing and the working set', text=(
                "Thrashing is when the system spends most of its time moving pages in and out instead of doing useful work. It happens when the processes in memory together need more frames than exist, "
                "so each one keeps faulting and stealing frames from the others.\n\n"
                "The classic trap is a naive scheduler. It sees low CPU utilisation, because everyone is waiting on page faults, and admits more processes to keep the CPU busy. "
                "That makes the shortage worse and utilisation falls further.\n\n"
                "The working set of a process is the set of pages it used in a recent window of time. If the OS keeps each process's working set in memory, faults stay low. "
                "When the total working sets exceed physical memory, the right move is to suspend or swap out a whole process, not add more. "
                "A related approach watches each process's page fault frequency and gives it more frames when the rate is high or takes some away when it is low."
            )),
        ],
        keyPoints=[
            'Paging removes external fragmentation but leaves some internal fragmentation in the last page.',
            'A logical address is page number plus offset; physical address = frame number x page size + offset.',
            'The TLB caches translations; a miss costs an extra memory access for the page table.',
            'A page fault means the page is not in memory, so the OS must load it from disk.',
            "FIFO can suffer Belady's anomaly; LRU and optimal cannot.",
            'Thrashing happens when working sets exceed physical memory; reduce the number of processes to fix it.',
        ],
        challenges=[
            dict(id='challenge-os-memory-paging-q1', kind='prediction', title='Address translation',
                 prompt='Page size is 1,024 bytes. Logical address 3,000 is accessed and its page maps to frame 7. What is the physical address?',
                 options=['7,952', '8,120', '10,168', '3,952'], answer=1,
                 explanation="3,000 divided by 1,024 is page 2 with offset 3,000 minus 2,048, which is 952. Frame 7 starts at 7 times 1,024, which is 7,168, so the physical address is 7,168 plus 952, which is 8,120. 7,952 multiplies the frame number by 1,000 instead of 1,024, 10,168 adds the whole logical address to the frame base, and 3,952 adds the offset to the logical address instead of to the frame's base address.",
                 hint='First split the address into page number and offset, then rebuild it with the frame number.'),
            dict(id='challenge-os-memory-paging-q2', kind='prediction', title='Effective access time',
                 prompt='Memory access is 100 ns, TLB lookup is 10 ns and the TLB hit ratio is 90 percent. What is the effective memory access time?',
                 options=['110 ns', '130 ns', '120 ns', '210 ns'], answer=2,
                 explanation="A hit costs 10 + 100 = 110 ns. A miss costs 10 + 100 for the page table + 100 for the data = 210 ns. The average is 0.9 x 110 + 0.1 x 210 = 99 + 21 = 120 ns. 110 and 210 are just the hit and miss costs, and 130 counts the extra page table access twice on a miss.",
                 hint='Work out the cost of a hit and of a miss, then weight them by how often each happens.'),
            dict(id='challenge-os-memory-paging-q3', kind='prediction', title='FIFO page faults',
                 prompt='With 3 frames, initially empty, and the reference string 1, 2, 3, 4, 1, 2, how many page faults does FIFO cause?',
                 options=['4', '5', '6', '3'], answer=2,
                 explanation="1, 2 and 3 fault and fill the frames. 4 faults and evicts 1. Then 1 faults and evicts 2, and 2 faults and evicts 3. Every reference faults, so the total is 6. Answers of 4 or 5 assume 1 or 2 are still resident, but FIFO evicted each one just before it was needed again.",
                 hint='Track the frames after each reference and remember FIFO evicts the earliest loaded page.'),
            dict(id='challenge-os-memory-paging-q4', kind='prediction', title='Internal fragmentation',
                 prompt='Pages are 2,048 bytes. A process needs 9,000 bytes of memory. How many bytes are lost to internal fragmentation?',
                 options=['1,240', '808', '2,048', '0'], answer=0,
                 explanation="9,000 bytes need 5 pages, since 4 pages hold only 8,192. Five pages hold 10,240 bytes, and 10,240 minus 9,000 is 1,240. 808 is 9,000 minus 8,192, the amount that spills into the fifth page rather than the waste. 2,048 is a whole page, but most of the last page is used, and 0 would only be true if the size were an exact multiple of the page size.",
                 hint='Round the size up to whole pages, then subtract what is actually needed.'),
            dict(id='challenge-os-memory-paging-q5', kind='prediction', title='Responding to thrashing',
                 prompt='CPU utilisation is low and the disk is busy with paging. What is the right response?',
                 options=['Admit more processes to keep the CPU busy', 'Switch from LRU to FIFO replacement', 'Make the time quantum shorter', 'Suspend some processes so the rest can keep their working sets in memory'], answer=3,
                 explanation="This is thrashing: the working sets of the running processes do not fit in memory. Reducing the number of processes frees frames so the others stop faulting. Admitting more processes makes it worse, FIFO is not better than LRU at this, and a shorter quantum changes CPU sharing, not memory pressure.",
                 hint='The CPU is idle because processes are waiting on the disk, not because there is too little work.'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-os-file-systems', kind='guide', track=TRACK, subject=SUBJECT,
        title='File systems', order=6,
        summary='A file system maps names to data blocks on disk, using directories, inodes, allocation schemes and journaling to keep files organised and safe.',
        sections=[
            dict(title='Files, directories and metadata', text=(
                "To a user, a file is a named sequence of bytes. To the file system, it is metadata plus a set of disk blocks holding the data. "
                "Metadata includes the size, owner, permissions, timestamps and the locations of the data blocks.\n\n"
                "A directory is itself a special file whose contents are a list of entries, each mapping a name to the file it refers to. "
                "Directories nest to form a tree, and a path such as /home/asha/notes.txt is resolved one component at a time, starting from the root directory.\n\n"
                "When a program opens a file, the OS resolves the path once, loads the metadata, and returns a file descriptor, a small integer that indexes a per-process table of open files. "
                "Later reads and writes use the descriptor, so the path is not looked up again on every call. "
                "The open file entry also tracks the current offset, which is why two successive reads continue where the last one stopped."
            )),
            dict(title='Inodes in Unix file systems', text=(
                "Unix-style file systems store each file's metadata in an inode, short for index node. An inode holds the file type, size, owner, permissions, timestamps, a link count and pointers to the data blocks. "
                "Notably, it does not hold the file name. Names live only in directory entries, which map a name to an inode number.\n\n"
                "An inode usually has a handful of direct pointers plus single, double and triple indirect pointers. A single indirect pointer points to a block that contains more block pointers. "
                "Say blocks are 4 KB, pointers are 4 bytes, and there are 12 direct pointers. Direct pointers cover 12 times 4 KB, which is 48 KB. "
                "One indirect block holds 4,096 divided by 4, which is 1,024 pointers, covering 1,024 times 4 KB, which is 4 MB. "
                "This design makes small files fast to reach while still allowing very large files through the deeper levels."
            )),
            dict(title='Hard links and soft links', text=(
                "Because names are separate from inodes, a single file can have several names. A hard link is just another directory entry pointing to the same inode. "
                "The inode's link count tracks how many names exist. Deleting a name removes one entry and decrements the count; the data is freed only when the count reaches zero and no process has the file open.\n\n"
                "So if a.txt has a hard link b.txt and you delete a.txt, b.txt still opens the same data. Hard links normally cannot point to directories and cannot cross file systems, since inode numbers are only unique within one file system.\n\n"
                "A soft link, or symbolic link, is a small separate file whose content is a path. Opening it makes the OS follow that path. "
                "Soft links can cross file systems and point to directories, but if the target is deleted or moved, the link dangles and opening it fails."
            )),
            dict(title='How blocks are allocated', text=(
                "The file system must decide which disk blocks belong to each file. Contiguous allocation gives a file one run of consecutive blocks. "
                "Sequential and random access are both fast, since block i is just the start plus i, but it causes external fragmentation and makes files hard to grow.\n\n"
                "Linked allocation stores a pointer to the next block inside each block. There is no external fragmentation and files grow easily, but reaching block 500 means following 499 pointers, "
                "and one corrupted pointer loses the rest of the file. The FAT design moves those next pointers into a file allocation table at the start of the volume, which is small enough to cache in memory, so following the chain no longer needs a disk read per block.\n\n"
                "Indexed allocation, which inodes use, keeps all of a file's block pointers in one place. Random access is fast and there is no external fragmentation, at the cost of space for the index. "
                "Free blocks are often tracked with a bitmap, one bit per block, which makes finding runs of free space quick."
            )),
            dict(title='Crash consistency and journaling', text=(
                "Creating or growing a file updates several structures: the data block, the inode, the free-space bitmap and maybe a directory. "
                "If power fails halfway through, the disk can be left inconsistent, for example a block marked used that no file points to, or an inode pointing to a block still marked free.\n\n"
                "Older systems fixed this with a full check at boot, such as fsck, which scans every structure and can take a very long time on large disks. "
                "Journaling file systems such as ext4 and NTFS first write a description of the planned changes to a log, called the journal, and mark it committed. Only then do they apply the changes in place. "
                "After a crash, the system replays committed journal entries and discards incomplete ones, so recovery takes seconds.\n\n"
                "ext4 by default (data=ordered mode) and NTFS journal only metadata, not file contents. That keeps the structure consistent after a crash, but data written just before the crash can still be lost or only partly written. "
                "ext4's data=journal mode also logs file data, at the cost of writing it twice."
            )),
        ],
        keyPoints=[
            'A directory maps names to inode numbers; the inode stores metadata and block pointers, not the name.',
            'A hard link is another name for the same inode; data is freed when the link count hits zero.',
            'A soft link stores a path and dangles if the target is removed.',
            'Contiguous allocation is fast but fragments; linked is slow for random access; indexed balances both.',
            'Journaling logs changes before applying them, so crash recovery is fast.',
        ],
        challenges=[
            dict(id='challenge-os-file-systems-q1', kind='prediction', title='Where the name lives',
                 prompt='In a Unix file system, where is a file\'s name stored?',
                 options=['In the inode', 'In the directory entry that points to the inode', 'In the first data block of the file', 'In the superblock'], answer=1,
                 explanation="Directory entries map names to inode numbers, and the inode holds everything else. That separation is what lets one inode have several hard-linked names. The data blocks hold only file content, and the superblock describes the whole file system, not individual files.",
                 hint='If one file can have two names, the name cannot be part of the file itself.'),
            dict(id='challenge-os-file-systems-q2', kind='prediction', title='Deleting a hard-linked file',
                 prompt='a.txt has a hard link named b.txt. You delete a.txt. What happens when you open b.txt?',
                 options=['It fails because the data was freed', 'It opens but is empty', 'It opens normally with the same contents', 'It opens a copy taken when the link was made'], answer=2,
                 explanation="Both names point to the same inode. Deleting a.txt drops the link count from 2 to 1, so the inode and its data stay. The data is not freed until the count reaches zero, nothing is emptied, and a hard link never makes a copy. A soft link, by contrast, would dangle here.",
                 hint='Think about the inode link count before and after the delete.'),
            dict(id='challenge-os-file-systems-q3', kind='prediction', title='Inode reach',
                 prompt='Blocks are 4 KB, block pointers are 4 bytes, and an inode has 12 direct pointers and one single indirect pointer. What is the largest file it can address?',
                 options=['48 KB', '4 MB', '52 KB', '4,144 KB'], answer=3,
                 explanation="Direct pointers reach 12 x 4 KB = 48 KB. The indirect block holds 4,096 / 4 = 1,024 pointers, reaching 1,024 x 4 KB = 4,096 KB. Together that is 48 + 4,096 = 4,144 KB. 48 KB ignores the indirect pointer, 4 MB ignores the direct ones, and 52 KB counts the indirect block as a single data block.",
                 hint='Add what the direct pointers cover to what one full block of pointers covers.'),
            dict(id='challenge-os-file-systems-q4', kind='prediction', title='Random access',
                 prompt='Which allocation method is slowest for reading block 1,000 of a large file directly?',
                 options=['Linked allocation with pointers stored in each block', 'Contiguous allocation', 'Indexed allocation', 'They are all equally fast'], answer=0,
                 explanation="Linked allocation must read through the chain from the start, following 999 pointers stored on disk. Contiguous allocation computes the block address directly, and indexed allocation looks it up in the index, so both are fast. They clearly are not equal.",
                 hint='Which method has to visit earlier blocks just to find the next one?'),
            dict(id='challenge-os-file-systems-q5', kind='prediction', title='Why journaling helps',
                 prompt='What is the main benefit of a journaling file system?',
                 options=['It makes files smaller on disk', 'It removes the need for inodes', 'It lets each file have multiple names', 'After a crash it can recover a consistent state quickly by replaying the log instead of scanning the whole disk'], answer=3,
                 explanation="Journaling records intended changes before applying them, so after a crash the system replays committed entries and drops incomplete ones without a full scan. It does not compress files, ext4 and others still use inodes, and multiple names come from hard links, not from journaling.",
                 hint='Think about what happens when power fails in the middle of an update.'),
        ],
    ),
]

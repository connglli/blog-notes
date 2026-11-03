# Transactional Lock-Free Execution of Lock-Based Programs

**Summary by:** GPT 6 Astra

**Author:** Ravi Rajwar, James R. Goodman

**Source:** ASPLOS 2002; ASPLOS Influential Paper Award 2013

**Link:** https://doi.org/10.1145/605397.605399

## Key insight

Speculatively executing critical sections without taking their locks is useful only if conflicting executions can still make progress. Retaining timestamp-based priority across retries prevents competing transactions from repeatedly aborting one another without a winner.

## Basic idea

Transactional Lock Removal builds on speculative lock elision [1], executing a critical section with buffered state and conflict detection [2]. Nonconflicting sections can commit without acquiring the lock. When accesses conflict, timestamp priority [3] makes the older contender win, and a restarted contender retains its timestamp. The progress argument applies under the hardware and execution assumptions [4]; unsupported operations or resource limits can fall back to ordinary locking.

## Illustrative example

**Elide a coarse lock.** Two threads update different entries in a table normally protected by one lock. Their speculative executions retain the lock's externally visible free state while tracking the data they access. If their tracked sets do not conflict, both can complete without the unnecessary serialization imposed by the coarse lock.

**Create a conflict.** Suppose they instead update shared entries `left` and `right` in opposite access orders. Blindly aborting the holder whenever another request arrives can make the two threads repeatedly restart each other.

**Choose a winner.** Give the first transaction timestamp `(12, 0)` and the second `(12, 1)`, with processor identity breaking the clock tie. The first has higher priority. Its conflicting requests force the second to restart; the second's requests cannot force the first to wait for lower-priority speculative work. After the first completes, the second can retry.

**Keep the place in line.** The second retains its timestamp after conflict-induced restarts. Successful transactions advance their logical clocks according to the protocol, preventing a continual stream of new transactions from permanently taking priority over it. Timestamps resolve conflicts; they do not impose a total execution order on transactions that never conflict.

## Concepts and terms

**[1] Speculative lock elision.** Recognize suitable lock-acquire/release behavior and execute the enclosed code without making the lock held in shared memory. Track the assumptions needed for the execution to remain valid. The program remains written using locks; this is a hardware execution technique, not a source-level conversion into a different concurrent algorithm.

**[2] Speculative state and conflicts.** Buffer updates and preserve recoverable processor state until commit. Coherence activity detects conflicting accesses to tracked data. Abort discards speculative changes and restores the checkpoint. Irreversible effects cannot safely be treated like ordinary buffered stores.

**[3] Timestamp arbitration.** A logical clock plus processor identifier gives a unique priority. Earlier timestamps win conflicts; lower-priority contenders restart or defer their requests. Retaining a timestamp across conflict retries and monotonically advancing clocks after success are essential to the starvation-freedom argument.

**[4] Progress and fallback.** Finite tracking resources, cache evictions, interrupts, scheduling quanta, and operations such as I/O constrain speculative execution. The design permits acquiring the real lock when speculative execution cannot proceed. Consequently its title must not be read as an unconditional wait-free guarantee for every arbitrary lock-based program, including blocking or nonterminating critical sections.

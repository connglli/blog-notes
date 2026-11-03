# Algorithms for scalable synchronization on shared-memory multiprocessors

**Summary by:** GPT 6 Astra

**Author:** John M. Mellor-Crummey and Michael L. Scott

**Source:** ACM Transactions on Computer Systems 9(1), 1991; Edsger W. Dijkstra Prize in Distributed Computing 2006.

**Link:** https://doi.org/10.1145/103727.103729

## Key insight

Busy waiting need not repeatedly hammer one shared cache line. Each waiter can spin on a locally accessible flag and receive ownership through one write from its predecessor.

## Basic idea

The paper develops scalable locks and barriers using local spinning [1]. Its queue lock [2] links per-waiter records through an atomic tail exchange, then passes ownership directly to the next waiter. A compare-and-swap [3] release path handles the race between becoming the last waiter and a new arrival. The scalability metric concerns remote memory references [4], not a guarantee that lock acquisition completes despite a stalled owner.

## Illustrative example

**Join.** A owns the lock. B prepares a queue record containing a null successor pointer and a waiting flag, then atomically exchanges the shared tail with its own record. The exchange returns A's record, so B publishes itself as A's successor and spins on B's flag.

C repeats the process, receives B as predecessor, publishes itself as B's successor, and spins on C's own flag. A, B, and C do not all repeatedly read the same lock word.

**Handoff.** A releases by clearing B's waiting flag. B enters the critical section, then clears C's flag when it finishes. Each ownership transfer targets one successor instead of waking every waiter.

**Late-arrival race.** Suppose C is releasing and sees no successor. It tries to compare-and-swap the tail from C to null. If this succeeds, the queue was empty and C returns.

If D has already exchanged itself into the tail but has not yet linked itself through `C.next`, the compare-and-swap fails. C waits until its successor link appears, then clears D's flag. Returning immediately after the failed compare-and-swap would strand D.

**Implementation conditions.** Queue records remain valid while other participants may access them. Flag and link operations need the appropriate atomicity and ordering for the target memory model. Local placement or coherent caching makes the repeated polling local; the enqueue and handoff operations still perform remote communication.

If A is descheduled while holding the lock, B and C wait. Queueing avoids unnecessary communication and supplies an orderly handoff, but this remains a blocking mutual-exclusion lock.

## Concepts and terms

**[1] Local spinning.** Repeatedly polling a flag accessible from local memory or a coherent cache rather than issuing repeated remote operations on a contested shared location.

**[2] Queue lock.** A lock whose contenders form a linked waiting queue. The lock stores a tail pointer, and each participant supplies its own node for that acquisition.

**[3] Compare-and-swap.** An atomic operation replacing a location only if its current value equals an expected value. Here it detects whether a successor arrived before the tail was cleared.

**[4] Remote memory reference.** An operation requiring communication beyond locally accessible storage. The queue lock bounds such references per acquisition independently of the number of contending processors under the paper's placement assumptions.


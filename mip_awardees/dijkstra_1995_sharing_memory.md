# Sharing memory robustly in message-passing systems

**Summary by:** GPT 6 Astra

**Author:** Hagit Attiya, Amotz Bar-Noy, and Danny Dolev

**Source:** Journal of the ACM 42(1), 1995; Edsger W. Dijkstra Prize in Distributed Computing 2011.

**Link:** https://doi.org/10.1145/200836.200869

## Key insight

A majority can preserve the newest observed register value across failures, but readers must also propagate what they learn. Otherwise a read can expose a partial write that a later read forgets.

## Basic idea

The paper emulates an atomic single-writer multi-reader register [1] using message passing and majority quorums [2]. The simple unbounded version attaches an increasing timestamp [3] to each write and stores the greatest timestamp seen at each processor. A writer broadcasts and waits for a majority; a reader first queries a majority, then writes back [4] the greatest returned pair to a majority before returning it. Correct-majority availability and the specified communication assumptions provide termination despite crashes.

## Illustrative example

**Partial write.** Three replicas A, B, and C initially store value 4 at timestamp 0. The unique writer starts writing 9 with timestamp 1. Its message reaches A, but B and C have not received it and the write has not completed.

**Why query alone fails.** Reader R1 queries A and B and sees `(1,9)` and `(0,4)`. Returning 9 immediately would expose the concurrent write. A later reader R2 could query B and C, see only `(0,4)`, and return 4. That newer-then-older read sequence violates an atomic register.

**Write back.** Instead, R1 broadcasts `(1,9)` and waits until a majority, say A and B, acknowledges. Replicas retain their largest timestamp and never replace it with an older one.

R2's later query to B and C obtains timestamp 1 from B, selects value 9, and performs its own write-back before returning. Any possible majority query intersects the majority supporting R1's completed read, so the observation cannot be forgotten.

**Completion and ordering.** The original write may remain incomplete. It can nevertheless be placed before R1 in a legal atomic history, since their executions overlapped. R1's write-back preserves the value it exposed rather than waiting for the writer to recover.

The example uses the paper's simple unbounded timestamp construction. The paper also develops bounded representations and a dynamic-link setting; the three-replica trace does not establish those additional mechanisms. It also does not solve consensus: an atomic register supplies reads and writes, not the stronger synchronization operation consensus requires.

## Concepts and terms

**[1] Atomic single-writer multi-reader register.** A shared variable written by one designated process and read by several. Operations must admit one sequential ordering consistent with nonoverlapping real-time order.

**[2] Majority quorum.** More than half the replicas. Any two majorities intersect, while a correct majority allows an operation to complete without waiting for a particular failed replica.

**[3] Timestamp.** An ordering label assigned by the unique writer. In the unbounded construction it increases monotonically, letting replicas distinguish new data from delayed older messages.

**[4] Read write-back.** Propagating the highest observed timestamp/value pair and waiting for majority acknowledgment before completing a read. This protects observations of writes that were only partially disseminated.


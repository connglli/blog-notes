# Software transactional memory

**Summary by:** GPT 6 Astra

**Author:** Nir Shavit and Dan Touitou

**Source:** Distributed Computing 10(2), 1997 (conference version PODC 1995); Edsger W. Dijkstra Prize in Distributed Computing 2012.

**Link:** https://doi.org/10.1007/s004460050028

## Key insight

A process holding several memory locations need not block everyone if its transaction is described in shared state that others can finish. Ownership and helping can implement atomic multiword changes without dedicated transactional hardware.

## Basic idea

The implementation supports static transactions [1] whose accessed locations are known in advance. A shared transaction descriptor [2] records the data set, state, and information needed for another process to execute it. Processes acquire location ownership in a fixed order, perform the update after successful acquisition, and release ownership; conflicts trigger failure and controlled helping [3]. Single-word load-linked/store-conditional [4] coordinates these steps, and the guarantee is non-blocking system progress [5], not that every transaction always succeeds.

## Illustrative example

**Transaction.** Two locations store balances 11 and 4. A transaction transfers 3 from the first to the second, producing 8 and 7. Its data set is the two addresses, fixed before execution, and its transition function is deterministic. Assume sufficient funds and that all accesses use the transactional interface.

**Acquire.** Process A initializes and publishes a stable descriptor, then acquires the lower-addressed location. It pauses before acquiring the second. A private lock-based implementation would leave another process unable to complete a conflicting transaction without A returning.

**Help.** Process B encounters A's ownership while trying to acquire a conflicting location. B marks its own attempt failed and releases any ownership already acquired. As an initiator, it can then help A using A's stable descriptor and instance version.

Helping attempts the remaining ownership acquisition and completes A's transaction if successful. The shared descriptor coordinates the old values, status, update completion, and release so helpers cannot apply the transfer twice or write through a stale descriptor after locations have been released.

**Retry.** B can retry its own transaction after helping. If its attempt fails again, this does not contradict the progress guarantee: continued activity ensures some transaction succeeds, not necessarily B's. A helper that itself encounters a conflict does not recursively begin an unbounded chain of helping; the algorithm distinguishes helper calls from initiator calls.

**Scope.** Transactional clients observe the transfer as one operation with respect to the sequential specification. A raw uninstrumented reader between physical writes is outside that contract. A traversal that discovers new addresses while executing is also outside the static-transaction interface; the paper separately explains how to use static operations in a broader sequential-to-concurrent transformation.

## Concepts and terms

**[1] Static transaction.** A transaction with a predetermined data set and a transition function depending only on those locations. Locations outside the set are unchanged.

**[2] Transaction descriptor.** A shared record describing a particular attempt, including its locations, status, old values, completion information, and version. Stable publication lets helpers use a coherent description.

**[3] Helping.** Completing another process's transaction on its behalf. The algorithm releases the current attempt's ownership before helping and avoids recursive helper chains.

**[4] Load-linked/store-conditional.** A pair of single-location primitives: load-linked records an observation, and store-conditional succeeds only if the relevant intervening modification condition has not invalidated it.

**[5] Non-blocking progress.** If processes continue attempting transactions, some operation succeeds in finitely many system steps. Individual operations may repeatedly fail; wait-freedom would require a stronger per-operation guarantee.


# On optimistic methods for concurrency control

**Summary by:** GPT 6 Astra

**Author:** H. T. Kung and John T. Robinson

**Source:** ACM Transactions on Database Systems 6(2), 1981; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/319566.319567

## Key insight

When conflicting transactions are uncommon, let transactions work on private updates and check their compatibility before publishing. Avoiding long-held locks trades waiting for the possibility of aborting and repeating work.

## Basic idea

An optimistic transaction [1] has a read phase, a validation phase, and, if validation succeeds, a write phase. Reads record a read set [2], while modifications remain private in a write set [3]. Validation chooses a serial order [4] and checks whether overlapping transactions' accesses are compatible with that order. Failed validation discards private changes and retries; successful validation authorizes publication under synchronization that prevents a conflicting commit from slipping through the check.

## Illustrative example

**Read.** A database contains `seats = 4` and `price = 10`. Transaction A reads `seats` and privately prepares `seats = 3`. B reads `seats` and `price`, then privately prepares `price = 11`. Their read sets are `{seats}` and `{seats, price}`; their write sets are `{seats}` and `{price}`. Neither private update is visible yet.

**Validate in a simple serial-validation implementation.** Maintain a commit counter and completed transactions' write sets. Each transaction records the counter at the start of its read phase. Protect the final validation and publication step with one short critical section, so publication is not concurrent with another transaction's final validation.

A enters first, finds no conflicting transaction committed during its read phase, publishes `seats = 3`, and records its write set. B then examines transactions committed since B began. A wrote `seats`, which B read. B must abort even though A's and B's write sets do not overlap: B's proposed computation depended on data invalidated by the required serial order.

**Retry.** B discards its private state, reads `seats = 3` and `price = 10`, and recomputes. If nothing conflicting commits during that read phase, B validates and publishes its new price. The resulting execution is equivalent to running A before the successful attempt of B.

The paper also gives more concurrent validation schemes. Its general conditions distinguish transactions that finished before a read began, transactions whose write phase ends before the later write phase, and transactions whose writes overlap. In the last case, both read/write and write/write intersections need attention. The simplified example deliberately serializes final validation and writing instead of pretending one intersection test covers every scheduling scheme.

## Concepts and terms

**[1] Optimistic transaction.** A transaction that performs its main computation without reserving every accessed object against competitors, then aborts if its observed execution cannot be safely committed. Repeated conflicts can cause repeated aborts or starvation.

**[2] Read set.** The objects whose values a transaction consulted. Correct tracking must include every dependency relevant to the database operation, not just fields convenient to record.

**[3] Write set.** The objects the transaction intends to modify, with tentative replacement values kept separate from shared state until publication.

**[4] Serial order.** An ordering of whole committed transactions whose effects and reads agree with the concurrent execution. Validation establishes this equivalence; individual operations need not have run sequentially in real time.

# Transactional Memory: Architectural Support for Lock-Free Data Structures

**Summary by:** GPT 6 Astra

**Author:** Maurice Herlihy and J. Eliot B. Moss

**Source:** ISCA 1993; SIGOPS Hall of Fame Award 2015; Dijkstra Prize in Distributed Computing 2012

**Link:** https://doi.org/10.1145/165123.165164

## Key insight

Cache-coherence mechanisms can support speculative operations on several memory locations and make their changes visible together. This permits short shared-data updates without leaving a lock held by a stalled process.

## Basic idea

Transactional memory [1] adds transactional loads and stores that track a read set and write set [2]. Stores remain tentative until a commit operation succeeds; conflicting accesses or implementation limits can abort the transaction. A validation instruction [3] lets software detect an aborted, potentially inconsistent speculative read before relying on it. The proposed transactional cache [4] extends coherence machinery to track ownership and discard tentative updates, targeting short critical sections rather than arbitrarily large computations.

## Illustrative example

**Read speculatively.** A bounded queue uses two shared locations: `tail`, containing the next insertion position, and `slot[tail]`, which receives the new value. In a simplified insertion with capacity already guaranteed, a thread transactionally loads `tail = 3`, checks that the speculative read remains valid, tentatively stores `item` into slot 3, and tentatively stores 4 into `tail`.

**Compete.** Another thread attempts an insertion using the same tail. The cache-coherence extension detects conflicting transactional access. Depending on the conflict-resolution policy, an attempt aborts and its tentative writes are discarded. It cannot expose `tail = 4` while leaving slot 3 unpublished as part of a successful transaction.

**Commit or retry.** A successful commit makes both updates take effect atomically in a serialization order. An unsuccessful commit tells the thread to reread the tail and repeat the operation. A correct full queue algorithm must also handle capacity, consumers, and reclamation; the two-location example isolates the transaction mechanism rather than claiming to implement that complete queue.

**Validate before unsafe use.** If the loaded value were a pointer into a linked structure, a concurrent update might invalidate the speculative traversal. The paper's `VALIDATE` operation detects whether the transaction has already aborted before software uses read values in a way requiring consistency. Validation is not a promise that the eventual commit will succeed; a later conflict can still abort it.

A transaction can also abort because its data exceeds hardware capacity or because of an interrupt or context switch. Software needs an appropriate retry strategy, and the mechanism alone does not guarantee that every thread eventually commits. The paper leaves general interaction between transactional and nontransactional accesses to the same locations unspecified, so this example assumes participating accesses follow the transactional protocol.

## Concepts and terms

**[1] Transactional memory.** Memory operations grouped into a transaction whose committed changes appear together and whose committed executions are serializable. Aborting removes its tentative memory changes.

**[2] Read set and write set.** Locations read transactionally and locations accessed for transactional writing. The paper's exclusive transactional load places its location in the write set even before a store.

**[3] Validation instruction.** A test of whether the active transaction has remained valid. Failure discards its tentative updates; success establishes consistency of the preceding speculative reads without preventing later abort.

**[4] Transactional cache.** Hardware storage and coherence state for speculative data. Tentative writes remain local until commit and can be discarded on abort; finite cache resources limit the transactions it can retain.

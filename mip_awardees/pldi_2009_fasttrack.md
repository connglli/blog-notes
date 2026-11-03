# FastTrack: Efficient and Precise Dynamic Race Detection

**Summary by:** GPT 6 Astra

**Author:** Cormac Flanagan, Stephen N. Freund

**Source:** PLDI 2009; SIGPLAN Most Influential PLDI Paper Award, 2019

**Link:** https://doi.org/10.1145/1542476.1542490

**Code:** [RoadRunner and FastTrack](https://github.com/stephenfreund/RoadRunner)

## Key insight

For a race-free prefix, writes to one location are ordered, so recording only the latest write's thread and clock is sufficient. Multiple unordered readers require a richer representation.

## Basic idea

FastTrack detects data races [1] using the happens-before relation [2]. Threads maintain vector clocks [3], but most memory locations record compact epochs [4] for their latest accesses. Read metadata expands to a vector when unordered readers must be remembered, preserving precision while making common access checks constant time. The guarantee concerns races in the observed execution, not every execution the program might take.

## Illustrative example

**Ordered access.** Thread A writes `x` at its local clock 5, so store write epoch `5@A`. After releasing a lock, A's clock is communicated through that lock. Thread B acquires it and has vector clock entries including `B[A] = 5`. Its read checks `5 <= B[A]`, so the write is ordered before the read.

**Unordered readers.** Suppose B reads at epoch `7@B`, and another thread C also reads `x` without learning B's clock. The two reads do not race because neither writes. However, replacing the read record by C's epoch would forget B. Promote the read metadata to a vector containing both `7@B` and C's read epoch, say `4@C`.

**Later write.** A writer D must satisfy the last-write check and every recorded reader's clock requirement. If `D[B] = 7` but `D[C] = 3`, the check against `4@C` fails: C's read and D's write are unordered and conflict. If D has learned both clocks, the write is safe and the old read information can be cleared for subsequent accesses.

The clock values describe synchronization knowledge, not wall-clock time. Seeing C's read earlier in a log does not itself make that read happen-before D's write.

## Concepts and terms

**[1] Data race.** Conflicting accesses to one location, at least one a write, not ordered by the modeled synchronization relation.

**[2] Happens-before.** The transitive relation induced by per-thread order and synchronization such as lock release/acquire and thread fork/join.

**[3] Vector clock.** One logical-time component per thread. Joining synchronization histories takes componentwise maxima; comparison is componentwise.

**[4] Epoch.** A pair `clock@thread`; checking it against a vector requires only that thread's component.

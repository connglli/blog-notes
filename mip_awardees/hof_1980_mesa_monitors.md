# Experience with Processes and Monitors in Mesa

**Summary by:** GPT 6 Astra

**Author:** Butler W. Lampson and David D. Redell

**Source:** SOSP 1979; Communications of the ACM 23(2), 1980; SIGOPS Hall of Fame Award 2009

**Link:** https://doi.org/10.1145/358818.358824

## Key insight

Notification need not immediately transfer execution to a waiting process. Treating it as a hint simplifies scheduling, provided a waiter reacquires the monitor lock and rechecks its actual condition before proceeding.

## Basic idea

Mesa combines concurrent processes [1] with monitors [2] protecting shared data. A process unable to proceed waits on a condition variable [3], releasing the monitor lock and reacquiring it before returning from the wait. A notification makes a waiter eligible to run later, so it does not guarantee that the desired condition still holds when the waiter resumes. The program preserves a monitor invariant [4] before releasing the lock and tests its waiting predicate in a loop. Timeouts, aborts, and nested calls require the same explicit reasoning about locks and restored invariants.

## Illustrative example

**Protect a buffer.** Two consumer processes A and B share a one-item buffer with a producer. The monitor invariant is that the buffer contains either zero or one item, with its occupancy flag agreeing with the stored state. A consumer holds the monitor lock while inspecting or changing that state.

**Wait.** A finds the buffer empty and waits on `not_empty`. The wait releases the lock, allowing the producer to enter. The producer inserts item X, restores the invariant, notifies `not_empty`, and exits. Notification does not hand the lock directly to A.

**Race with another consumer.** Before A reacquires the lock, B enters and removes X. A eventually resumes with the lock but finds the buffer empty again. It must wait again. Code equivalent to `while empty: wait(not_empty)` is correct; checking `empty` only once before waiting would let A incorrectly remove a nonexistent item.

The producer's notification concerns a possible change, while the protected state is the authority on whether A may proceed. A timeout or another wakeup likewise sends A back to the predicate test rather than proving that an item exists.

**Keep nested locks explicit.** If code inside monitor M calls another monitor N and waits there, the wait releases N's lock, not automatically M's. Holding M while waiting for another process that needs M can deadlock. The program must choose a call structure that avoids this dependency or restore M's invariant and explicitly leave its critical region before the blocking interaction.

This design establishes safe access when the lock and predicate rules are obeyed. It does not promise fairness or guarantee that every eligible waiter runs promptly. Resource-selection policies, such as which consumer receives a limited resource, need application-level scheduling rather than an assumption that monitor acquisition order is fair.

## Concepts and terms

**[1] Process.** A concurrently executing control path. Mesa integrates process creation and completion with its procedure and type mechanisms, rather than treating a process as merely a label on a lock.

**[2] Monitor.** A module whose entry procedures execute with mutual exclusion over its protected state. Internal operations can temporarily violate the invariant only while exclusion prevents another entrant from observing that state.

**[3] Condition variable.** A place for processes to wait for changes relevant to a predicate. It does not store the predicate's truth or reserve a resource for a notified process.

**[4] Monitor invariant.** A property established before exit or wait and assumed after entering or reacquiring the lock. A particular resource-availability predicate may be stronger and must be tested separately.

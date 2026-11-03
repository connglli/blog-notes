# The Implementation of the Cilk-5 Multithreaded Language

**Summary by:** GPT 6 Astra

**Author:** Matteo Frigo, Charles E. Leiserson, Keith H. Randall

**Source:** PLDI 1998; SIGPLAN Most Influential PLDI Paper Award, 2008

**Link:** https://doi.org/10.1145/277652.277725

## Key insight

Make ordinary local execution cheap, even if handing work to another processor becomes more expensive: local execution happens much more often than stealing.

## Basic idea

Cilk-5 applies the work-first principle [1] to fork-join programs [2]. Each worker executes locally from one end of a deque [3], while idle workers steal older work from the other end. Two procedure clones [4] separate cheap serial-style execution from the bookkeeping needed after a steal. The scheduler exploits available parallelism; it does not make dependencies disappear or promise linear speedup for every program.

## Illustrative example

**Computation.** Sum an eight-element array by splitting it into two four-element halves. Spawn computation of the left half, compute the right half, synchronize, and add the two results. Repeat recursively until a subarray is small enough for sequential summation. Assume the input is immutable and partial sums use separate storage.

**One worker.** At a spawn, save the parent's continuation and execute the child like an ordinary call. If no one steals the parent, the child returns and the parent continues locally. By the time the parent reaches synchronization, its spawned work has finished in this serial execution, so the fast clone needs no waiting protocol there.

**Two workers.** While worker A descends into the left half, idle worker B steals the older parent continuation from the opposite end of A's deque. B resumes it through the slow clone and computes the right half. The slow clone records that the left result may still be outstanding and waits or suspends appropriately at synchronization. When both results exist, combine them once.

**Cost.** Splitting into too many tiny tasks still costs frame allocation and deque operations. Work-first design minimizes those costs along the frequent local path while allowing more work during theft and cross-worker return. A deeply sequential dependency chain limits parallel speedup regardless of how many idle workers attempt to steal.

## Concepts and terms

**[1] Work-first principle.** Prioritize reducing overhead added to total one-processor work; scheduling theory motivates shifting less frequent overhead toward the critical path.

**[2] Fork-join program.** A computation can spawn children and later synchronize before using their results.

**[3] Deque.** A double-ended queue: the owner uses a stack-like end, while thieves take older exposed work from the other end.

**[4] Procedure clones.** Fast and slow versions of a procedure, with saved frames allowing a stolen continuation to resume with full parallel bookkeeping.

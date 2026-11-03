# DieHard: Probabilistic Memory Safety for Unsafe Languages

**Summary by:** GPT 6 Astra

**Author:** Emery D. Berger, Benjamin G. Zorn

**Source:** PLDI 2006; SIGPLAN Most Influential PLDI Paper Award, 2016

**Link:** https://doi.org/10.1145/1133981.1134000

**Code:** [DieHard](https://github.com/emeryberger/DieHard)

## Key insight

A larger, randomized heap can make a memory error less likely to damage a live object; independently randomized replicas can further reduce shared failures.

## Basic idea

DieHard approximates infinite-heap behavior [1] through overprovisioning [2] and randomized allocation [3]. Objects of a size class are placed among many available slots, reducing predictable adjacency and immediate reuse. An optional replicated execution [4] runs differently randomized copies and compares their outputs. These mechanisms provide probabilistic tolerance, not a proof that invalid accesses are legal or harmless.

## Illustrative example

**Allocation.** Imagine a size class with 16 equally sized slots and only four live objects. Suppose a buggy object overruns by one byte into the immediately following slot. In a simplified model with uniformly distributed other objects and with the following slot inside this class, the probability that this particular neighboring slot contains one of the other three live objects is `3/15 = 1/5`. This calculation illustrates sparsity; it is not the paper's general bound for arbitrary overruns.

**Reuse.** Free an object at slot 6 while a stale pointer remains. A conventional immediate-reuse policy might put the next object there. Random placement distributes future allocations among free slots, reducing the chance of promptly overwriting the stale object's storage. It does not prevent the stale pointer from being used, and enough subsequent allocations can still reuse the slot.

**Replication.** Run three copies with independent heap layouts on the same input. An overrun may corrupt a live object in one copy and land in unused space in another. Comparing externally produced results can detect disagreement and support a correct majority when the required execution assumptions hold. Shared deterministic bugs, correlated errors, or arbitrary external side effects do not disappear merely because three processes exist.

The tradeoff is extra memory and, with replication, extra execution. Increasing the empty space changes failure probabilities; it does not turn C into a memory-safe language.

## Concepts and terms

**[1] Infinite-heap behavior.** An idealized memory model motivating separation and avoidance of harmful reuse; a finite implementation only approximates relevant properties.

**[2] Overprovisioning.** Supplying more heap capacity than the live data requires, creating unused space around allocations.

**[3] Randomized allocation.** Using random choices to select object placement rather than packing objects in a fixed allocation order.

**[4] Replicated execution.** Multiple executions with diversified layouts and compared outputs, requiring compatible inputs and handling of nondeterminism.

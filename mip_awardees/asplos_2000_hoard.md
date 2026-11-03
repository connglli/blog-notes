# Hoard: A Scalable Memory Allocator for Multithreaded Applications

**Summary by:** GPT 6 Astra

**Author:** Emery D. Berger, Kathryn S. McKinley, Robert D. Blumofe, Paul R. Wilson

**Source:** ASPLOS 2000; ASPLOS Influential Paper Award 2019

**Link:** https://doi.org/10.1145/378993.379232

**Code:** [Hoard](https://github.com/emeryberger/Hoard)

## Key insight

Separate heaps reduce allocation contention, but freed memory must not remain stranded in the wrong heap. Hoard combines local allocation with transfers of larger storage units through a global heap, controlling both contention and excess memory consumption.

## Basic idea

Hoard organizes objects into size classes and superblocks [1], with per-processor heaps and one global heap. Freeing an object returns it to its owning superblock [2], not simply to the freeing thread's private pool. An emptiness rule [3] moves sufficiently underused superblocks to the global heap for reuse elsewhere. This organization also reduces allocator-induced false sharing [4], without claiming to eliminate all sharing created by an application.

## Illustrative example

**Allocate locally.** Count capacity in equal-sized object slots. Heap `producer` owns two superblocks of four slots each. A producer allocates objects there and passes them to a consumer, which eventually frees them. Those frees update the superblocks owned by `producer`.

**Cross the threshold.** Suppose only two objects remain live, both in one superblock. Use illustrative parameters `f = 1/2`, `K = 1`, and superblock capacity `S = 4`. Total capacity is `a = 8`, live usage is `u = 2`, and free capacity is six. The heap is more than half empty and has more than one superblock's worth of free space, so both transfer conditions hold.

**Recycle globally.** Move the empty superblock to the global heap. The local heap now has capacity four and usage two. A different heap needing storage can obtain that superblock instead of requesting another four slots from the operating system. Returning each freed object only to the consumer's own pool would not provide this ownership-and-rebalancing discipline.

**Preserve locality.** Most allocations use the local heap and favor fuller suitable superblocks. Separate allocating heaps usually use different superblocks, reducing the chance that independent allocations place different threads' writable objects on one cache line. A partially occupied superblock transfer can still leave sharing, so the claim is reduction rather than impossibility.

## Concepts and terms

**[1] Size class and superblock.** Requests are rounded to supported object sizes. A superblock holds multiple objects of one class and tracks free slots. Completely empty superblocks can be reused for another class; large objects have a separate operating-system allocation path.

**[2] Ownership and synchronization.** Each superblock belongs to one heap at a time. A free locates and synchronizes with that owner even when a different thread allocated or frees the object. Per-heap synchronization reduces centralized contention; Hoard is not a lock-free allocator.

**[3] Emptiness rule and memory bound.** Transfer when `u < (1-f)*a` and `u < a-K*S`, choosing a superblock at least fraction `f` empty. This leaves each local heap either sufficiently utilized or within a bounded amount of spare capacity. The memory bound includes per-heap reserve space and allocation granularity; it is not a claim of zero fragmentation or immediate return of every free page to the OS.

**[4] False sharing.** Independent writable objects occupy the same coherence cache line, causing unnecessary invalidations between processors. Allocation placement can create or amplify this effect. Returning frees to their original superblocks and keeping common allocation paths local reduce allocator-induced cases, but application object layouts and sharing patterns remain relevant.

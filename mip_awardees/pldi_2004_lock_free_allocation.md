# Scalable Lock-Free Dynamic Memory Allocation

**Summary by:** GPT 6 Astra

**Author:** Maged M. Michael

**Source:** PLDI 2004; SIGPLAN Most Influential PLDI Paper Award, 2014

**Link:** https://doi.org/10.1145/996841.996848

## Key insight

An allocator must not stop every requesting thread merely because one thread pauses while changing shared allocation metadata.

## Basic idea

The allocator uses lock-free synchronization [1] over processor heaps and size-class superblocks [2]. Allocation first reserves capacity through the active-superblock header, then removes a block by compare-and-swap [3] on its descriptor. Freeing returns a block to its original superblock, with state transitions making partial superblocks reusable and empty ones reclaimable. Version tags address the ABA problem [4] in free-list updates.

## Illustrative example

**Reservation.** Consider one active superblock with four free blocks ordered `2 -> 5 -> 1 -> 7`. Suppose three blocks are available for reservation through its header. Thread A successfully reserves one and then pauses. This reservation promises a block, not specifically block 2.

**Concurrent allocation.** Thread B reserves another block. It reads the descriptor's head 2 and its successor 5, then atomically replaces the descriptor with one whose head is 5 and whose version tag is incremented. B returns block 2. A resumes, reads the updated head, and can remove block 5. B did not wait for A to finish its operation.

**Retry.** If two threads read the same head, only one matching compare-and-swap succeeds. The loser rereads the descriptor and retries. A stale observation must not succeed merely because a block was popped, freed, and became the head again: the tag distinguishes the changed list history, subject to the tag's wraparound assumptions.

**Free.** Freeing block 2 pushes it back onto that superblock's free list and atomically updates counts and state. A superblock with outstanding reservations cannot be treated as empty. An implementation must preserve this distinction and the paper's descriptor-reclamation protocol; replacing a mutex with a bare compare-and-swap on a head pointer is insufficient.

## Concepts and terms

**[1] Lock-free synchronization.** System-wide progress despite a delayed participating thread; it does not promise a fixed completion bound for each individual request.

**[2] Size-class superblock.** A larger memory region subdivided into equal-size allocation blocks, with shared metadata describing availability and ownership.

**[3] Compare-and-swap.** Atomically replace a memory value only if it still equals an expected value.

**[4] ABA problem.** A value changes away from an observed value and back, concealing intervening changes from a comparison that checks only that value.

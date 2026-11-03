# The Multikernel: A New OS Architecture for Scalable Multicore Systems

**Summary by:** GPT 6 Astra

**Author:** Andrew Baumann, Paul Barham, Pierre-Evariste Dagand, Tim Harris, Rebecca Isaacs, Simon Peter, Timothy Roscoe, Adrian Schüpbach, and Akhilesh Singhania

**Source:** SOSP 2009; SIGOPS Hall of Fame Award 2020

**Link:** https://doi.org/10.1145/1629575.1629579

**Code:** [Barrelfish source mirror](https://github.com/BarrelfishOS/barrelfish)

## Key insight

A multicore machine can be managed as a distributed system of cores. Explicit communication and replicated operating-system state expose coordination costs that a shared-memory kernel leaves implicit in cache coherence.

## Basic idea

A multikernel [1] communicates between cores through messages and treats operating-system state as replicated or partitioned rather than globally shared. Barrelfish separates core-local CPU drivers [2] from user-level monitors [3] that coordinate cross-core operations. The communication abstraction permits batching and topology-aware protocols without requiring every core to share one instruction set or one kernel data layout. Applications may still share memory; the architectural restriction concerns how the operating system coordinates its own state.

## Illustrative example

**Setup.** Four cores run parts of an application that mapped virtual page `v` to physical frame `f`. The application removes that mapping and wants to reuse `f`. Each core may retain an old translation in its translation lookaside buffer [4], so changing a page-table entry alone is insufficient.

**Coordinate.** The initiating monitor sends invalidation messages to the monitors responsible for affected cores. Each arranges the local invalidation and acknowledges completion. The initiator must obtain the required acknowledgments before treating the old mapping as unusable everywhere and safely reusing the frame. An acknowledgment that precedes the necessary local protection change would violate this contract.

**Adapt the protocol.** Suppose cores 0 and 1 share one processor package, while cores 2 and 3 share another. Sending every notification separately across the slower package boundary may be wasteful. A topology-aware multicast can send to a representative on the other package, which forwards locally. Batching multiple invalidations can amortize message overhead. These are changes to the communication protocol, not changes to the application's mapping semantics.

**Represent state.** Each core's local kernel structures record its own execution and memory state; monitors maintain the information needed to coordinate ownership and mappings. Sharing a cache-coherent memory channel to transport messages does not turn all those structures into one shared mutable kernel. The channel is an implementation of communication, with explicit send and receive operations.

The example isolates one coordination operation. It does not claim that messaging is always faster than direct shared-memory access. The paper evaluates alternative shootdown protocols and uses hardware knowledge to select efficient communication patterns. Replica consistency requirements depend on the operation: a stale monitoring statistic may be tolerable, while stale permission to access a reassigned page is not.

## Concepts and terms

**[1] Multikernel.** An operating-system structure with explicit inter-core communication, hardware-neutral coordination mechanisms, and replicated state. Replication can be optimized with sharing where that preserves the abstraction.

**[2] CPU driver.** A core-local privileged component handling mechanisms such as scheduling, protection, and low-level communication. It is distinct from a general device driver.

**[3] Monitor.** A user-level component on each core that coordinates system-wide operations with other monitors and manages resources outside the CPU driver's local mechanisms.

**[4] Translation lookaside buffer and shootdown.** A TLB caches virtual-to-physical address translations. A shootdown coordinates removal of obsolete cached translations from processors that might still use them.

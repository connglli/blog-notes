# Safe Memory Reclamation for Dynamic Lock-Free Objects Using Atomic Reads and Writes

**Summary by:** GPT 6 Astra

**Author:** Maged M. Michael

**Source:** PODC 2002; Edsger W. Dijkstra Prize in Distributed Computing, 2022

**Link:** https://doi.org/10.1145/571825.571829

## Key insight

Removing a node from a data structure does not mean another thread has stopped using it; publish the references that must remain safe before validating and dereferencing them.

## Basic idea

Each thread publishes a bounded set of hazard pointers [1]. Before using a removable node, it publishes the pointer and rechecks that the node is still validly reachable. Removed nodes enter a retired list [2] instead of being freed immediately; scans reclaim only nodes absent from the hazard records. The protocol supports lock-free reclamation [3] under its ordering and reference-publication conditions, rather than making arbitrary stale pointers safe.

## Illustrative example

**Read and protect.** A shared stack head points to node R. Thread A reads the head, publishes R in its hazard slot, then rereads the head. Assume sequentially consistent atomic accesses for this example. If the head differs, A clears or updates its hazard and retries without reading R's fields.

**Concurrent removal.** Suppose A's validation succeeds, then B removes R using compare-and-swap. B places R on its retired list. A can still read R's successor while its hazard continuously names R; unlinking has not yet made the storage available for reuse.

**Scan.** After enough retirements, B collects hazard-pointer values. Finding R in A's slot means R must be retained. Another retired node S absent from every hazard slot can be freed if the data structure obeys the publication protocol. Once A finishes and clears its slot, a later scan can reclaim R.

**Critical race.** If B removes R before A publishes its hazard and the head has not returned to that address, A's recheck fails before any dereference. If storage has been reused at the same address, A must treat it as the currently validated node, without carrying forward fields read before protection. Publication alone does not validate reachability. A stalled thread can keep its protected nodes alive, but bounded hazard slots do not require retaining every later retired node. Moving protection between slots introduces additional scan-order requirements beyond this one-slot example.

## Concepts and terms

**[1] Hazard pointer.** A shared announcement, written by its owning thread, that a node may be accessed without another validity check.

**[2] Retired node.** A node removed from the shared structure but retained until no qualifying reader can use it.

**[3] Lock-free reclamation.** Other threads can continue reclamation despite a paused thread, subject to bounded retained hazards; atomic reads/writes here do not eliminate the data structure's own compare-and-swap operations.

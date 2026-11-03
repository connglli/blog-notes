# The Repeat Offender Problem: A Mechanism for Supporting Dynamic-Sized, Lock-Free Data Structures

**Summary by:** GPT 6 Astra

**Author:** Maurice Herlihy, Victor Luchangco, Mark Moir

**Source:** DISC 2002; Edsger W. Dijkstra Prize in Distributed Computing, 2022

**Link:** https://doi.org/10.1007/3-540-36108-1_23

## Key insight

Separate protecting an object from deciding when it can be reclaimed, and preserve responsibility for protected retired objects without making the reclaimer wait for their users.

## Basic idea

The repeat offender interface [1] lets clients post guards [2] before validating that a value remains in use. A liberation operation [3] identifies values safe to release. The Pass The Buck algorithm transfers responsibility for guarded values into per-guard handoff slots [4], which later liberation operations revisit. Its bounded-step liberation procedure avoids waiting for a stalled client, while application-specific validation remains outside the generic mechanism.

## Illustrative example

**Protection.** A stack node Cedar is still linked. Reader A posts a guard naming Cedar and validates that the shared head still names it before dereferencing. Another thread unlinks Cedar and submits it for liberation. Unlinking changes its status from in-use to retiring, not directly to safe-to-free.

**Handoff.** A reclamation worker examines its candidate set `{Cedar, Birch}`. It encounters A's guard for Cedar. Instead of waiting for A or forgetting Cedar, it uses compare-and-swap to place Cedar's reclamation responsibility in that guard's handoff slot. Birch can continue through the remaining checks. Assume no guard protects Birch; it may be returned for freeing.

**Later pass.** A finishes with Cedar and clears its guard. A subsequent liberation operation observes that the guard does not protect the handed-off value, removes it from the handoff slot atomically, and carries it through the remaining checks. If no other protection prevents release, Cedar can be freed.

**Concurrent workers.** A handoff slot also carries a version. Replacing a slot must preserve responsibility for its previous value, rather than overwriting and losing that value. The paper's bounded retry rules address competing workers; an arbitrary unbounded compare-and-swap loop would not inherit its wait-free guarantee. The example shows an uncontended trace, not a replacement for those concurrency rules. Continued liberation calls and the stated progress assumptions are needed for eventual release.

## Concepts and terms

**[1] Repeat offender interface.** Values move between free, in-use (the paper's `injail`), and retiring (`escaping`) states, with protection against premature reuse.

**[2] Guard.** A client's published protection for a value, effective after a suitable validation and while continuously maintained.

**[3] Liberation operation.** An operation accepting retiring candidates and returning values safe to free; wait-free means bounded own steps regardless of other threads' timing.

**[4] Handoff slot.** Versioned shared storage retaining responsibility for a protected candidate so another reclamation pass can continue its processing.

# Hints for Computer System Design

**Summary by:** GPT 6 Astra

**Author:** Butler W. Lampson

**Source:** SOSP 1983; SIGOPS Hall of Fame Award 2005

**Link:** https://doi.org/10.1145/800217.806614

## Key insight

Good system design separates a clear correctness contract from the mechanisms that make the common case fast. An optimization should have an explicit relationship to authoritative state and a safe way to recover when its assumptions fail.

## Basic idea

Lampson presents design heuristics rather than one algorithm or a universally consistent rule set. Recurring themes include simple interfaces [1], hiding implementation decisions [2], separating normal from exceptional cases [3], and avoiding repeated expensive computation through caches and hints [4]. A hint may be wrong, so it must be checked against authoritative information before an irreversible action. These techniques are useful only when their costs, failure behavior, and workload assumptions fit the system being designed.

## Illustrative example

**Define a small interface.** Design a storage service offering `read(object, block)` and `write(object, block, bytes)`. Clients see stable object identifiers and logical block numbers, not the physical placement of blocks. The service can change placement without forcing every client to understand its allocator.

**Represent truth.** Each allocated disk block carries a protected label identifying its owning object and logical position. The design treats those labels and the required data-update protocol as authoritative. A separate index maps `(object, block)` to a likely physical address for fast lookup.

**Use a checked hint.** A request for block 3 of object X consults the index and obtains physical address 90. Before reading or overwriting as X's block, the service checks that address 90's label actually names `(X, 3)`. If it does, the fast path proceeds. If the index is stale, the service uses a slower authoritative search or repair procedure rather than trusting the hint and overwriting someone else's block.

**Cache an expensive result.** Suppose locating all blocks of X requires a costly scan. Cache the resulting index and invalidate or rebuild entries when placement changes. A cache entry intended to be authoritative must remain coherent; a merely advisory entry may be stale only if its use includes a sufficient check. The distinction is part of the contract, not just a choice of name.

**Separate exceptional work.** Most requests use a valid index entry and require a small number of operations. Rare corruption or inconsistency takes a slower recovery path that reconstructs derived state. This is acceptable only if recovery is correct and exceptions remain sufficiently infrequent for the required performance and availability. The design cannot excuse frequent failures by calling them exceptional.

This example adapts the paper's checked-storage-hint idea into a small service. It does not specify a complete crash-consistent storage system: preserving labels and data across partial writes still needs a justified update protocol. Keeping the fast index recoverable does not repair corrupted authoritative data by itself.

## Concepts and terms

**[1] Simple interface.** A small, comprehensible contract exposing the operations clients need. Simplicity must include enough functionality to avoid forcing every client to duplicate hidden mechanisms.

**[2] Hidden implementation decision.** A choice such as physical placement that clients cannot depend on through the interface, leaving room to change the implementation.

**[3] Normal and exceptional cases.** Separate paths optimized for frequent operations and for less common situations requiring more general or expensive handling. Both must satisfy the correctness contract.

**[4] Cache and hint.** A cache saves a computed result for reuse and requires appropriate coherence. A hint is allowed to be wrong, provided its correctness is checked before an unrecoverable action and a valid fallback exists.

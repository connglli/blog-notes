# Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency

**Summary by:** GPT 6 Astra

**Author:** Cary G. Gray and David R. Cheriton

**Source:** SOSP 1989; SIGOPS Hall of Fame Award 2009

**Link:** https://doi.org/10.1145/74850.74870

## Key insight

A server can promise a client that cached data remains valid for a bounded time. When a client disappears, the server waits out that promise rather than waiting forever for an invalidation acknowledgment.

## Basic idea

A lease [1] lets a cache serve reads without contacting the server until a specified deadline. Before a conflicting write, the server obtains approval from every unexpired leaseholder or waits for those leases to expire. A leaseholder approving the write invalidates its cached copy [2]. Short leases limit failure-related blocking but require more renewals, while long leases reduce renewal traffic but prolong conflicts. Clock assumptions [3] and server-recovery rules [4] make this a consistency mechanism, not an ordinary cache timeout that permits stale reads by design.

## Illustrative example

**Read under a promise.** Client A fetches file F and receives a lease with an effective local validity interval of five seconds. Until its conservative local deadline, A can serve reads from its cached copy. The server must honor its corresponding promise for at least that long, accounting for communication delay and clock uncertainty.

**Conflict.** At time two seconds, client B requests a write to F. The server asks A to approve. A invalidates its cached data and replies, allowing the server to perform B's write without waiting for the deadline. A's next read obtains a valid lease and current data rather than using its old bytes.

**Lose contact.** If A is unreachable, the server cannot assume A has stopped reading. It delays B's write until A's outstanding lease must have expired. A must stop serving the cache when its own conservative deadline passes even if it cannot reach the server. After expiration, B's write can proceed without A's acknowledgment.

**Restart the server.** Suppose the server crashes while A's lease remains valid. If it forgets outstanding promises and immediately permits writes, A can return stale data while believing its lease is valid. A safe recovery approach waits long enough for every pre-crash lease to expire before granting conflicting writes; durable information about lease bounds can reduce this waiting where available.

The example assumes writes are persistent at the server and uses the paper's write-through setting. A failed server clock that advances too quickly, or a client clock that advances too slowly, can break the required deadline relationship. A cached copy plus an arbitrary local timer does not satisfy the protocol without this timing contract.

## Concepts and terms

**[1] Lease.** A time-bounded promise that the server will not allow conflicting modification without the holder's approval. Renewal extends that promise only through another valid exchange.

**[2] Invalidation.** Removing the right to use a cached copy as current, whether or not its bytes remain stored locally. A holder must do this before acknowledging a conflicting write.

**[3] Clock assumptions.** Bounds sufficient to ensure a client stops relying on a lease no later than the server stops honoring it. Communication and clock uncertainty reduce the lease's effective usable duration.

**[4] Recovery rule.** A restarted server must respect promises made before its crash, for example by waiting out their maximum possible remaining term. Forgetting them is a consistency failure, not just a performance issue.

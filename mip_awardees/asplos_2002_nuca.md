# An Adaptive, Non-Uniform Cache Structure for Wire-Delay Dominated On-Chip Caches

**Summary by:** GPT 6 Astra

**Author:** Changkyu Kim, Doug Burger, Stephen W. Keckler

**Source:** ASPLOS 2002; ASPLOS Influential Paper Award 2026

**Link:** https://doi.org/10.1145/605397.605420

## Key insight

A large on-chip cache need not make every hit wait for its farthest storage. Treat distance-dependent access time as part of the cache design and move frequently accessed lines toward faster nearby banks.

## Basic idea

A non-uniform cache architecture, or NUCA [1], divides a cache into banks with different access latencies. Dynamic NUCA allows a line to occupy different banks within its bank set [2]. Search policies [3] locate these movable lines, while generational promotion [4] gradually exchanges frequently used lines into nearer banks. The design balances faster hits against the traffic and energy required to search banks and move data.

## Illustrative example

**Place a line.** Consider one bank set with three possible locations, `near`, `middle`, and `far`. Suppose their illustrative unloaded hit latencies are 2, 5, and 9 cycles. Line `key` is in `far`, while less frequently used lines occupy the nearer locations. These numbers describe the example, not the paper's measured configurations.

**Find it.** An incremental search probes nearby locations first and reaches `far` only after earlier failures. A multicast search sends requests toward several candidate banks concurrently, finding a distant hit sooner but using more network and bank resources. A controller-side partial-tag summary can avoid some pointless probes; a partial match still requires a full tag check.

**Promote gradually.** After a hit in `far`, swap `key` with the line in `middle`. After another hit, swap it with the line in `near`. Repeated use therefore moves it closer without shifting every line in the set after each access. The displaced lines remain cached in farther banks.

**Account for costs.** Once `key` is nearby, its hits can avoid the far-bank latency. This is not free: each exchange consumes internal bandwidth, simultaneous requests can contend, and locating an absent line can require eliminating several candidate banks. A workload that rarely reuses moved lines may gain little from promotion.

## Concepts and terms

**[1] NUCA and banks.** A bank is an independently accessible part of the cache. Wire travel and internal communication make distant banks slower. Static NUCA assigns each address a fixed bank; dynamic NUCA additionally permits movement. Nonuniform latency exists within one cache level and is not simply the addition of another cache level.

**[2] Bank set and mapping.** A bank set identifies the candidate banks in which a particular cache line may reside. Mapping determines the logical associativity and the physical locations that participate. Movement stays within compatible locations so lookup and replacement remain well-defined.

**[3] Search and partial tags.** Incremental lookup saves probes; multicast reduces serialized searching; hybrid policies combine them. Smart search stores portions of tags near the controller to rule out candidates or detect misses sooner. Partial tags can produce false candidates, but must not produce a false cache hit without a full comparison.

**[4] Generational promotion.** On a hit, exchange the accessed line with one in the next-nearer bank rather than fully reordering all locations by recency. Hot lines migrate inward over repeated accesses. Replacement and insertion policies must also decide where newly fetched lines enter. Reported speedups depend on the paper's modeled technology, cache organization, and workloads, not just the existence of banking.

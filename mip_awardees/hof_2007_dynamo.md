# Dynamo: Amazon's Highly Available Key-value Store

**Summary by:** GPT 6 Astra

**Author:** Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, Gunavardhan Kakulapati, Avinash Lakshman, Alex Pilchin, Swaminathan Sivasubramanian, Peter Vosshall, and Werner Vogels

**Source:** SOSP 2007; SIGOPS Hall of Fame Award 2017

**Link:** https://doi.org/10.1145/1294261.1294281

## Key insight

Accepting writes during partial failures can be more useful than forcing every update into one immediately consistent history. Version ancestry and application-assisted reconciliation make the resulting conflicts explicit.

## Basic idea

Dynamo assigns keys to replicated nodes using consistent hashing [1] and tracks version ancestry with vector clocks [2]. Reads and writes wait for configurable numbers of responses, using sloppy quorums [3] to substitute reachable nodes for unavailable preferred replicas. Hinted handoff [4] returns those temporary copies when the intended nodes recover. Concurrent versions are returned for reconciliation, while background anti-entropy [5] repairs replicas that missed updates.

## Illustrative example

**Place and write.** A key `packing-list` belongs to preferred replicas A, B, and C. Use replication factor `N = 3` and thresholds `W = 2`, `R = 2`. If A is unreachable, a coordinator can use D as a temporary replica and attach a hint naming A. A write succeeds after the required two acknowledgments, rather than waiting specifically for A.

**Detect concurrent versions.** Two clients read the same list `{coat}` with clock `{B:1}`. One adds `map` through B, yielding `{B:2}`. The other adds `lamp` through C without seeing the first change, yielding `{B:1, C:1}`. Neither clock dominates the other: the first has a greater B counter, while the second has a greater C counter.

A read that encounters both returns both versions and their context. The application chooses `{coat, map, lamp}` and writes it back with context covering both versions. A coordinator then advances its counter, producing a descendant of both. Set union is this example's policy, not a universal reconciliation rule; in a shopping-cart-like application it can restore an item that another client removed.

**Repair placement.** When A becomes reachable, D sends the hinted copy to A and removes its temporary copy after successful transfer. Longer-lived divergence is detected by comparing hashes of key ranges and descending only into differing parts, then transferring inconsistent objects.

**Contract.** `R + W > N` does not by itself make this design linearizable. Sloppy quorums may use different substitute replica sets during a partition, and concurrent updates are explicitly permitted. Applications must understand multiple returned versions. Availability also depends on enough reachable nodes to satisfy the configured threshold; the design is not a promise that every request succeeds under every failure.

## Concepts and terms

**[1] Consistent hashing.** Mapping keys and node positions onto a ring so a key's responsible nodes follow its position. Multiple virtual positions per physical node help distribute load and accommodate different capacities.

**[2] Vector clock.** Per-node counters summarizing version ancestry. One version subsumes another when its counters are componentwise at least as large; incomparable clocks indicate concurrent histories requiring reconciliation.

**[3] Sloppy quorum.** A response threshold over the first suitable reachable nodes in a preference list, rather than a fixed membership set. This favors availability but weakens ordinary fixed-quorum reasoning.

**[4] Hinted handoff.** Temporary storage of a replica on another node, annotated with its intended owner so it can be delivered later.

**[5] Anti-entropy.** Background comparison and repair of replicas. Dynamo uses Merkle trees, whose internal hashes summarize child ranges, to avoid transferring matching data.

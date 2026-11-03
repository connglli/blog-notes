# Chord: A Scalable Peer-to-peer Lookup Service for Internet Applications

**Summary by:** GPT 6 Astra

**Author:** Ion Stoica, Robert Morris, David Karger, M. Frans Kaashoek, and Hari Balakrishnan

**Source:** SIGCOMM 2001; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/383059.383071

**Code:** [Chord project source](https://github.com/sit/dht)

## Key insight

Hashing keys and nodes onto one identifier ring makes ownership simple. A small table of exponentially spaced routing links makes lookup fast without requiring every node to know the entire membership.

## Basic idea

Chord uses consistent hashing [1] to assign each key to its successor [2] on a circular identifier space. Each node maintains a successor pointer for basic routing and a finger table [3] that skips progressively larger portions of the ring. Lookups forward toward the target using known nodes that precede it. Stabilization [4] repairs routing information as membership changes, and successor lists [5] help bypass failures. The lookup service identifies a responsible node; application-level data replication and storage semantics remain separate responsibilities.

## Illustrative example

**Build the ring.** Use a four-bit identifier space, with positions 0 through 15 and nodes at 1, 4, 8, and 12. Key 10 belongs to node 12, the first node at or after 10 clockwise. Key 15 wraps around to node 1.

**Add routing shortcuts.** Node 1's finger entries start at `1 + 1`, `1 + 2`, `1 + 4`, and `1 + 8`, modulo 16. Their successor nodes are respectively 4, 4, 8, and 12. Duplicate entries are allowed because not every position contains a node.

**Look up.** Node 1 seeks key 10. Its closest known finger preceding 10 is node 8, so it forwards there. Node 8 observes that 10 lies after itself and no later than its successor 12, and returns node 12. The answer is an ownership location, not a proof that any particular value is stored durably there.

**Join and repair.** Node 10 joins between 8 and 12. It learns its successor, and stabilization exchanges predecessor/successor information so node 8 eventually points to 10. Key 10's ownership moves to the joining node; higher-level storage must arrange any associated data transfer. Finger entries are refreshed separately, so stale shortcuts may lengthen routes even when the successor structure is correct.

**Failure boundary.** If 12 fails, a predecessor can try the next live entry in its successor list. This does not reconstruct lost application data, and it does not guarantee recovery from every possible partition or arbitrary malformed ring. The paper's logarithmic routing claims assume the randomized identifier distribution and routing/membership conditions used in its analysis. A static ring with correct fingers is much easier to reason about than unrestricted concurrent churn.

## Concepts and terms

**[1] Consistent hashing.** Applying a common hash space to nodes and keys so membership changes move ownership mainly in the affected ring interval.

**[2] Successor.** The first node encountered clockwise at or after an identifier, with wraparound. Successor pointers define the basic ordered ring.

**[3] Finger table.** At node `n`, entry `i` points to the successor of `n + 2^(i-1)` modulo the identifier-space size. These links support logarithmic lookup under the paper's assumptions.

**[4] Stabilization.** Periodic communication that checks successor/predecessor relationships, informs neighbors, and refreshes routing pointers after changes. Convergence depends on the network and failure assumptions.

**[5] Successor list.** Several consecutive successor candidates retained to avoid losing the routing chain when the immediate successor fails.

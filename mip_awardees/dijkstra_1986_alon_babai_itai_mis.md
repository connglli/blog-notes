# A Fast and Simple Randomized Parallel Algorithm for the Maximal Independent Set Problem

**Summary by:** GPT 6 Astra

**Author:** Noga Alon, László Babai, Alon Itai

**Source:** Journal of Algorithms 7(4), 1986; Edsger W. Dijkstra Prize in Distributed Computing, 2016

**Link:** https://doi.org/10.1016/0196-6774%2886%2990019-2

## Key insight

Choose vertices with degree-dependent probabilities, then resolve local conflicts in parallel so each phase removes a substantial expected fraction of the remaining edges.

## Basic idea

The algorithm builds a maximal independent set [1] in phases on a residual graph. Mark each nonisolated vertex of degree d with probability `1/d`; mark isolated vertices unconditionally. For every edge whose endpoints were both marked, independently erase one endpoint's mark, with higher-degree endpoints more likely to lose. Add surviving marked vertices and delete them together with their neighbors; the Las Vegas [2] algorithm has expected polylogarithmic parallel time under the paper's PRAM models [3].

## Illustrative example

**Graph.** A star has center Hub connected to leaves Ash, Birch, and Cedar. The center has degree three and each leaf degree one. Initially the selected set is empty.

**Mark.** Every leaf is marked, while Hub is marked with probability one third. Suppose Hub is marked in this phase. Conflict decisions use this initial mark snapshot, not an order-dependent sequence of already modified marks.

**Resolve.** On each center-leaf edge, erase Hub's mark with probability `3/(3+1)=3/4`, otherwise erase that leaf's mark. Suppose the Hub-Ash edge erases Ash, and the other two edges erase Hub. The surviving marks are Birch and Cedar. They are not adjacent, so both may enter the independent set.

**Remove and finish.** Delete Birch, Cedar, and their neighbor Hub. Ash remains as an isolated vertex and is selected unconditionally in the next phase. The final set contains all three leaves. Every removed unselected vertex had a selected neighbor, proving maximality; surviving selections never share an edge, proving independence.

If Hub had not been marked, all leaves could have been selected immediately. Random choices change the amount of work and the selected set, not the validity requirements. A parallel implementation must represent independent edge erasures consistently: several requests to erase a mark all have the same effect. The paper analyzes expected edge removal, rather than assuming every individual phase removes a fixed fraction deterministically.

## Concepts and terms

**[1] Maximal independent set.** A set of pairwise nonadjacent vertices that cannot be enlarged; maximality is not maximum cardinality.

**[2] Las Vegas algorithm.** Randomness affects running time, while a returned answer satisfies the specified correctness condition.

**[3] PRAM model.** A parallel shared-memory abstraction. Concurrent-read/concurrent-write and exclusive-access variants charge different costs for implementing a phase, so their running-time bounds differ.

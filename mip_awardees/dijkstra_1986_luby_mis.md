# A Simple Parallel Algorithm for the Maximal Independent Set Problem

**Summary by:** GPT 6 Astra

**Author:** Michael Luby

**Source:** STOC 1985; SIAM Journal on Computing 15(4), 1986; Edsger W. Dijkstra Prize in Distributed Computing, 2016

**Link:** https://doi.org/10.1137/0215074

## Key insight

Many nonconflicting vertices can be selected simultaneously by locally comparing random priorities, then removing the vertices already covered by those selections.

## Basic idea

The randomized algorithm builds a maximal independent set [1] in phases. Give each remaining vertex a random priority [2], choose local minima, and delete each chosen vertex together with its neighbors. Repeat on the residual graph [3]. The paper analyzes fast parallel implementations and also develops derandomization; this summary focuses on its simple randomized selection mechanism.

## Illustrative example

**Graph.** Five vertices form the path `A-B-C-D-E`. An independent set may contain B and D because they are not adjacent. It is maximal if every excluded vertex has a chosen neighbor; maximal does not mean largest possible.

**Priorities.** Suppose the phase assigns priorities A=8, B=2, C=7, D=5, E=9. These are illustrative draws. B is smaller than both A and C, while D is smaller than C and E. Select B and D simultaneously. Resolve any equal adjacent priorities consistently so two adjacent vertices cannot both win; isolated vertices can be selected immediately.

**Deletion.** Remove B and its neighbors A and C; remove D and its neighbors C and E. The residual graph is empty. The result `{B,D}` is independent and maximal: A, C, and E each touch a chosen vertex. Yet `{A,C,E}` is larger, showing that the requested output is not a maximum independent set.

**Why phases work.** Chosen vertices never conflict within a phase. Removing their neighbors prevents future choices from conflicting with earlier choices. When nothing remains, every unchosen vertex was removed as a neighbor, proving maximality. Randomization is used to obtain rapid progress, not to excuse an incorrect final set. The paper's expected parallel running time depends on the shared-memory machine model; a phase count and a machine instruction count are not interchangeable.

## Concepts and terms

**[1] Maximal independent set.** A set with no internal edge that cannot be enlarged by adding another vertex; it need not have maximum cardinality.

**[2] Random priority.** A randomly chosen ordering key used to break symmetry among adjacent vertices; the paper implements comparisons using a large finite range.

**[3] Residual graph.** The graph induced by vertices not yet selected or excluded as neighbors of selected vertices.

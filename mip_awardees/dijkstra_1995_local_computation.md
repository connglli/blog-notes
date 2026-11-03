# What Can Be Computed Locally?

**Summary by:** GPT 6 Astra

**Author:** Moni Naor, Larry Stockmeyer

**Source:** STOC 1993; SIAM Journal on Computing 24(6), 1995; Edsger W. Dijkstra Prize in Distributed Computing, 2025

**Link:** https://doi.org/10.1137/S0097539793254571

## Key insight

Being able to check a solution locally does not imply being able to construct it locally; nevertheless, constant-time construction has a finite structural form that can be studied systematically.

## Basic idea

The paper studies locally checkable labelings [1] on bounded-degree networks with unique identifiers. A local algorithm [2] runs in a number of rounds independent of network size. If such an algorithm exists, an order-invariant [3] one exists, enabling finite searches for a fixed time bound. Deciding whether some constant time bound works is nevertheless undecidable in general, and the paper also identifies nontrivial locally solvable tasks.

## Illustrative example

**Local check.** Consider assigning three colors to a cycle so adjacent vertices differ. Once colors are supplied, each node checks the condition by inspecting its two neighbors. That makes the task locally checkable, but says nothing about how the colors are chosen.

**One-round rule.** Suppose a deterministic rule sees an oriented triple `(left ID, own ID, right ID)`. For an order-invariant rule there are only six relative-order patterns, regardless of how large the identifiers are. For example, `(2,7,11)` and `(100,300,900)` must receive the same output because both are increasing triples.

**Conflict.** Place four increasing identifiers consecutively on a sufficiently long cycle. The two middle nodes each see an increasing triple. Any order-invariant one-round rule assigns them the same color, violating the edge between them. This refutes such a rule without listing all numeric identifiers or every possible program implementing it.

**Finite search and limits.** More generally, for fixed degree, time, and finite label alphabet, enumerate bounded neighborhood shapes and relative identifier orders, assign candidate outputs, and test compatibility on the neighborhoods needed by the checker. The order-invariance theorem justifies considering such finite rules when studying fixed-time solvability. Searching progressively larger time bounds does not decide that no constant-time rule exists: it may continue forever. The undecidability result concerns that unbounded existence question, not failure to check one proposed labeling.

## Concepts and terms

**[1] Locally checkable labeling.** A problem with finite input/output alphabets whose validity is determined by fixed-radius neighborhood constraints on bounded-degree graphs.

**[2] Local algorithm.** A distributed algorithm whose communication radius is bounded by a constant independent of the number of nodes.

**[3] Order invariance.** Outputs depend on relative ordering of identifiers in a view, not their particular numeric values; relabeling while preserving order leaves the output unchanged.

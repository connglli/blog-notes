# CCS Expressions, Finite State Processes, and Three Problems of Equivalence

**Summary by:** GPT 6 Astra

**Author:** Paris C. Kanellakis, Scott A. Smolka

**Source:** PODC 1983 conference version; extended in Information and Computation 86(1), 1990; Edsger W. Dijkstra Prize in Distributed Computing, 2021

**Link:** https://doi.org/10.1145/800221.806724

## Key insight

Preserving a process's branching behavior gives an equivalence that is more discriminating than equality of possible action sequences, yet can be checked in polynomial time on explicit finite-state graphs.

## Basic idea

The paper studies equivalence of finite-state processes described using CCS, a language for communicating processes, and represented as labeled transition systems [1]. Bisimulation [2] requires matching each step in both directions while retaining the same relation between the resulting states. Repeated partition refinement [3] computes this equivalence without enumerating complete executions. Trace equivalence [4] forgets when choices occur and has a harder worst-case decision problem for nondeterministic finite-state processes. Weak bisimulation [5] hides internal actions and can also be checked in polynomial time by constructing suitable transitions before comparison.

## Illustrative example

**Describe two machines.** A beverage machine accepts a coin, then lets its customer select tea or coffee, or cancel and return to the initial state. A second machine nondeterministically selects tea-only or coffee-only service while accepting the coin; either state also permits cancellation. Both reach a terminal state after serving a drink. All states are equally accepting: observations concern possible actions, not separate acceptance labels. Their visible traces coincide, including any number of coin/cancel pairs followed by a successful purchase.

**Refine states.** Form the disjoint union of the two state graphs and initially put all states in one block. Split states whenever their outgoing transitions reach different sets of blocks for some action. Terminal states separate from active states. The tea-only state, coffee-only state, and first machine's choice state separate because their enabled drink actions differ. In the next refinement, the machines' initial states separate: one coin transition reaches the choice block, while the other's coin transitions reach the two restricted-service blocks.

**Interpret the mismatch.** After the second machine selects tea-only service, it cannot match the first machine's coffee step. Equal traces therefore do not imply bisimulation. An implementation can keep recomputing, for each state, the set of pairs `(action, destination block)` until no split occurs; it need not distinguish duplicate transitions to the same block. With appropriate sorting, the paper implements this refinement in `O(nm)` time for a fixed action alphabet, where n and m count explicit states and transitions.

**Hide bookkeeping.** Add an internal logging step before the first machine starts accepting coins. Strong comparison observes this extra step. Weak comparison permits it to be matched by doing no internal work: compute internal-action reachability, and for each visible action include paths consisting of internal steps, that action, and further internal steps. Compare these expanded graphs, also allowing zero or more internal steps as an internal transition.

## Concepts and terms

**[1] Labeled transition system.** States connected by action-labeled directed edges. Complexity measured on this explicit graph need not be polynomial in a compact expression that generates it.

**[2] Bisimulation.** A relation R such that every action step from either related state has a same-action counterpart whose endpoints are again in R.

**[3] Partition refinement.** Repeatedly splitting candidate equivalence classes when their transition behavior disagrees, until the partition is stable.

**[4] Trace equivalence.** Equality of possible visible action sequences, without retaining their branching structure; for nondeterministic finite-state systems its decision problem is PSPACE-complete, meaning complete for polynomial-space computation.

**[5] Weak bisimulation.** Bisimulation abstracting from internal actions, conventionally labeled τ, while matching visible behavior through internal-action closures.

# jStar: Towards Practical Verification for Java

**Summary by:** GPT 6 Astra

**Author:** Dino Distefano, Matthew J. Parkinson

**Source:** OOPSLA 2008; SIGPLAN Most Influential OOPSLA Paper Award, 2018

**Link:** https://doi.org/10.1145/1449764.1449782

## Key insight

Describe an object's state through an abstract predicate whose representation can vary by class, then automate local reasoning about the heap those predicates own.

## Basic idea

jStar combines separation logic [1], abstract predicate families [2], and symbolic execution [3]. Static and dynamic method specifications [4] separate concrete implementation reasoning from contracts usable through dispatch. A theorem prover checks entailments and finds untouched heap portions, while user-supplied abstraction rules summarize symbolic states to infer loop invariants. Automation relies on supplied contracts and sound rules; it does not infer an arbitrary class's intended meaning unaided.

## Illustrative example

**Abstract state.** A client holds a counter `c` described by `Counter(c, n)` and an unrelated buffer described by `Buffer(b)`. The separating conjunction `Counter(c,n) * Buffer(b)` states that their owned memory portions are disjoint. Define a dynamic contract for `increment`: consume `Counter(c,n)` and return `Counter(c,n+1)`, assuming arithmetic remains in range.

**Representations.** One counter class stores a single integer field. Another stores a base plus a delta. Each class supplies its own interpretation of the counter predicate. The client need not know which fields encode n, and a subclass cannot satisfy the contract merely by changing some unrelated field.

**Method proof.** For the single-field implementation, unfold the appropriate predicate to obtain ownership and the current value of the field. Symbolically execute the increment, producing a field containing `n+1`, then fold the predicate back. The buffer is outside the method's required footprint and is carried through unchanged by local reasoning.

**Dispatch and abstraction.** The client uses the dynamic contract regardless of the selected implementation; direct superclass or private calls can use static specifications. If a loop repeatedly manipulates a linked collection of counters, abstraction rules can fold a growing explicit chain into a list predicate. Those rules must preserve all concrete possibilities. An incorrect user rule can make verification unsound, and inability to prove a condition is not itself proof of a concrete bug.

## Concepts and terms

**[1] Separation logic.** A logic for mutable storage; `P * Q` splits owned heap portions between P and Q and supports framing untouched storage.

**[2] Abstract predicate family.** A named state abstraction whose concrete definition is selected by an object's class, hiding representation from clients.

**[3] Symbolic execution.** Execute statements over logical descriptions of possible states instead of individual concrete inputs.

**[4] Static and dynamic specifications.** Contracts for a known implementation versus contracts respected by implementations reached through dynamic dispatch.

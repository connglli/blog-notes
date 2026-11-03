# Iris: Monoids and invariants as an orthogonal basis for concurrent reasoning

**Summary by:** GPT 6 Astra

**Author:** Ralf Jung, David Swasey, Filip Sieczkowski, Kasper Svendsen, Aaron Turon, Lars Birkedal, and Derek Dreyer

**Source:** POPL 2015; SIGPLAN Most Influential POPL Paper Award 2025.

**Link:** https://doi.org/10.1145/2676726.2676980

**Artifact:** [Iris 1.0 Coq formalizations](https://plv.mpi-sws.org/iris/distrib/)

## Key insight

Resource algebras describe which logical permissions can coexist and how they may change; invariants connect those permissions to shared physical state. Combining these ingredients supports concurrent proof rules without making every protocol a primitive of the logic.

## Basic idea

Iris represents ghost state [1] using partial commutative monoids [2] and permits frame-preserving updates [3]. Shared invariants [4] relate that logical state to concrete memory. A thread can open an invariant around an appropriate atomic step, use its resources, and restore it before another thread can observe the state. The paper derives richer protocols and reasoning principles from these ingredients, rather than assuming that every multi-instruction operation is physically atomic.

## Illustrative example

**Resource choice.** Consider an atomic counter and a ghost integer recording its current value. Use an exclusive monoid: its elements are an empty resource and exclusive claims `Own(n)`; combining two nonempty claims is invalid.

Place the concrete counter cell and its matching ghost claim in the shared invariant `exists n. counter -> n * Own(n)`. Initially both record zero. This small example illustrates the framework's mechanism; it is not a complete client specification for a counter library.

**Atomic increment.** A thread opens the invariant for a physical atomic increment. It learns some current `n` and temporarily obtains the cell and `Own(n)`. The instruction updates the cell to `n+1`.

It can also update the ghost claim to `Own(n+1)`. This is frame-preserving because the only resource compatible with an exclusive claim is empty; no other thread can hold a conflicting nonempty fragment of this same ghost resource. Reestablish the existential invariant with witness `n+1` and close it.

**Interference.** A second thread performing the same operation opens an invariant whose witness may have changed. It must reason with the value it actually obtains, not the value it remembers from an earlier operation. Two successful increments therefore preserve agreement between concrete and ghost states at every boundary where the invariant is closed.

Replacing the atomic increment by a load followed later by a store does not justify leaving the invariant open across both steps. Other threads could run between them. Such an implementation needs additional synchronization or a more involved proof.

## Concepts and terms

**[1] Ghost state.** Logical state used only in proofs, with no required runtime representation. Its updates cannot directly change physical memory.

**[2] Partial commutative monoid.** A resource set with an associative, commutative composition operation, a unit, and potentially incompatible combinations. Separating conjunction `P * Q` composes separately owned resources; `counter -> n` means ownership of the counter cell containing `n`.

**[3] Frame-preserving update.** A change to owned ghost resources that remains compatible with every resource the environment could separately own. This prevents a local proof from invalidating other threads' claims.

**[4] Shared invariant.** A proposition maintained around access to shared state. Iris controls when it may be opened and requires restoration; arbitrary nested use or opening across non-atomic execution is not licensed merely because the proposition was initially true.


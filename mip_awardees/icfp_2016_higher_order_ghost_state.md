# Higher-order ghost state

**Summary by:** GPT 6 Astra

**Author:** Ralf Jung, Robbert Krebbers, Lars Birkedal, and Derek Dreyer

**Source:** ICFP 2016; SIGPLAN Most Influential ICFP Paper Award 2026.

**Link:** https://doi.org/10.1145/2951913.2951943

**Code:** [Original Iris 2.0 Coq development](https://gitlab.mpi-sws.org/iris/iris/tree/iris-2.0)

## Key insight

Threads may need to agree on a logical predicate, not merely on a number or address. Ghost state can record predicates themselves if its semantic model controls the resulting self-reference.

## Basic idea

Iris 2.0 extends concurrent separation logic [1] with higher-order ghost state [2], allowing proof-only variables to contain assertions and predicates of the logic. Agreement resources [3] connect separate threads' descriptions of a shared logical choice. CMRAs [4] extend the resource algebra with step-indexed equivalence and validity [5], making this recursive model sound. The later modality [6] guards dependencies, so agreement about a stored predicate initially yields a delayed equality rather than an unrestricted immediate equality.

## Illustrative example

**Setup.** Two workers wait while an initializer prepares cells `left` and `right`. Their specifications preserve resources described by the same client-selected predicate `R(address)`. The interface accepts logical predicates, not merely numeric tags.

For a concrete instance, choose `R(address) = address -> 9`, initialize both cells to 9, and signal readiness. Synchronization transfers each cell's ownership to its worker. For this instance, workers read their cells and return ownership unchanged. Here `address -> 9` owns that cell containing 9, and `P * Q` combines separately owned resources.

**Record the choice.** Before the predicate is chosen, allocate a pending one-shot ghost name `gamma`. The initializer assigns `R` to it once. Its initialized agreement assertion, written here as `Saved(gamma, R)`, can be duplicated and sent with each worker's resource.

Each worker can therefore return a package of the form `exists Q. Saved(gamma, Q) * Q(cell)`. Without the common ghost name, the two returned existential packages could contain unrelated predicates. Knowing only that each cell satisfies some predicate does not recover the client's shared choice.

**Rejoin.** Opening the returned packages exposes predicates `Q1` and `Q2`. Agreement at the same ghost name yields `later(Q1 = Q2)`. The physical computation step that joins the workers permits the proof to use this delayed equality and recover one common predicate for both cells. For the concrete instance, their combined ownership describes two distinct cells containing 9.

The saved assertion identifies the predicate; it does not establish that predicate. Recording `R` without owning either cell cannot manufacture the permissions transferred to the workers.

**Semantic check.** Composition must preserve finite-step equivalence: predicates indistinguishable for the available steps cannot yield immediately distinguishable resources. CMRA validity checks agreement at that index. Later guards recursive dependencies between assertions and resources. These are proof-model conditions, not runtime comparisons of arbitrary predicates.

## Concepts and terms

**[1] Concurrent separation logic.** A program logic tracking ownership of resources so threads can reason locally and transfer permissions through synchronization. Separating conjunction composes ownership according to its resource algebra.

**[2] Higher-order ghost state.** Proof-only state containing logical assertions or predicates, which may themselves mention ghost ownership. A one-shot instance can be initialized once and then retain persistent agreement about its value.

**[3] Agreement resource.** A shareable logical resource whose compatible copies must describe the same stored value, at the precision allowed by the model. Duplicating this knowledge does not duplicate the resources described by that value.

**[4] CMRA.** An algebra with resource composition, a core describing duplicable information, and indexed validity. Its operations respect the model's indexed equivalence and support consistent decomposition and combination.

**[5] Step-indexed equivalence and validity.** Logical approximations parameterized by a natural number of computation steps. Agreement or validity at a larger index implies the corresponding lower-index condition.

**[6] Later modality.** An assertion interpreted with one fewer available step, trivially true at index zero. It guards recursive definitions and can be discharged by the relevant program-step proof rules, not by an unrestricted logical implication.

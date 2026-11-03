# Dependent types and multi-monadic effects in F*

**Summary by:** GPT 6 Astra

**Author:** Nikhil Swamy, Cătălin Hriţcu, Chantal Keller, Aseem Rastogi, Antoine Delignat-Lavaud, Simon Forest, Karthikeyan Bhargavan, Cédric Fournet, Pierre-Yves Strub, Markulf Kohlweiss, Jean-Karim Zinzindohoue, and Santiago Zanella-Béguelin

**Source:** POPL 2016; SIGPLAN Most Influential POPL Paper Award 2026.

**Link:** https://doi.org/10.1145/2837614.2837655

**Code:** [F* implementation](https://github.com/FStarLang/FStar)

**Artifact:** [Paper artifacts](https://fstar-lang.org/papers/mumon/artifacts/)

## Key insight

Dependent types can describe both mathematical proofs and effectful programs if effects remain explicit in their specifications. Effect-specific predicate transformers compose verification conditions while keeping nontermination out of the trusted logical fragment.

## Basic idea

F* combines dependent and refinement types [1] with an effect system [2] for state, exceptions, divergence, and other computations. Each effect receives a Dijkstra-monad specification [3] describing how a desired postcondition determines a precondition. Effect lifts [4] allow computations to compose at a common effect without forcing every pure expression to carry the most complicated specification. Obligations are discharged using SMT solving and explicit proofs, while termination checking [5] protects the total fragment used for logical reasoning.

## Illustrative example

**Stateful computation.** A program reads a valid integer reference `cell`, adds 2 to the value, stores the result, and returns the old value. Work over mathematical integers and a heap containing that reference.

Require the postcondition `cell_final = returned + 2`, with all other cells unchanged. Let the initial heap store 6 at `cell`; execution returns 6 and leaves 8 there.

**Backward calculation.** The write operation substitutes the updated heap into the desired postcondition. Its obligation is that the stored value equals the saved old value plus 2. Pure addition establishes that equality. The read provides the old value and the original heap relationship. Sequencing the three specifications computes a sufficient precondition: the reference must be valid, and the operation must have the required access to it.

The pure addition can be lifted into the state effect as a computation that leaves the heap unchanged. It need not independently manipulate a heap parameter at source level.

**Logical boundary.** To state and prove facts about the result, use total functions. A recursive helper called with a smaller natural number can justify termination by that decreasing argument. An unrestricted recursive function that may run forever belongs to a divergence-permitting effect instead; its result cannot be treated as an inhabitant proving an arbitrary proposition.

If an effectful computation can raise exceptions, its postcondition must account for the exceptional outcome as well as the normal result. Simply composing normal-return equations would omit behavior.

## Concepts and terms

**[1] Dependent and refinement types.** Types may mention values; a refinement restricts values of a base type by a predicate, such as integers satisfying `x >= 0`.

**[2] Effect system.** A classification of computations by permitted behavior, distinct from their result types. It separates total pure reasoning from operations such as mutation and possible divergence.

**[3] Dijkstra-monad specification.** A predicate-transformer interface with return and bind operations. Bind feeds the second computation's required condition backward through the first computation's specification.

**[4] Effect lift.** A mapping that interprets a smaller effect within a larger one while preserving its specification. For example, lifting a pure computation into state records that it does not modify the heap.

**[5] Termination checking.** Establishing that recursive calls decrease in a well-founded order. F* combines semantic reasoning about decreases with automated proof obligations rather than accepting arbitrary recursion in its total logical core.


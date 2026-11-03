# Extended Static Checking for Java

**Summary by:** GPT 6 Astra

**Author:** Cormac Flanagan, K. Rustan M. Leino, Mark Lillibridge, Greg Nelson, James B. Saxe, Raymie Stata

**Source:** PLDI 2002; SIGPLAN Most Influential PLDI Paper Award, 2012

**Link:** https://doi.org/10.1145/512529.512558

## Key insight

Programmer-written contracts let an automatic theorem prover find mistakes beyond ordinary type errors, without requiring a full interactive correctness proof.

## Basic idea

ESC/Java translates annotated Java methods into guarded commands [1] and verification conditions [2]. Method contracts [3] summarize calls, allowing modular checking [4] rather than repeatedly analyzing every callee. Unproved conditions produce warnings about possible runtime errors or contract violations. The paper deliberately accepts some unsound approximations, including bounded loop treatment, so a clean report is not a general proof of correctness.

## Illustrative example

**Contract.** Consider `int read(int[] data, int index) { return data[index]; }`. Its intended precondition is `data != null && 0 <= index && index < data.length`; its postcondition says the result equals the selected element. This example has no loop, mutation, or integer arithmetic requiring an overflow model.

**Method checking.** At entry, assume the precondition. Before the array access, require that the array is non-null and that the index lies within bounds. Those obligations follow directly. Replacing the last precondition comparison by `index <= data.length` admits an invalid boundary case: a two-element array with index two.

**Caller checking.** A caller with a non-null array of length two and index one satisfies the contract. A caller passing index two fails the call-site obligation even if the callee's body is not expanded. After a valid call, the checker uses the callee's postcondition to reason about the returned value.

**Warning interpretation.** A warning can reflect a real error or a contract too weak to establish what the caller needs. Conversely, checking only selected loop unfoldings can miss an error requiring more iterations. Modular proofs also rely on specifications matching implementations. The example demonstrates the contract mechanism without extending its simple proof to every approximation made by the complete checker.

## Concepts and terms

**[1] Guarded command.** A small intermediate language of assignments, assumptions, assertions, and nondeterministic choices used for logical reasoning.

**[2] Verification condition.** A logical formula whose validity implies that the translated command cannot violate the checked assertions under its assumptions.

**[3] Method contract.** Preconditions required from callers, postconditions promised on return, and information about permitted modifications or exceptions.

**[4] Modular checking.** Analyze a method using other methods' contracts, checking the assumptions at each call rather than substituting every implementation.

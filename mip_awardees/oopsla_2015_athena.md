# Finding Deep Compiler Bugs via Guided Stochastic Program Mutation

**Summary by:** GPT 6 Astra

**Author:** Vu Le, Chengnian Sun, Zhendong Su

**Source:** OOPSLA 2015; SIGPLAN Most Influential OOPSLA Paper Award, 2025

**Link:** https://doi.org/10.1145/2814270.2814319

**Code:** [EMI compiler validation project](https://web.cs.ucdavis.edu/~su/emi-project/)

## Key insight

Code that does not execute on selected inputs can still reshape a compiler's analyses and expose miscompilations of the code that does execute.

## Basic idea

Athena generates programs equivalent modulo inputs [1] by inserting and deleting statements in unexecuted regions. Candidate statements come from a corpus and are adapted to the types and variables available at the insertion point. A Markov-chain search [2] favors control-flow diversity while penalizing excessive size [3], enabling sequences of mutations rather than isolated random deletions. Compiled variants must retain the seed's result on the profiling inputs, not on every possible input.

## Illustrative example

**Seed and profile.** A C function initializes `result = 6`, checks whether its input `mode` is nonzero, performs extra arithmetic inside that branch, and returns `result`. Profile only `mode = 0`. The branch body is unexecuted, while the condition and return are executed. Assume the seed's observed execution is well-defined.

**Mutation.** Insert a nested loop and a conditional assignment into the branch body using in-scope integer variables. They may change the result for nonzero modes, but cannot change the selected execution if the surrounding condition and executed code are preserved. Deleting required declarations or changing a live branch condition would not be justified merely because the original body was unexecuted.

**Guidance.** Compare the variant's control-flow nodes and edges with the seed's. A variant introducing genuinely different control structure can receive a better objective value than a cosmetic edit; excessive growth is penalized. The search can probabilistically accept a less favorable intermediate candidate, allowing several changes to combine into a useful later test. This is a search heuristic, not a proof that larger structural distance causes a bug.

**Oracle.** Compile seed and variant with the same compiler configuration and run both at mode zero. A return of 6 for one and 9 for the other violates the expected input-restricted equivalence. Retain and reduce the reproducer, checking validity; passing the test for mode zero establishes nothing about equivalence for mode one.

## Concepts and terms

**[1] Equivalence modulo inputs.** Programs have matching observable behavior for a designated input set, even if they differ elsewhere.

**[2] Markov-chain search.** Repeatedly propose a mutation of the current candidate and probabilistically accept it using an objective-derived preference.

**[3] Control-flow diversity objective.** A score based on differences in graph nodes and edges, with a size penalty to discourage unproductive program growth.

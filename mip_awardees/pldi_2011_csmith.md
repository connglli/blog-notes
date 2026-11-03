# Finding and Understanding Bugs in C Compilers

**Summary by:** GPT 6 Astra

**Author:** Xuejun Yang, Yang Chen, Eric Eide, John Regehr

**Source:** PLDI 2011; SIGPLAN Most Influential PLDI Paper Award, 2021

**Link:** https://doi.org/10.1145/1993498.1993532

**Code:** [Csmith](https://github.com/csmith-project/csmith)

## Key insight

Random programs become useful wrong-code tests only when their executions have a sufficiently well-defined result to compare across compilers.

## Basic idea

Csmith generates random C programs and uses differential testing [1] to compare compiled executions. Incremental pointer and effect analyses [2] reject dangerous constructions, while runtime guards handle operations such as potentially overflowing arithmetic. The generator avoids undefined behavior [3] and result-changing unspecified choices; comparisons still require compatible implementation-defined behavior [4]. Disagreement detects a problem, but agreement is not a correctness proof.

## Illustrative example

**Generation.** Construct a program with an initialized array `unsigned a[3] = {2, 4, 8}`, a pointer to one of its elements, a bounded loop, and a final checksum of its integer state. Choose only nonnegative indices below three. All unsigned arithmetic uses the same integer width on the compared targets.

**Safety checks.** Suppose a generated expression combines reading `a[0]` with a function call that might modify `a[0]`, where evaluation order is not fixed. The effect analysis detects the conflicting read and write and regenerates that expression. A later attempt to store the address of a local variable globally need not be forbidden outright, but dereferencing it after the local variable's lifetime ends must be rejected. Closing a loop requires rechecking facts carried by its back edge, not just checking the first iteration.

**Execution.** Compile the resulting source with compiler A, compiler B, and a different optimization level of A. If the checksums are 14, 14, and 10, retain the source and compiler commands as a candidate miscompilation. Reduce and inspect it before identifying the faulty transformation; majority agreement is useful evidence, not a mathematical oracle.

**Boundary.** Running the same source on targets with different integer widths may legitimately change its output. A comparison must hold the relevant implementation choices fixed. Likewise, a checksum collision or a bug shared by all tested compilers can hide a defect.

## Concepts and terms

**[1] Differential testing.** Compare multiple implementations of the same intended semantics when a separate expected-answer oracle is unavailable.

**[2] Pointer and effect analyses.** Track possible referenced locations and possible reads and writes to those locations.

**[3] Undefined behavior.** An execution outside the language's requirements, making arbitrary outputs unsuitable evidence of wrong code.

**[4] Implementation-defined behavior.** A choice an implementation must document, such as integer widths; it can differ legitimately between targets.

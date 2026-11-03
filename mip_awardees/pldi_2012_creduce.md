# Test-Case Reduction for C Compiler Bugs

**Summary by:** GPT 6 Astra

**Author:** John Regehr, Yang Chen, Pascal Cuoq, Eric Eide, Chucky Ellison, Xuejun Yang

**Source:** PLDI 2012; SIGPLAN Most Influential PLDI Paper Award, 2022

**Link:** https://doi.org/10.1145/2254064.2254104

**Code:** [C-Reduce](https://github.com/csmith-project/creduce)

## Key insight

Shrinking a compiler test needs transformations that understand program structure, and a test that rejects invalid programs as well as programs that lose the bug.

## Basic idea

C-Reduce applies modular reduction passes [1] until they reach a fixed point [2]. An interestingness test [3] decides whether each candidate retains the targeted failure and satisfies the required validity conditions. Accepted candidates replace the current program; rejected candidates are discarded. For wrong-code bugs, undefined behavior [4] must be excluded, because disagreement on an invalid execution is not evidence of miscompilation.

## Illustrative example

**Setup.** Suppose a compiler wrongly removes a necessary unsigned comparison in a program containing `unsigned x = 5;`, an unused helper, a structure used only to hold `x`, and a final printed result. Another compiler prints the expected result. This is a hypothetical fault, not a claim about any particular compiler version.

**Predicate.** A test first checks that the candidate compiles, terminates within a timeout, and passes the chosen validity checks. It then runs both compiled versions and accepts only a disagreement matching the bug under investigation. A compiler crash alone does not satisfy this wrong-code predicate.

**Reduction.** Removing the unused helper keeps the predicate true, so retain the deletion. Replacing the structure field with a scalar also succeeds, enabling later removal of the structure declaration. Deleting `x`'s initializer might make the text smaller but introduce an uninitialized read; reject that candidate even if the executable outputs differ. Replacing the critical comparison by a constant removes the disagreement, so reject that candidate too.

**Iteration.** Run the passes again because one pass can expose an opportunity for another. Stop when a complete round makes no accepted change. The result is small relative to these passes and this acceptance predicate, not a proven globally shortest reproducer. A weak validity checker or an overly broad crash predicate can produce a misleading result even when the reduction loop works correctly.

## Concepts and terms

**[1] Reduction pass.** An iterator over candidate source changes, such as deleting declarations, simplifying expressions, or replacing aggregate storage with scalars.

**[2] Fixed point.** A state where another complete pass round changes nothing.

**[3] Interestingness test.** An executable yes/no criterion defining the property the reduced input must retain.

**[4] Undefined behavior.** An executed operation for which the language imposes no requirements, such as certain invalid memory accesses; output differences then need not indicate compiler defects.

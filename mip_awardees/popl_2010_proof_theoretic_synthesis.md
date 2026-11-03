# From program verification to program synthesis

**Summary by:** GPT 6 Astra

**Author:** Saurabh Srivastava, Sumit Gulwani, and Jeffrey S. Foster

**Source:** POPL 2010; SIGPLAN Most Influential POPL Paper Award 2020.

**Link:** https://doi.org/10.1145/1706299.1706337

**Documentation:** [VS3 project](https://www.microsoft.com/en-us/research/project/vs3-verification-and-specification-using-smt-solvers/)

## Key insight

The unknowns in a verification problem can include the program itself. Solving for statements, guards, invariants, and termination arguments together produces code with a corresponding correctness argument.

## Basic idea

Proof-theoretic synthesis [1] starts with an input-output specification and a resource-constrained program structure [2]. It replaces unspecified assignments, branch conditions, inductive invariants [3], and ranking functions [4] with logical unknowns. Generated constraints enforce partial correctness, termination, and well-formed executable choices. Solving these constraints yields a program within the chosen expression and structural domains; the approach does not search all possible programs without restrictions.

## Illustrative example

**Specification and skeleton.** Given a nonnegative mathematical integer `limit`, return twice its value. Permit two integer variables, `i` and `total`, one loop, addition by constants, and comparisons. Fix both initial values to zero, but leave the loop condition and update constants unknown.

Write the candidate updates as `i := i + a` and `total := total + b`. These are a simplified parameterized skeleton, not a claim about the paper's concrete input syntax.

**Proof constraints.** Choose a candidate invariant `0 <= i <= limit and total = 2*i`. It holds initially. Preserving its equality across the body requires `b = 2*a`. To prevent overshooting the bound and allow exit exactly at `i = limit`, one solution uses `a = 1`, `b = 2`, and guard `i < limit`.

When the guard is false, the invariant implies `i = limit`, hence `total = 2*limit`. For termination, the rank `limit - i` is nonnegative at the loop head and decreases by one on each iteration.

**Extracted program.**

```python
def double_by_addition(limit: int) -> int:
    assert limit >= 0
    i, total = 0, 0
    while i < limit:
        i, total = i + 1, total + 2
    return total
```

For `limit = 3`, the loop states are `(0,0)`, `(1,2)`, `(2,4)`, and `(3,6)`. The invariant holds at each state and the rank runs 3, 2, 1, 0.

The well-formedness constraints matter independently of the arithmetic proof. An unconstrained logical relation might describe valid output pairs without defining an executable update or mutually suitable guards. Synthesis must satisfy the selected programming language and resource limits as well as the postcondition.

## Concepts and terms

**[1] Proof-theoretic synthesis.** Constructing code by solving verification-style constraints in which program fragments and proof components are both unknown.

**[2] Resource-constrained structure.** User-supplied restrictions on control-flow shape, available state, atomic operations, and operation usage. These define the synthesis space.

**[3] Inductive invariant.** A predicate true initially and preserved by every loop-body step taken under the guard. Combined with loop exit, it establishes the result condition.

**[4] Ranking function.** A measure in a well-founded order that strictly decreases on every loop iteration. It rules out infinite execution under the stated precondition.


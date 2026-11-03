# Automatic Predicate Abstraction of C Programs

**Summary by:** GPT 6 Astra

**Author:** Thomas Ball, Rupak Majumdar, Todd Millstein, Sriram K. Rajamani

**Source:** PLDI 2001; SIGPLAN Most Influential PLDI Paper Award, 2011

**Link:** https://doi.org/10.1145/378795.378846

## Key insight

Keep the control structure of a C program while replacing its data with the truth values of selected predicates.

## Basic idea

C2BP constructs a predicate abstraction [1] as a Boolean program [2], including procedures and local variables. For each statement, theorem-prover queries determine how the tracked predicates can change; insufficient information becomes nondeterministic choice [3]. The resulting program overapproximates [4] the modeled concrete executions, so checking it can establish safety while also producing spurious counterexamples. The paper's logical memory model is not a complete account of arbitrary C pointer arithmetic.

## Illustrative example

**Predicates.** Consider mathematical integer variables `x` and `y` and track `p = (x == y)` and `q = (x > 0)`. A call to `copy()` executes `x = y`. Ignore machine overflow in this deliberately restricted example.

**Transfer.** After the call, `p` is certainly true. The new value of `q` asks whether the old `y` was positive. The two predicates do not always answer that question. If old `p` is true, old `q` suffices; when `p` is false, the abstraction may have to permit either Boolean result. Crucially, both updates are computed from the old abstract state, not by letting the first update manufacture information for the second.

**Checking.** An assertion immediately after `copy()` that `x == y` becomes `assert(p)` and succeeds in the abstract program. An assertion that `x > 0` cannot be proved without additional assumptions: a concrete input with negative `y` is a genuine counterexample.

**Lost information.** Suppose the caller had first assigned `y = 3`. Without a predicate describing `y`, abstraction can forget that fact before the call and still permit `q = false`. Add `r = (y > 0)`: the assignment sets `r` true, and `copy()` updates `q` from `r`. The false abstract outcome disappears. This refinement illustrates why predicate selection affects precision; automatic construction for a supplied set is distinct from discovering a sufficient set.

## Concepts and terms

**[1] Predicate abstraction.** Mapping a concrete state to the truth values of finitely many selected logical expressions.

**[2] Boolean program.** A program with Boolean data and ordinary procedural control flow, potentially including an unbounded recursion stack.

**[3] Nondeterministic choice.** The analysis considers every allowed outcome, rather than randomly selecting one execution.

**[4] Overapproximation.** Every modeled concrete execution has a corresponding abstract execution, but the abstract program may admit additional ones.

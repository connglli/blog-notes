# KLEE: Unassisted and Automatic Generation of High-Coverage Tests for Complex Systems Programs

**Summary by:** GPT 6 Astra

**Author:** Cristian Cadar, Daniel Dunbar, and Dawson Engler

**Source:** OSDI 2008; SIGOPS Hall of Fame Award 2018

**Link:** https://www.usenix.org/conference/osdi-08/klee-unassisted-and-automatic-generation-high-coverage-tests-complex-systems

**Code:** [KLEE source](https://github.com/klee/klee)

## Key insight

Symbolic execution becomes useful for real utilities when efficient state representation, solver reuse, search policy, and environment models work together. Solving a feasible path condition produces an executable test rather than merely a report about a symbolic path.

## Basic idea

KLEE interprets LLVM code using symbolic values [1] and maintains a path condition [2] for each execution state. It asks a constraint solver [3] which branch outcomes remain feasible, forks when both are possible, and also checks for errors such as invalid memory accesses. Simplified queries and cached solver results reduce exploration cost. Models of operating-system interactions [4] supply symbolic files and other inputs, and concrete solutions are replayed against native programs to validate discovered behavior.

## Illustrative example

**Setup.** A tiny utility reads one byte from an input file, uses it as unsigned `n`, and returns early if `n > 5`. Otherwise it computes `20 / (n - 2)` using integer arithmetic. The input byte is symbolic, and the environment model records that the read returns one byte successfully.

**Fork.** At the range test, both `n > 5` and `n <= 5` are feasible for an unconstrained byte. KLEE keeps separate states with those conditions. The returning state can yield a test such as `n = 6`. In the other state, the divisor is the expression `n - 2`, not one guessed concrete number.

**Find an error.** Before division, KLEE asks whether `n <= 5` and `n - 2 = 0` can both hold. A solver returns `n = 2`. KLEE records a division-by-zero test and continues the non-error state under `n != 2`, rather than abandoning all remaining inputs after the first bug.

**Reuse work.** If an unrelated input byte has constraints elsewhere, independence analysis can omit those constraints from a query about `n`. A cached satisfying assignment can answer another query when it actually satisfies that query; an unsatisfiable subset proves every superset unsatisfiable. These checks reduce solver work without replacing logical implication with guesswork.

**Replay.** The test describes a real one-byte file containing value 2 and the relevant call behavior. A replay driver recreates that environment and executes the native utility. Disagreement can reveal an inaccurate environment model or a mismatch in execution assumptions. Search may still exhaust its time or memory budget before reaching other paths; high coverage is not a proof of program correctness.

## Concepts and terms

**[1] Symbolic value.** An expression over unknown inputs, constants, and program operations. Concrete values are constant expressions and can often be evaluated directly.

**[2] Path condition.** The conjunction of constraints accumulated by taking a sequence of branch outcomes. It describes which inputs can reach the current state.

**[3] Constraint solver.** A procedure that decides whether the modeled formulas have a satisfying input assignment. KLEE reduces query size and reuses answers because solving commonly dominates execution cost.

**[4] Environment model.** Code describing interactions beyond the analyzed program, such as file reads. Repeated reads must respect a consistent file state, and modeled failures must be represented in replay when relevant.

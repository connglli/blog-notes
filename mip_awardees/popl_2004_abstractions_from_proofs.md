# Abstractions from proofs

**Summary by:** GPT 6 Astra

**Author:** Thomas A. Henzinger, Ranjit Jhala, Rupak Majumdar, and Kenneth L. McMillan

**Source:** POPL 2004; SIGPLAN Most Influential POPL Paper Award 2014.

**Link:** https://doi.org/10.1145/964001.964021

**Code:** [BLAST project and downloads](https://www.sosy-lab.org/~dbeyer/Blast/index-epfl.php)

## Key insight

A proof that an apparent error path is impossible can also identify the facts needed to exclude it. Interpolants isolate these facts at the program locations where they matter.

## Basic idea

Predicate abstraction [1] makes a program finite by retaining selected logical facts, but forgotten relationships can produce spurious error traces [2]. The verifier encodes such a trace as a conjunction of transition constraints and asks whether it is satisfiable. From an unsatisfiability proof it extracts Craig interpolants [3] between trace prefixes and suffixes. These interpolants guide location-specific refinement [4], avoiding both the impossible trace and unnecessary tracking of every discovered predicate everywhere.

## Illustrative example

**Setup.** A small integer program assigns `saved = input`, then `result = saved + 2`, and checks `result == input + 2`. There is no arithmetic overflow in this example. An abstraction that forgets relationships between variables can admit a failing-assertion path.

**Trace formula.** Give assigned values distinct logical names. The error trace requires all three constraints: `saved1 = input0`, `result1 = saved1 + 2`, and `result1 != input0 + 2`. Their conjunction is unsatisfiable.

At the cut after the first assignment, the prefix implies `saved1 = input0`; combining that formula with the suffix yields a contradiction. Both names occur on each side of the cut, so this equality is a valid interpolant there.

At the cut after the second assignment, `result1 = input0 + 2` is an interpolant. It forgets `saved1`, which the remaining failing assertion does not mention. Renamed back to program variables, the useful predicates are `saved = input` at the first location and `result = input + 2` at the second.

**Refinement.** Retain the first predicate while processing the addition and the second while processing the assertion. The abstract transition establishes the second equality, so the error branch becomes impossible.

This single trace does not constitute a whole-program proof when other paths or loops exist. The verifier repeats reachability and refinement until it either excludes all error paths, finds a feasible error trace, or fails to finish. The method does not promise termination on arbitrary programs.

## Concepts and terms

**[1] Predicate abstraction.** Representing concrete states by truth values of chosen predicates. An abstract state denotes all concrete states consistent with those values, so loss of information can introduce extra behaviors.

**[2] Spurious error trace.** An abstract path to failure whose concrete transition constraints have no joint solution. A satisfiable error-trace formula instead supplies a real counterexample within the program model.

**[3] Craig interpolant.** For inconsistent formulas `A` and `B`, a formula `I` such that `A` implies `I`, `I and B` is inconsistent, and `I` uses only vocabulary shared by `A` and `B`.

**[4] Location-specific refinement.** Adding predicates at the control points where they exclude a spurious behavior. A fact needed at one cut can be dropped when its role has been transferred to a different fact.


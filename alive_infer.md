# Alive-Infer: Data-Driven Precondition Inference for Peephole Optimizations in LLVM

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:**

* David Menendez, Santosh Nagarakatte (Rutgers University)<br/>

**Source:** PLDI 2017

**Link:** https://doi.org/10.1145/3062341.3062372<br/>

**Code:** [Alive-NJ](https://github.com/rutgers-apl/alive-nj) (the prototype extends Alive-NJ and is also called PInfer in parts of the paper)

## Key insight

Preconditions for peephole optimizations can be inferred from data: generate positive and negative examples, learn predicates on demand that separate them, and assemble the predicates into a Boolean formula, yielding either a weakest or a succinct partial precondition. For 73 evaluated optimizations, inference finds a weaker precondition than the Alive suite supplies, allowing the rewrite in more cases.

## Basic idea

Peephole optimizations [1] in LLVM are specified in Alive [2] with a precondition that decides when the rewrite may fire; raising that precondition by hand when an optimization is invalid is tedious and forces a trade-off between applicability and succinctness [4]. Alive-Infer removes the precondition and infers it from data: it generates positive and negative examples [5] (a type assignment plus values for the symbolic constants [3]), learns predicates [6] that separate them, and combines the predicates with either a complete Boolean learner that accepts all positive examples or a weighted partial learner that is succinct but may reject some [9]. The loop is counterexample-guided: candidate preconditions are checked with an SMT solver, counterexamples are added as negative examples, and positive examples rejected by a partial precondition are added back to weaken it. Two challenges specific to Alive are handled explicitly: type polymorphism, because examples must cover several type assignments and predicates must be enumerated in a type-correct way, and compile-time undefined behavior [8], because evaluating a precondition such as a division by zero inside the compiler can crash it. On 174 optimizations from the Alive suite that have a supported precondition, Alive-Infer produced weakest preconditions for 133 and partial preconditions for 31 more within a 1000-second timeout, with 73 of the weakest preconditions weaker than the suite's, and it generalized 54 of 71 concrete patterns from the Souper superoptimizer [11].

## Illustrative example: inferring a weaker precondition

**The optimization.** The rewrite removes one of two comparisons of the same runtime value `%v` against symbolic constants `k` and `m`:

```text
%p = icmp eq %v, k
%q = icmp ne %v, m
%r = and %p, %q
=>
%r = icmp eq %v, k
```

The source is true at `%v` exactly when `%v == k` and `%v != m`, and the target keeps the first test. The rewrite is valid for all `%v` exactly when `k != m`: if `k == m`, then at `%v == k` the source is false (because `%v != m` fails) while the target is true.

**Examples and classification.** An example assigns a type and concrete values to `k` and `m`. For a 4-bit integer type, the refinement check [5] with the constants substituted decides the status:

| (k, m) | Status | Check |
| --- | --- | --- |
| (0, 1) | positive | `∀v: (v == 0 && v != 1) == (v == 0)` holds |
| (2, 1) | positive | valid, but rejected by LLVM's stronger precondition `k u< m` |
| (0, 0) | negative | at `v == 0` the source is false and the target is true |
| (3, 3) | negative | the same counterexample at `v == 3` |

Concretely, for (2, 1) the SMT query `∃v ¬((v == 2 && v != 1) == (v == 2))` is unsatisfiable, so the example is positive; for (3, 3) the same query has the model `v = 3`, so the example is negative. Examples come from such SMT models, random values, and the boundary values `{0, 1, -1, minimum signed}`.

**Concrete predicates on the examples.** The enumerator proposes predicates [6] from small to large and evaluates each one on every example; the predicate matrix [7] records accept, reject, or unsafe:

| Predicate | (0, 1) pos | (2, 1) pos | (0, 0) neg | (3, 3) neg |
| --- | --- | --- | --- | --- |
| `k u< m` | accept | reject | reject | reject |
| `k != m` | accept | accept | reject | reject |
| `k == m` | reject | reject | accept | accept |
| `isPowerOf2(k)` | reject | accept | reject | reject |
| `m /u k == 0` | unsafe | accept | unsafe | reject |

`k u< m` rejects the positive (2, 1), and `isPowerOf2(k)` rejects the positive (0, 1), so neither can serve as the whole precondition. `k == m` separates the examples in the opposite direction (it accepts the negatives), so the learner can use its negation. `m /u k == 0` is unsafe [8] on the positive (0, 1) because `k = 0` makes the division undefined at compile time, which disqualifies it; unsafe evaluations are treated as rejections, and a predicate is forbidden from being unsafe on any positive example. `k != m` accepts all positives and rejects all negatives, so it is the separating predicate the learner keeps.

**Validating a candidate.** The Boolean learner [9] turns the separating predicate into the candidate precondition `k != m`, and the SMT validation [5] checks it in two ways. For validity, the query `∃k, m, v ¬(k != m ⇒ ((v == k && v != m) == (v == k)))` is unsatisfiable, so there is no counterexample. For weakness, every valid constant pair satisfies `k != m`, so no non-trivially valid example is rejected, and `k != m` is the weakest precondition. Had the learner emitted `k u< m` instead, the validity check would still pass, but the weakness check would find the positive example (2, 1), a valid case that the candidate rejects; that witness is added back to the positive examples and learning continues.

**Result.** `k != m` is strictly weaker than LLVM's precondition `k u< m`, which loses the valid case `(2, 1)`. For optimizations whose separating condition is more complex, Alive-Infer reports succinct partial preconditions as it finds them and keeps iterating to weaken them.

## Concepts and terms

**[1] Peephole optimization.** A local rewrite that replaces a small instruction pattern with an equivalent one. LLVM's InstCombine and InstructionSimplify passes are peephole optimizers, and the Alive suite used in the evaluation is a snapshot of their optimizations.

**[2] Alive and the refinement check.** Alive is a domain-specific language, similar to LLVM IR, for specifying a peephole optimization as `source => target` plus an optional precondition, together with an SMT-based verifier. For each feasible type, Alive checks `∀R,C: φ ∧ δs ⇒ δt ∧ ιs = ιt`, where `R` and `C` are the runtime variables and symbolic constants, `φ` is the precondition, `δs` and `δt` are the conditions under which the source and target are defined, and `ιs` and `ιt` are the values they compute: whenever the precondition holds and the source is defined, the target must be defined and compute the same value.

**[3] Symbolic constants, runtime variables, and type polymorphism.** Input variables whose values are known at compile time (symbolic constants, constant expressions, parameter types) are distinct from runtime values. Preconditions may mention only the compile-time-known values, and an example fixes both a type assignment and values for the constants. Alive optimizations are polymorphic, so inference samples type assignments and enumerates predicates that respect the type constraints.

**[4] Weakest and partial preconditions.** A weakest precondition accepts every non-trivially valid example in the checked type domain; the source must be defined for at least one runtime input. A partial precondition rejects every negative example but may accept only some positive examples. Strict weakness requires both `φA ⇒ φI` and a witness satisfying `φI ∧ ¬φA`; the witness alone proves only that the inferred condition accepts an additional case. Alive checks feasible type assignments up to an integer-width bound. Implicit assumptions from LLVM's pattern-matching order must also be included when interpreting a condition for an individual optimization.

**[5] Positive and negative examples.** An example is a type assignment plus values for the symbolic constants. It is positive when the optimization is valid for those values (the refinement check succeeds and the target has no compile-time undefined behavior) and negative otherwise. Examples come from three sources: models of SMT queries (a model of the negated refinement condition is a negative example; a model of `∃e. (∃R. δs(e,R)) ∧ (∀R. V(e,R))` supplies a positive example, where e fixes the type and constants and V includes refinement and target compile-time safety), random values, and a Cartesian product of boundary values. Trivial examples whose source is never defined are discarded.

**[6] Predicate enumeration.** Predicates are built from comparisons of constant expressions, constant functions (`abs`, `log2`, `width`), and predicate functions (`isSignBit`, `isPowerOf2`, `isPowerOf2OrZero`). The enumerator is type-directed, emits expressions in normal form to avoid duplicates such as `a + (b + c)` and `(a + b) + c`, and orders predicates by weight, roughly the number of syntax-tree nodes, producing larger predicates only as needed. Bitvector identities are treated with care, since expressions such as `-(a / b)`, `-a / b`, and `a / -b` are distinct. Predicates are enumerated as concrete expressions, not left as holes for the SMT solver to solve. An individual predicate is only evaluated on the examples; validity against the optimization is checked for Boolean combinations of predicates (candidate preconditions), while the solver also generates and classifies examples.

**[7] Predicate matrix and vectors.** A conceptual matrix whose rows are examples and columns are learned predicates; each entry is accept, reject, or unsafe. A predicate vector is the list of results for one example, and many examples can share a vector. A vector is positive if only positive examples have it, negative if only negative examples do, and mixed otherwise. New predicates are learned to split mixed vectors, and when no mixed vector remains a complete precondition is possible.

**[8] Compile-time undefined behavior and safety.** Alive's constant-expression language has partial operations, for example division by zero or signed overflow. A precondition or a target constant expression that evaluates such an operation can crash the compiler, so each term gets a safety condition `σ` that is true exactly when the term is defined. Verification uses `∀R,C: σφ ∧ (φ ⇒ σt ∧ (δs ⇒ δt ∧ ιs = ιt))`: the precondition must always be safe, and target expressions must be safe whenever the precondition holds. Predicates may be unsafe on negative examples, where an unsafe evaluation counts as a rejection, but never on positive examples.

**[9] Boolean formula learning.** Two learners turn predicate vectors into a formula in conjunctive normal form. The complete learner searches for clauses of up to `k` predicates that accept all positive vectors, increasing `k` until every negative vector is rejected by at least one clause, then runs a greedy set cover to drop unnecessary clauses. The partial learner bounds clause size by a parameter `K` (the prototype uses `K = 1`), weights each positive vector by the number of examples it represents, and greedily picks clauses that reject negative vectors while accepting the most positive weight, producing a succinct formula that may reject some positive examples.

**[10] Alive-Search.** A baseline that enumerates preconditions in increasing size and tests validity and weakness. If it finishes, it finds a minimum-size weakest precondition in its search language. For two predicates of sizes `m` and `n`, the paper contrasts whole-formula enumeration of order `c^(m+n)` with the predicate learner's best-case work of order `c^m + c^n`, where `c` describes the enumeration's exponential growth. These are search-space estimates, not bounds on SMT solving time.

**[11] Souper and pattern generalization.** Souper is an LLVM IR superoptimizer that discovers concrete expression patterns. Alive-Infer generalizes a pattern by replacing concrete constants in the source with symbolic constants and inferring a precondition; it produced 51 weakest and 3 partial preconditions out of 71 patterns, with the rest failing because Z3 hung or returned unknown, or because the Boolean learner could not find a formula.

# Hydra: Generalizing Peephole Optimizations with Program Synthesis

**Summary by:** DeepSeek V4.1 Flash, GPT 6 Astra

**Author:** Manasij Mukherjee, John Regehr

**Source:** OOPSLA1 2024, Proceedings of the ACM on Programming Languages 8, article 120, 29 pages

**Link:** https://doi.org/10.1145/3649837

## Key insight

A concrete missed optimization can be generalized by synthesizing its constants and preconditions, with solver checks rejecting unsound candidates. Hydra also checks which integer widths support the resulting rule and generates code for applying it in LLVM.

## Basic idea

Turning one missed peephole optimization [1] into a reusable compiler rule requires separating essential conditions from incidental constants and instruction structure. Hydra accepts a concrete rewrite in compiler intermediate representation (IR) [2], prunes irrelevant parts, and narrows integer widths to reduce solver cost [3]. Program synthesis [4] replaces literals with parameters, expressions, and preconditions, including conditions over dataflow facts [5] that a compiler can establish. Hydra then verifies the rule for feasible width assignments within a configurable bound [6]. Supported rules become C++ pattern matchers and replacements for an LLVM optimization pass.

## Illustrative example

**Setup.** Start with a concrete rule for replacing multiplication by 16 with a left shift by four. Suppose the compiler also knows that `n` is nonzero, a dataflow fact attached to the input rule. The following table rebuilds the paper's multiplication example with our own expression and constants. Each `=>` replaces program code; moving down the table generalizes the rewrite rule itself. Arithmetic wraps to the stated integer width, and `x << k` shifts left by `k` bits, discarding bits beyond that width.

| Phase | Rewrite pattern | How Hydra gets there |
| --- | --- | --- |
| Concrete input, 32 bits | `when n != 0: (n + 7) * 16 => (n + 7) << 4` | Accept an observed optimization with fixed constants, width, and context. |
| Pruned, 32 bits | `x * 16 => x << 4` | Try removing the nonzero condition and replacing `n + 7` with a fresh variable `x`; solver checks show both changes preserve validity. |
| Narrowed, 4 bits | `x * 2 => x << 1` | Assign smaller types and synthesize new constants that keep the same instruction structure valid. |
| Symbolic constants, 4 bits | `x * C => x << D` | Replace the literals with parameters. This candidate is invalid for unrestricted `C` and `D`. |
| Synthesized shift, 4 bits | `x * C => x << log2(C)` | Search expressions in `C` for the right-hand constant `D`. This candidate still needs a precondition. |
| Guarded rule, 4 bits | `when IsPowerOf2(C): x * C => x << log2(C)` | Synthesize and verify a condition that admits the original example and excludes invalid multipliers. |
| Generalized rule, width W | `when IsPowerOf2(C): x * C => x << log2(C)` | Replace the fixed type with a width parameter and verify feasible widths within the configured bound. |

**Finding the expression.** `x` matches a runtime value or expression, while `C` matches a constant in the program being compiled. After narrowing, the constant pair is `C = 2, D = 1`. Hydra's expression search uses that pair as an input-output example; `log2(C)` is a candidate that fits it. Fitting one pair does not prove the rule: `C - 1` fits the same pair too. Hydra must check candidates as rewrites, not merely as functions reproducing the observed constants.

**Finding the condition.** Here `log2(C)` means the base-two logarithm of positive `C`, rounded down. The unguarded candidate fails at four bits for `x = 1, C = 3`: multiplication gives 3, whereas shifting by `log2(3) = 1` gives 2. Hydra uses counterexamples to reject preconditions that admit such cases, then asks the solver to verify surviving conditions. `IsPowerOf2(C)` requires `C` to be nonzero with exactly one set bit, making the shift amount valid and the rewrite correct for every `x` at the checked width.

**Checking widths and applying the rule.** The four-bit proof does not justify a 32-bit rewrite. Hydra separately checks feasible width assignments up to its configured maximum of 64 bits. The generated matcher then recognizes multiplication by a constant, tests the power-of-two condition, computes the shift amount at compilation time, and emits the replacement. It can therefore turn `total * 32` into `total << 5`, even though neither that expression nor that constant appeared in the input rule; a multiplier of 24 fails the condition.

## Concepts and terms

**[1] Peephole rule.** A local rewrite has the form `precondition |= LHS => RHS`: when the condition holds, replace the left-hand instruction pattern with the right-hand pattern. A rule is more general when it applies in more situations. Hydra starts with an optimization opportunity supplied by a developer or a superoptimizer, a tool that searches for cheaper instruction sequences.

**[2] IR semantics and verification.** LLVM IR is a typed representation between source code and machine code; Hydra works through Souper's representation of LLVM computations. Integer values have specified bitwidths. Hydra uses Alive2 and a solver to check refinement: the replacement must not introduce behavior forbidden by the original. This matters for instructions with undefined or poison behavior, which cannot safely be treated as ordinary mathematical operations. Poison is an invalid IR value whose use can invalidate execution.

**[3] Pruning and narrowing.** Pruning greedily removes preconditions, replaces subexpressions with fresh variables, and drops unnecessary instruction restrictions, retaining changes only when verification succeeds. Narrowing assigns smaller types consistent with instruction typing rules and searches for constants that keep the rewrite valid. Counterexamples from failed solver checks guide that search. If narrowing fails, generalization uses the original widths.

**[4] Program synthesis.** Hydra searches expressions assembled from a component set of operators and available constants. One strategy recursively solves equations suggested by the original constant values; another enumerates candidate expressions. Candidate preconditions are filtered using positive and negative examples, verified, and ranked to favor weaker conditions that admit more cases. The search is bounded and may fail or time out; it does not guarantee the most general possible rule.

**[5] Dataflow facts and variables.** Dataflow analysis proves properties of program values without executing them. Known-bits analysis records proven zeros and ones; range analysis records bounds; demanded-bits analysis identifies bits whose values can affect later computation. Hydra also supports single-property facts such as the nonzero condition in the example. Hydra exposes these results as synthesis inputs, such as masks of proven-zero bits, so a rule can test an analysis result rather than require one fixed mask. The proof assumes that the compiler's analysis facts are sound.

**[6] Width checking.** Hydra erases concrete integer types and enumerates assignments that satisfy LLVM's typing rules, up to a configurable maximum of 64 bits in the paper. Rules valid only for some assignments receive width preconditions. An optional faster mode checks only power-of-two widths and records that restriction in the rule. These finite checks do not establish correctness for arbitrary larger integer widths.

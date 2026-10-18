# Provably Correct Peephole Optimizations with Alive

**Summary by:** GPT 6 Astra

**Author:** Nuno P. Lopes, David Menendez, Santosh Nagarakatte, John Regehr

**Source:** PLDI 2015, pages 22-32

**Link:** https://doi.org/10.1145/2737924.2737965

**Code:** [Alive, paper version](https://github.com/nunoplopes/alive/tree/pldi15)

## Key insight

Write a local optimization as a source pattern, a replacement, and a precondition, then use the same specification to check correctness and generate its compiler implementation. Correctness requires refinement, not ordinary equality, because an optimization may make undefined behavior more defined.

## Basic idea

Alive verifies reusable peephole optimization rules [1], unlike a translation validator that checks particular compiler outputs. Its LLVM-like language describes typed source and target templates with symbolic constants and a precondition [2]. For each feasible type assignment, it encodes the instructions as bit-vector formulas and asks an SMT solver [3] whether the target violates refinement [4], including definedness and poison conditions. A failed obligation produces concrete inputs explaining the failure; a verified rule can be translated into C++ pattern-matching and replacement code [5].

## Illustrative example

**The rule.** Shift a word left and then right by the same compile-time amount. The left shift carries `nuw` [6], so losing a nonzero high bit produces poison instead of a wrapped result. This is Alive syntax, which permits omitted types and direct assignments:

```text
Pre: K u< width(%word)
%shifted = shl nuw %word, K
%out = lshr %shifted, K
=>
%out = %word
```

`K` is a symbolic constant, `%word` is a runtime input, and `%out` is the root replaced by the rule. The precondition uses unsigned comparison and requires the shift amount to be less than the word width.

**Encoding.** Fix a width `w` and let `P` mean that shifting `%word` left by `K` loses no nonzero bits. Under the precondition, neither shift has the out-of-range behavior described by the paper. When `P` holds, the source is poison-free and computes `lshr(shl(word, K), K)`; the target computes `word`. For ordinary concrete inputs, the value-mismatch query is `K < w ∧ P ∧ lshr(shl(word, K), K) != word`, with all operations interpreted at width `w`.

**Checking the boundary.** At width 4, `word = 3` and `K = 1` give `0011 -> 0110 -> 0011`. At `word = 8` and `K = 1`, the flagged source produces poison, so replacing its result with the defined value 8 is permitted. Removing `nuw` makes that same input a counterexample: the unflagged shifts give `1000 -> 0000 -> 0000`, but the replacement returns 8. Equality on inputs where the source is poison-free is therefore insufficient unless the verifier also checks whether the transformation introduces poison or undefined behavior.

**Nondeterministic inputs.** With `K = 0` and an `undef` input [7], both sides permit every word value. The check does not require arbitrary choices in the two sides to coincide: it requires every target choice to have a matching source choice.

**Generating the optimizer.** For this rule, generated C++ matches an `lshr` whose operand is a `shl` with `nuw`, checks that both amounts are the same constant and satisfy the precondition, and replaces the outer result with the original word. Cleanup of unused instructions is left to a separate compiler pass. Verification covers the enumerated types, not every possible integer width [8].

## Concepts and terms

**[1] Peephole optimization and SSA.** LLVM's intermediate representation (IR) describes computations using typed instructions. A peephole optimization replaces a small graph of these instructions. In static single assignment (SSA) form, each register name has one definition, and uses point to that definition. A pattern follows these dependencies rather than requiring adjacent lines of code. Instructions whose operands do not depend on each other need not appear in a particular order.

**[2] Templates, constants, and preconditions.** A template describes a family of instruction graphs. Runtime operands vary during execution; symbolic constants vary between matched programs but are known when the compiler applies the rule. A precondition restricts valid matches. Omitted types are inferred from instruction constraints, such as requiring a binary operation's operands and result to have the same width. Both templates name the result being replaced with the same root variable.

**[3] Bit-vector encoding and SMT.** An `iW` integer is a W-bit word, with ordinary addition and multiplication wrapping modulo `2^W`. SMT, satisfiability modulo theories, combines logical constraints with theories such as fixed-width arithmetic. Alive builds expressions for each instruction's value, definedness, and poison-freedom, then asks whether the negation of a correctness obligation is satisfiable. A satisfying assignment is a counterexample; unsatisfiability proves that obligation for the chosen types. A timeout is not a proof.

**[4] Refinement.** Every behavior permitted by the target must be permitted by the source. For concrete inputs satisfying the precondition, Alive checks that a defined, poison-free source is replaced by a defined, poison-free target with the same value. It checks the relevant shared instructions, not just the final root; memory-changing rules also require final-memory agreement. Immediate undefined behavior leaves execution unconstrained, whereas poison is a deferred exceptional value that propagates through dependent operations and can cause undefined behavior when consumed. The summary follows the paper's 2015 model, whose details, including out-of-range shifts, differ from later LLVM semantics.

**[5] Code generation.** The generator walks backward from the source root, emits LLVM pattern-matcher calls that bind operands and constants, checks the precondition, constructs the target instructions, and replaces the root's uses. Type-unification checks prevent a match from creating ill-typed target instructions. The generated matcher and any compiler analyses used by a precondition remain part of the trusted implementation.

**[6] Instruction attributes.** `nuw` requires no unsigned wrap and `nsw` requires no signed wrap; violating the requirement produces poison. `exact` similarly requires selected divisions or right shifts to lose no information. These are semantic conditions, not requests for runtime checks. Alive can also infer attribute assignments by making their presence Boolean unknowns in the correctness queries, seeking fewer requirements on the source and more valid attributes on the target.

**[7] Undef and quantifier order.** `undef` denotes a permitted set of ordinary values rather than one fixed value. The verification conditions quantify target choices universally and source choices existentially: for every input and target choice, some source choice must justify the target behavior. Reversing those quantifiers would check a different contract.

**[8] Scope and trust.** The prototype enumerates integer widths 1 through 64 by default and bounds type nesting; passing those checks is not an unbounded-width theorem. The main language handles straight-line integer and pointer patterns, not general loops or floating-point code. Correctness also depends on the encoded LLVM semantics, the solver, the code generator, and trusted analysis predicates. The paper's evaluation found eight incorrect rules among 334 translated InstCombine transformations; it did not verify LLVM as a whole.

# SMT-Based Translation Validation for Machine Learning Compiler

**Summary by:** GPT 6 Astra

**Author:** Seongwon Bang, Seunghyeon Nam, Inwhan Chun, Ho Young Jhoo, Juneyoung Lee

**Source:** CAV 2022, LNCS 13372, pages 386-407

**Link:** https://doi.org/10.1007/978-3-031-13188-2_19

**Code:** [MLIR-TV](https://github.com/aqjune/mlir-tv), [supplementary material](https://doi.org/10.5281/zenodo.6615676)

## Key insight

Many tensor transformations depend on data movement and algebraic structure, not the exact bits of floating-point arithmetic. Represent values and operations with a finite symbolic abstraction, preserve enough distinctions to expose a counterexample, and add precision only when the coarse check cannot decide the transformation.

## Basic idea

MLIR-TV compares functions before and after high-level MLIR transformations [1], without requiring an explanation from the compiler. It represents tensors as symbolic arrays [2] and floating-point arithmetic through compact value encodings and uninterpreted functions [3], then checks whether the target refines the source [4]. Abstraction refinement [5] exposes more arithmetic structure when validation fails or times out. For reductions whose permitted semantics includes reordering and reassociation, hash constraints [6] encode those laws without expanding every arithmetic operation; accepting such a rewrite is distinct from proving IEEE floating-point equality [7].

## Illustrative example

**The transformation.** Consider a three-element `f32` tensor `A`. In mathematical notation for the tensor operations, the source computes `dot(A, [1, 1, 1])`; the target computes `sum([A[1], sum([A[2], A[0]])])`. The target changes both order and grouping. We first check it under a policy that permits commutative, reassociative reductions, then distinguish that result from strict IEEE arithmetic.

**Coarse encoding.** Model `A` with an SMT array and write its selected values as `a`, `b`, and `c`. Their abstract bit-vectors identify symbolic floating-point values; they are not low-precision replacements used to execute the program. Initially, `dot` is an uninterpreted function independent of `sum`. The solver can assign unrelated results to the source dot product and target sums, producing a failed validation that does not yet demonstrate a real miscompilation.

**Exposing the missing structure.** The next abstraction stage expresses the dot product as a sum of elementwise products. Multiplication by 1 is handled by the arithmetic encoding, leaving the source `sum([a, b, c])`. Let `u = sum([c, a])` be the target's inner result, so its final result is `sum([b, u])`.

**Encoding the permitted reduction laws.** For a symbolic hash function `h`, impose the nesting constraint `h(u) = h(c) + h(a)`. The source's aggregate hash is `h(a) + h(b) + h(c)`; the target's is `h(b) + h(u)`, which expands to the same expression. The reduction encoding requires unequal reduction results to have distinguishable aggregate hashes. These hashes are identically equal, so the solver cannot keep the two results unequal. No concrete hash values need to be selected, and the proof is not a probabilistic collision test.

**Checking the numerical contract.** For `A = [2^25, -2^25, 1]`, strict binary32 arithmetic with round-to-nearest gives 1 for the left-to-right source accumulation. The target's inner `1 + 2^25` rounds to `2^25`, and its outer addition gives 0. Thus the algebraic proof is valid only under the permitted reduction laws, not under strict IEEE execution. MLIR-TV's IEEE mode disables the incompatible unsafe reduction properties. A successful abstract proof is also conditional on the supported operations and any size bounds [8].

## Concepts and terms

**[1] MLIR and translation validation.** MLIR programs combine dialects, each defining operations and types at a particular level. Tensor dialects express whole-tensor computations; `linalg` expresses structured iteration and reduction; `memref` describes memory-backed buffers and their layouts. MLIR-TV checks intraprocedural source/target function pairs with matching signatures rather than proving the transformation implementation correct for every program.

**[2] Tensor and loop encoding.** A tensor is an SMT array indexed in row-major order, with shape information and a separate initialization mask. An operation's result is a function from an output index to its element expression. For a supported `linalg` loop, indexing maps and parallel/reduction annotations determine the output expression without discovering an inductive loop invariant. Reductions use uninterpreted functions; array elements outside the valid shape are replaced with a neutral value before they are passed to a reduction, so unused array entries cannot affect the result.

**[3] Floating-point abstraction and uninterpreted functions.** An SMT (satisfiability modulo theories) solver searches for assignments satisfying logical constraints. An uninterpreted function has no arithmetic implementation fixed in the query; the solver may choose any interpretation consistent with those constraints. Abstract floating-point values retain sign, magnitude ordering, and distinguished cases such as zero, infinity, and NaN (not-a-number). Their width is chosen from a bound on how many distinct values a counterexample could require, including intermediate function applications, not merely the declared tensor element width. For elementwise operations, each output uses matching input positions, so one mismatching element suffices and reduces that bound. Commutativity of a binary operation can be encoded as `g(x, y) & g(y, x)`, where `g` is a fresh uninterpreted function and `&` is bitwise AND. Every commutative function can be represented this way.

**[4] Refinement and memory.** The encoded final state contains the return value, memory, and an undefined-behavior flag. Undefined behavior (UB) leaves an execution unconstrained. A target refines a source if the source has UB, or the target preserves the defined return and relevant memory behavior without introducing UB. Invalid tensor shapes, out-of-bounds accesses, and reads of uninitialized elements are UB in the paper's model. Memory buffers carry a block identity, offset, dimensions, and a layout mapping indices to storage offsets; the final comparison accounts for externally visible blocks and their accessibility and writability.

**[5] Abstraction refinement.** A coarse over-approximation permits behaviors absent from the intended arithmetic, so a countermodel can be spurious. MLIR-TV first leaves dot products independent of sums and uses coarse cast functions. On failure or timeout, it exposes dot products as sums of products and uses a more precise cast encoding. A further stage expands small constant-length sums into additions. General constant folding may require the separate IEEE mode. An unresolved abstract counterexample or timeout is not automatically proof of a compiler bug.

**[6] Hash constraints for reductions.** For an array `B`, define `H(B) = sum(h(x) for x in B)` using bit-vector addition and a symbolic element-hash function `h`. A multiset records elements and their multiplicities without their order. Permutations have identical hashes for every `h`; with a sufficiently large hash range, different multisets can be distinguished by some `h`. Therefore encode `sum(B) != sum(C) => H(B) != H(C)` with a fresh symbolic hash, letting the solver choose a distinguishing interpretation if one exists. Nested reductions add equations relating the hash of an inner result to the hashes of its elements. Hash widths must satisfy the encoding's bounds; arbitrary small widths can collapse distinctions. The paper also shares hash functions between comparisons with a stronger range bound, detailed in its supplement.

**[7] IEEE arithmetic versus permitted algebraic laws.** IEEE floating-point addition rounds and is not associative. Enabling reduction reassociation changes the assumed semantics; it is not an optimization of an exact IEEE proof. MLIR-TV assumes a semantics satisfying the selected laws and proves transformations relative to it. The abstract encoding is not simply real arithmetic: it retains special floating-point cases, ordering, and selected rounding information. IEEE mode uses the solver's concrete floating-point theory and disables incompatible reduction laws. The paper's final-value refinement treats NaN results of different signs as equivalent.

**[8] Scope and trust.** Over-approximation preserves the ability to expose a concrete bug only within the supported semantic model; it does not guarantee that every failure is real or that solving terminates. Optional bounds on dynamic tensor sizes can miss bugs outside those sizes. The paper does not support general function calls or loops that allocate buffers, and returning references to local buffers can produce false alarms. Its large-model experiments split functions into smaller pieces and adjusted selected signed-zero semantics; they are not unrestricted end-to-end proofs of the original model compilations.

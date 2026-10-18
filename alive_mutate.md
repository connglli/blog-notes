# High-Throughput, Formal-Methods-Assisted Fuzzing for LLVM

**Summary by:** GPT 6 Astra

**Author:** Yuyou Fan, John Regehr

**Source:** CGO 2024, pages 349-358

**Link:** https://doi.org/10.1109/CGO57630.2024.10444854

**Code:** [Alive-Mutate, paper artifact](https://github.com/Hatsunespica/alive2/tree/CGO-2024-artifact), [archived artifact](https://doi.org/10.5281/zenodo.10205321)

## Key insight

Use random mutations to explore program structures and Alive2 to check the optimizer across runtime inputs. A mutation may change the seed program's meaning; the optimization of that mutant is the step that must preserve permitted behavior.

## Basic idea

Alive-Mutate generates compiler tests by applying structured mutations [1] to existing LLVM IR tests while preserving typing and SSA validity [2]. Each mutant is passed through selected LLVM optimizations, then Alive2 performs translation validation [3] between the mutant and its optimized form. The required relation is refinement [4], so undefined behavior in the input program can be handled without demanding that every generated program be UB-free. Mutation, optimization, and checking run in one process [5], avoiding repeated parsing and file transfers, while logged pseudorandom seeds support replay [6].

## Illustrative example

**The seed.** A small function reads a byte, writes through another pointer, and reads the byte again:

```llvm
define i8 @difference(ptr noalias %read_at, ptr %write_at) {
entry:
  %before = load i8, ptr %read_at, align 1
  store i8 9, ptr %write_at, align 1
  %after = load i8, ptr %read_at, align 1
  %gap = sub i8 %after, %before
  ret i8 %gap
}
```

The `noalias` contract [7] prevents the write through `%write_at` from modifying the storage read through `%read_at` in a defined execution. An optimizer can therefore replace `%gap` with zero while retaining the store. Preprocessing checks that Alive2 supports the function and that optimizing the unmutated seed does not already produce a validation failure.

**Mutation.** Clone the seed and remove `noalias`. No operand type or definition changes, so SSA validity is preserved. The mutant permits an additional case: both pointers can name the same byte. Its meaning need not match the seed's meaning.

**Optimization and validation.** Consider a hypothetical buggy optimization that still returns zero for this mutant. Alive2 compares that result with the mutant, not with the seed. Give both pointers the same valid, writable byte address containing 4. The mutant reads 4, stores 9, reads 9, and returns 5; the optimized version stores 9 but returns 0. This is a defined-input counterexample, so refinement fails. The example illustrates the testing mechanism, not a claim that this particular bug was reported in the paper.

**Replay and repeat.** Record the seed that generated the mutant and the failure. A replay with the same tool versions and options can save the IR for inspection. Discard the mutant and begin the next iteration from the original seed, so successive trials do not silently accumulate unrelated mutations. A compiler crash is another failure category; an Alive2 timeout is not evidence of a miscompilation.

## Concepts and terms

**[1] Structured mutation.** Change the compiler's in-memory intermediate representation (IR) through operations that understand its structure. Examples include changing constants, toggling attributes, replacing operands, and moving instructions. A replacement operand must have the required type and be available at its use; if moving an instruction breaks that condition, the mutator chooses or creates replacement operands. Mutations need not preserve semantics. This differs from metamorphic tests whose mutations must maintain a known behavioral relation to the seed.

**[2] SSA and dominance.** Static single assignment gives every register one definition. A definition dominates a use when every execution path reaching that use passes through the definition; this is what makes the value available. Parameters and suitable constants are also available operands. The mutator caches dominance information and literal constants, with per-mutant information overriding the original cache where needed. Preserving these structural constraints makes a test acceptable to LLVM's IR verifier; it does not imply that the test has no undefined behavior.

**[3] Translation validation as the test oracle.** An oracle decides whether a test exposed a failure. Alive2 asks whether a particular optimized function correctly implements its input function, using symbolic rather than sampled runtime values. Its SMT (satisfiability modulo theories) solver searches logical formulas for a counterexample. Fuzzing samples programs; the validator searches their runtime-input space subject to its supported semantics and loop bounds. Unsupported features or incomplete solver results limit what a trial can establish.

**[4] Refinement and undefined behavior.** Every optimized behavior must be permitted by the unoptimized mutant. Source UB imposes no requirement on the corresponding target behavior, but a defined source execution must not acquire an impermissible result or new UB. Thus deleting an attribute can create useful tests by making more input cases defined. A confirmed failure is relative to the correctness of Alive2's model and implementation, as described in the [Alive2 summary](alive2.md).

**[5] In-process workflow.** Parse and preprocess a seed once, clone it for a trial, mutate the clone, retain the mutant as the reference, optimize a working version, and compare the two through Alive2's API. Reuse the process across trials; avoid printing and reparsing IR between stages. The paper compares 1,000 mutants for each of 194 small tests for InstCombine, LLVM's local simplification pass, against separate mutator, `opt`, and `alive-tv` processes using matching random seeds, reporting about 12 times higher average throughput. This saves orchestration overhead, not the underlying SMT work.

**[6] Pseudorandom replay.** A pseudorandom generator produces a deterministic sequence from its seed. Logging the seed for each mutant makes an interesting trial reproducible under the same configuration, while optional file saving keeps routine trials free of that I/O cost. The loop stops on its iteration or time limit, or a compiler crash.

**[7] Aliasing and `noalias`.** Pointers alias when accesses through them reach overlapping storage. For the seed's parameter, `noalias` constrains accesses during the call: storage accessed through that parameter and modified during the call cannot also be accessed through an unrelated pointer. It is not merely a test that pointer arguments have different bit patterns. Removing the attribute removes the assumption; violating it while the attribute is present makes the seed execution undefined.

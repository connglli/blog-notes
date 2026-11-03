# Formal certification of a compiler back-end, or: Programming a compiler with a proof assistant

**Summary by:** GPT 6 Astra

**Author:** Xavier Leroy

**Source:** POPL 2006; SIGPLAN Most Influential POPL Paper Award 2016.

**Link:** https://doi.org/10.1145/1111037.1111042

**Code:** [CompCert compiler project](https://github.com/AbsInt/CompCert)

## Key insight

A compiler can be an executable function accompanied by a proof that every successful result preserves its source program's specified behavior. Each pass can use its own intermediate language and its own relation between source and target states.

## Basic idea

The paper verifies a back end from Cminor [1] to a PowerPC assembly model in Coq [2]. Each compilation pass comes with a semantic-preservation proof [3], and the proofs compose across intermediate languages. Complicated choices can be delegated to untrusted algorithms when a verified checker [4] validates the choices before use. The theorem is conditional on successful compilation and the source semantics; it does not certify an entire C toolchain or arbitrary undefined source behavior.

## Illustrative example

**Source and registers.** Consider a Cminor computation that calculates `temp = input + 5` and returns `temp`, using the language's machine-integer operations. An intermediate register-transfer representation puts `input` and `temp` into pseudo-registers.

A state relation records which source variable corresponds to which pseudo-register. The translation proof establishes that executing the target instructions produces the value prescribed by the source expression. For input 7, both compute 12.

**Allocation choice.** A register allocator proposes physical locations for pseudo-registers. If two values must remain available simultaneously, the allocation must not overwrite one with the other. The verified checking machinery rejects a proposal that violates its allocation constraints; the search heuristic itself need not be proved correct.

**Stack and instructions.** Spilled values become stack accesses, and later passes assign actual frame offsets and expand operations into PowerPC instructions. Their proofs use relations describing how abstract locations correspond to memory. A frame too large for the target's supported addressing is a compilation error, not an excuse to emit a wrong offset.

The arithmetic result is only the smallest visible part of the contract. Calls, memory accesses, and control flow also need the intermediate-state relations used by their respective passes.

**Scope.** If compilation succeeds, compose the pass theorems to relate the final assembly to Cminor. The 2006 semantic-preservation theorems cover terminating source executions; their premises do not establish preservation for nonterminating programs. The source parser, final assembler, processor, and proof-checking infrastructure are separate parts of the trust boundary.

## Concepts and terms

**[1] Cminor.** The paper's low-level C-like imperative input language, with structured control flow, explicit memory operations, functions, and machine-oriented values. It is not the full C language.

**[2] Coq.** A proof assistant in which the compiler functions, semantics, and correctness proofs are expressed. Executable code can be extracted from the functional definitions.

**[3] Semantic preservation.** A relation between executions before and after translation, conditional on the source behavior covered by the semantics. A simulation argument connects different intermediate representations rather than requiring identical machine states.

**[4] Verified checker.** A proved procedure that accepts only proposals satisfying specified constraints. An untrusted heuristic may fail to find an acceptable proposal, but cannot silently bypass the check.


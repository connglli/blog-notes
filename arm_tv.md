# Translation Validation for LLVM's AArch64 Backend

**Summary by:** GPT 6 Astra

**Author:** Ryan Berger, Mitch Briles, Nader Boushehrinejad Moradi, Nicholas Coughlin, Kait Lam, Nuno P. Lopes, Stefan Mada, Tanmay Tirpankar, John Regehr

**Source:** OOPSLA 2025, Proceedings of the ACM on Programming Languages 9, article 369

**Link:** https://doi.org/10.1145/3763147

**Code:** [ARM-TV](https://github.com/regehr/alive2/tree/arm-tv), [paper artifact](https://doi.org/10.5281/zenodo.17013831)

## Key insight

Lift the backend's AArch64 output back into LLVM IR so that Alive2 can compare it with the original function. The lifted program must model machine behavior and calling-convention obligations, not silently inherit LLVM assumptions that are invalid for assembly.

## Basic idea

ARM-TV checks an LLVM function's translation to AArch64 assembly through a lowering-and-lifting pipeline [1]. Its lifter reconstructs the machine's register and stack environment using the application binary interface (ABI) [2], then expresses each instruction in LLVM IR while preserving the instruction's more tightly specified behavior [3]. An assembly-mode memory model [4] handles raw addresses and pointer/integer mixtures that LLVM's ordinary pointer rules cannot represent faithfully. After LLVM simplifies the lifted code, Alive2 checks refinement [5] against the original function, including return values, memory, and ABI checks; the guarantee depends on the lifter and checker and remains bounded for loops [7].

## Illustrative example

**Lowering.** Our LLVM function loads a 64-bit word and shifts it by an input amount:

```llvm
define i64 @scaled_load(ptr %address, i64 %distance) {
entry:
  %word = load i64, ptr %address, align 1
  %result = shl i64 %word, %distance
  ret i64 %result
}
```

A suitable AArch64 implementation is:

```asm
scaled_load:
  ldr x8, [x0]
  lslv x0, x8, x1
  ret
```

The ABI places `%address` in `x0`, `%distance` in `x1`, and the return value in `x0`. Register `x8` is temporary storage. Assume the load accesses eight valid, initialized bytes; `align 1` does not require the address to be eight-byte aligned.

**Building the environment.** The lifter allocates LLVM storage for the modeled registers and stack, initializes unspecified register contents with `freeze poison`, and writes the arguments into their ABI locations. This makes otherwise unspecified contents arbitrary but stable, allowing the solver to find accidental dependencies on them. Here `ldr` overwrites `x8` before it is used, and the three instructions leave the stack pointer and all callee-saved registers unchanged.

**Lifting the instructions.** ARM-TV can use hand-written instruction semantics or semantics obtained from ARM's ASL specification through ASLp [6]. Crucially, `lslv` reduces the shift amount modulo 64, whereas LLVM's `shl` produces poison for an amount of 64 or more. A correct lifting therefore masks the amount. After eliminating the register-storage bookkeeping, the computation has this LLVM form:

```llvm
define i64 @scaled_load_lifted(ptr %address, i64 %distance) {
entry:
  %word = load i64, ptr %address, align 1
  %masked = and i64 %distance, 63
  %result = shl i64 %word, %masked
  ret i64 %result
}
```

This is a simplified illustration of the computational part, not a complete dump of ARM-TV's environment and ABI checks. On the assembly side, `x0` holds an address rather than a logical object-and-offset pair; the assembly memory model resolves that address to the accessed bytes.

**Checking refinement.** When `distance < 64`, the source and lifted results agree. At `distance = 64`, the LLVM source returns poison while the machine returns the loaded word, which is a permitted refinement. But lifting `lslv` as an unmasked LLVM shift would misrepresent the machine instruction, even if that mistake did not invalidate this particular endpoint comparison.

**Detecting an error.** Replace the assembly's `lslv x0, x8, x1` with its 32-bit form, `lslv w0, w8, w1`. With the loaded word `2^40` and distance 0, the source returns `2^40`, but the incorrect code returns 0 because writing `w0` clears the upper half of `x0`. This gives a defined-input mismatch. Independently, clobbering a callee-saved register without restoring it would violate an ABI obligation even if the numerical return value matched.

## Concepts and terms

**[1] Lowering and lifting.** Lowering translates LLVM's typed intermediate representation (IR) into machine instructions. Lifting translates those instructions into an IR model of their effects. ARM-TV lowers one function with LLVM, lifts the resulting assembly, simplifies the lifted IR using LLVM's middle end, and passes the original and lifted functions to Alive2. This checks a compilation instance, not every possible execution of the backend on every input program.

**[2] ABI and checking the environment.** An ABI specifies where arguments and results reside, which registers a caller may expect to survive a call, and stack requirements. ARM-TV checks 16-byte stack-pointer alignment and restoration of callee-saved registers. At a modeled call, caller-saved registers become nondeterministic, so relying on their old values is detectable. Argument and return extension attributes are also enforced. Register storage is initialized with fixed arbitrary values, not zeroes; zero initialization could hide an erroneous read of unspecified state.

**[3] Instruction semantics and poison.** A machine instruction may define inputs for which an apparently corresponding LLVM instruction produces poison or immediate UB. Poison is LLVM's deferred exceptional value; it is not an ordinary hardware bit pattern. The lifter must preserve machine-defined cases with explicit masks, guards, or suitable intrinsics. A machine-level instruction name is therefore not enough to select the corresponding LLVM operation.

**[4] Assembly-mode memory.** Ordinary LLVM pointers carry an allocation identity and offset, restricting which object they may access. Assembly pointers are physical addresses that can access any valid region. ARM-TV extends Alive2 so lifted functions use physical pointers with full provenance, ordinary non-poison input and loaded values, address-based pointer comparison during refinement, and byte comparison that permits type punning, interpreting the same bytes as either pointers or integers. Memory still has validity constraints; full provenance does not make every address dereferenceable. Assembly mode rejects sub-byte accesses, while refinement separately checks the ABI's padding rules for sub-byte LLVM values.

**[5] Refinement checking.** The optimized implementation must introduce no behavior forbidden by the source. Source poison or UB permits a more defined machine implementation, but ordinary source results and observable memory must be preserved. Alive2 encodes this as constraints for an SMT (satisfiability modulo theories) solver, which searches for an assignment demonstrating a mismatch. A failed endpoint comparison indicates a defect somewhere in the compilation, lifting, simplification, or checking chain; it does not by itself identify which component is wrong.

**[6] ASL and ASLp.** ASL is ARM's Architecture Specification Language. ASLp partially evaluates that specification for a particular instruction encoding and configured execution mode, retaining symbolic operands while specializing known instruction fields. ARM-TV translates the reduced imperative program into LLVM IR. Its vectorization support recognizes suitable loops in the specification and emits LLVM vector operations instead of expanding everything into scalar bit manipulation. The ASL-to-LLVM bridge and configuration remain trusted; the generated lifter is not automatically an end-to-end verified compiler.

**[7] Scope and trust.** The paper targets sequential user-mode code, with a fixed modeled stack and bounded loop handling inherited from Alive2. It excludes features such as inline assembly, privileged instructions, and some unspecified calling conventions. The lifter, ABI model, post-lifting LLVM optimization, Alive2, and solver all matter to the result. The paper also reports false alarms from its alignment-inference heuristic and recommends disabling that heuristic to check whether a reported failure persists. Validation covers LLVM IR to AArch64 assembly, not the source-language frontend, assembler, or linker.

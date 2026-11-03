# Deegen: A JIT-Capable VM Generator for Dynamic Languages

**Summary by:** DeepSeek V4.1 Flash, GPT 6 Astra

**Author:** Haoran Xu, Fredrik Kjolstad

**Source:** OOPSLA1 2026, Proceedings of the ACM on Programming Languages 10, article 138, 29 pages

**Link:** https://doi.org/10.1145/3798246

**Code:** [LuaJIT Remake](https://github.com/luajit-remake/luajit-remake), [DSOM](https://github.com/sillycross/dsom)

**Artifact:** [Zenodo artifact](https://zenodo.org/records/18503844)

## Key insight

Deegen moves execution-engine engineering to build time: one C++ description of each bytecode produces both an interpreter and a fast-compiling baseline JIT. Both tiers share the language semantics while using different dispatch, specialization, and caching machinery.

## Basic idea

A dynamic-language virtual machine (VM) [1] often needs a low-overhead interpreter and a baseline just-in-time (JIT) compiler to execute code before expensive optimization becomes worthwhile. Deegen takes bytecode descriptions [2], type information, and inline-cache definitions [3], then generates both execution tiers and the logic that transfers execution between them. Build-time type specialization [4] removes unnecessary checks and separates common cases from slower fallback code. The interpreter uses continuation-passing dispatch and pinned registers [5], while the baseline JIT uses Copy-and-Patch [6] to assemble machine code from precompiled pieces. The implementer still supplies the parser, object representation, runtime services, and other language-specific components outside the generated engine.

## Illustrative example

**Setup.** Our toy language Tern represents numbers and objects as tagged values. Its function `bump(v)` computes `v.x + 1.5`; non-object arguments, missing properties, and non-number field values raise language errors. Objects `p = {x: 2.0, y: 9.0}` and `q = {x: 5.0, y: 7.0}` share an immutable shape identified by the integer `Point`, which maps `x` to storage slot 0. The function becomes three bytecodes: `FGET v, "x", t0`, `FADD t0, 1.5, t1`, and `RET t1`.

**Descriptions and specialization.** The implementer supplies C++ semantics and operand declarations for those bytecodes. `FGET` takes an object operand from a local slot and a property name from the constant table. Its cache uses the shape identifier as its key, saves the slot found by property lookup, and loads that slot from the current object on a hit. An `FADD` variant declares its right operand to be a constant number and speculates that its left operand is a number. Deegen removes the right-hand type check, retains a check on the left, and routes a failed check to the error-handling slow path.

**Interpretation.** On `bump(p)`, the field cache misses, resolves `x` to slot 0, and remembers that slot for `Point`. On `bump(q)`, the shape matches and the cache loads `q`'s slot 0, producing `6.5` after addition. It caches the lookup result, not `p`'s field value. Each bytecode implementation passes control directly to the next implementation while forwarding the VM state in designated registers.

**Compilation.** After enough calls make `bump` hot, the generated tier-switching logic requests baseline compilation. The compiler computes code and data sizes, allocates memory, copies and patches the bytecodes' machine-code templates, and fixes branch targets. Local-slot offsets and the constant `1.5` become values embedded in the generated code. The single bytecode scan belongs to the code-generation step; compilation as a whole has several steps.

**Compiled caching.** The first compiled field access can miss and generate a small code fragment that compares the shape with `Point` and loads slot 0. If that fragment fits in the cache's reserved code region and the region is empty, it is placed there. A different shape can add another fragment to the chain. A failed type check or missing property still reaches Tern's full error semantics.

## Concepts and terms

**[1] VM execution tiers.** An interpreter executes bytecodes, compact instructions chosen by the language implementation. A baseline JIT translates them to native instructions with little compilation work; an optimizing JIT spends more time analyzing the program to improve execution speed. Deegen generates the first two tiers. Per-function bytecode counts guide tier-up, the transition to compiled execution.

**[2] Bytecode descriptions.** Each description pairs a semantics function with declarations of operands, results, and variants. A variant specializes operand forms or types, such as a constant numeric right operand. Deegen APIs express actions that need different implementations across tiers, including returning a result, calling a guest-language function, entering a slow path, and raising an error. The parser emits bytecodes using generated builder APIs.

**[3] Shapes and inline caches.** A shape describes an object's property layout. More generally, a Deegen cache splits a computation into a lookup whose result is stable for a given key and an effect that combines cached state with fresh inputs. Captured lookup-local values form the cached state. Each bytecode occurrence has its own cache: the interpreter stores one entry, while the baseline JIT can maintain a chain of entries. A cache is sound only if a matching key still justifies its saved state; the language implementer must arrange that property.

**[4] Type specialization and slow paths.** A tagged value contains enough information to identify its language type as well as its payload. The implementer supplies type tests and representations. Deegen enumerates permitted parameter-type combinations and propagates constant results through the semantics to determine which code is reachable. Known types can eliminate checks; speculated types require runtime checks. Uncommon cases are moved to separate slow-path code, reducing the amount of code in the common path.

**[5] Continuation-passing dispatch and register pinning.** Each bytecode implementation is a machine function that ends with a tail call, transferring control without adding a native call-stack frame. Passing VM state in fixed argument positions under a suitable calling convention keeps values such as the bytecode pointer and stack base in designated registers. A separate VM stack records guest-language activations.

**[6] Copy-and-Patch.** A stencil is precompiled machine code with holes for constants and addresses. Deegen builds stencils offline from the bytecode semantics, then emits runtime routines that copy them and fill the holes. Common paths can fall through between bytecodes instead of dispatching through the interpreter. Slow paths are compiled ahead of time and use generated metadata to return to the appropriate location in JIT code.

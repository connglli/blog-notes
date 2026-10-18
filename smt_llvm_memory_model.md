# An SMT Encoding of LLVM's Memory Model for Bounded Translation Validation

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:** Juneyoung Lee, Dongjoo Kim, Chung-Kil Hur (Seoul National University); Nuno P. Lopes (Microsoft Research)

**Source:** CAV 2021

**Link:** https://doi.org/10.1007/978-3-030-81688-9_35

**Code:** [Alive2](https://github.com/AliveToolkit/alive2)

## Key insight

The first SMT encoding of LLVM's memory model precise enough to validate all of LLVM's intra-procedural memory optimizations and scalable to large programs, obtained by exploiting the structure of bounded translation validation: block ids are bounded, local and non-local blocks are separated, and every block owns its own SMT array. The encoding also needs a heap-allocation semantics that supports both checked and unchecked `malloc`, and it uncovered 21 previously unknown bugs.

## Basic idea

Verification of LLVM's scalar optimizations is mature, but memory optimizations are barely covered, because aliasing [3] forces the solver to consider every live object for every memory access. The paper targets bounded translation validation [1]: loops are unrolled a fixed number of times, so the tool checks one function pair at a time rather than the optimizer in general. It gives an SMT encoding of LLVM's memory model [2] in which pointers are (block id, offset) pairs and each block's bytes live in their own SMT array [5]; local blocks are separated from non-local ones by the top bit of the block id [4], block ids are bounded and mostly constant, and unknown pointers are restricted to a small alias set, so most aliasing questions are resolved before the solver sees them. It also defines a heap-allocation semantics [8] that requires an optimization to be correct both when `malloc` always succeeds and when `malloc` may return null, supporting both common C coding styles, and it approximates some behaviors [9] to stay scalable. Implemented in Alive2 [11], the encoding validates LLVM's 6,600 transformation tests in about 2.5 hours, finds 21 new memory bugs (10 already fixed), and reports 79 incorrect optimization pairs on five benchmarks with no false positives, all traced to mismatches between LLVM and the formal semantics, mostly incorrect handling of undef and poison [10].

## Illustrative example: removing an allocation and forwarding a store

**The transformation.** The source allocates a local block, stores to it, overwrites unrelated memory through an argument, and reads the local block back. The optimizer removes the allocation and returns the stored constant:

```c
#include <stdlib.h>

int f(int *p) {
    int *q = malloc(sizeof *q);
    *q = 42;
    *p = 7;
    return *q;
}
```

```c
int f(int *p) {
    *p = 7;
    return 42;
}
```

**Blocks and aliasing.** `p` comes from the caller, so it can only carry provenance for a non-local block; `q` is allocated inside `f`, so it is a fresh local block. A pointer can only access the block it carries provenance for [2], so `p` cannot touch `q` even if their physical addresses coincided. The encoding gets this for free by putting local blocks in the id range whose top bit is 1 and non-local blocks in the range whose top bit is 0 [4], so the solver never has to split on whether `p` and `q` alias.

**Memory and UB.** Each block gets its own SMT array from offset to byte [5], and bytes encode pointers and per-bit poison [6]. The store `*q = 42` writes `q`'s array at offset 0; the store `*p = 7` writes only non-local arrays, because `p` is non-local, so `q`'s array is untouched. Every access also updates the UB flag [2]: the access is UB if the pointer is not dereferenceable, for example if the offset is outside the block. The load `return *q` reads `q`'s array at offset 0 and returns 42.

**Refinement.** Correctness is a refinement query [7]: every target result under the encoding's assumptions must be permitted by some source execution, including the source's nondeterministic choices. The target returns 42 and its memory equals the source's minus the local block `q`; because `q` never escapes (no pointer to it is stored to memory or returned), the mapping between escaped local blocks ignores it, and the source's return value is 42 by store forwarding. The query is valid, so the transformation is verified.

**Null checks.** The source dereferences `q` immediately, without checking for null. The heap-allocation semantics [8] requires the transformation to be correct under both "malloc always succeeds" and "malloc may return null", which accommodate programs that omit null checks and programs that perform them; semantics C alone supports both allocation removal and null checks, but can make unchecked allocations vacuously justify arbitrary transformations.

## Concepts and terms

**[1] Bounded translation validation (BTV).** Checking that a compiler transformation is correct for a particular program pair, with loops unrolled a fixed number of times, instead of verifying the optimizer for all inputs. The paper validates pairs of IR functions taken before and after each intra-procedural optimization pass of a real compilation.

**[2] Memory blocks and pointers.** LLVM memory is a collection of blocks: each stack or global variable is a block, and each heap allocation creates a fresh one. A block has a size, alignment, read/write properties, liveness, allocation kind (stack, heap, global), a physical address, and contents. The encoding covers logical pointers in one address space and does not support integer-to-pointer casts (Section 3). A pointer is a (block, offset, attributes) triple; pointer arithmetic changes the offset but keeps the block, so a pointer can only access its own block. Accessing out of bounds, or through a dead or poison pointer, is undefined behavior.

**[3] Aliasing.** Determining which objects a memory access may touch. Without extra information, each access may touch any live block, so an SMT solver has to consider a cross product of blocks and accesses, which is the main obstacle to scaling memory verification. The encoding resolves most cases cheaply (constant ids, the local/non-local split) so that the solver sees small alias sets.

**[4] Local and non-local blocks.** Local blocks are allocated in the function under verification (its stack slots and heap allocations); all other blocks are non-local (globals, caller allocations, callee heap allocations; callee stack blocks are not observable). The most significant bit of a block id marks the kind, so the two groups never alias and globals and stack slots get constant ids. Non-local blocks have the same ids in the source and target functions; local blocks do not, because the two functions allocate differently.

**[5] Multi-array memory encoding.** One SMT array per block, from offset to byte, instead of one array from pointer to byte. Stores and loads touch only the arrays of blocks the pointer may alias; with small alias sets the formulas stay small and simplifications such as store forwarding apply. A read through an unknown pointer becomes a chain of `ite`s over the candidate arrays. Partial-order reduction additionally limits each unknown pointer to a prefix of the block ids, which bounds its alias set without losing precision.

**[6] Byte encoding.** Block contents are arrays of bytes, and a byte is either a pointer byte or a non-pointer byte. A pointer byte stores the pointer's (block, offset, attributes), a poison bit, and which byte of the pointer it is; storing a pointer writes several consecutive bytes. A non-pointer byte stores eight value bits and eight poison bits, so integer values track poison per bit. Reading a non-pointer zero byte as a pointer yields null, which supports `memset`-based initialization of pointer arrays.

**[7] Refinement.** Correctness is a refinement relation, not equality, because the compiler may remove behaviors. For all inputs related by refinement, if the target terminates with output O under its precondition, then the source can produce an output related to O, or the source has UB. Output refinement compares UB status, return values, and memory. Pointers to local blocks are compared through a mapping between escaped local blocks of the source and target, since the allocation orders may differ; any target value refines a poisoned source value. A function call extends the mapping transitively when a local block escapes.

**[8] Heap allocation semantics.** Three candidate semantics for `malloc`: (A) all allocations succeed; (B) an allocation succeeds only when a linear memory model has room; (C) allocations may non-deterministically return null, and executions that run out of space are excluded. A allows removing unused allocations but also removing null checks; B allows neither; C preserves null checks but lets an unchecked null dereference (UB) justify arbitrary code. The paper requires transformations to be correct under both A and C, which accommodates both unchecked and checked `malloc` styles.

**[9] Approximations for scale.** The encoding under-approximates some behaviors and over-approximates others to keep SMT queries small: local and non-local address spaces are separated by the top address bit; globals start as poison or concrete values, never as undef; `strlen`, `memcmp`, and `bcmp` are unrolled with a size precondition; and the set of escaped local blocks is computed per function. These approximations can cause both missed bugs and false reports; the paper argues that their practical impact is small for the LLVM optimizations evaluated (Section 9).

**[10] undef and poison.** LLVM's deferred-UB values: `undef` may yield a different value at every use, and `poison` taints values, with branching on poison being UB. The memory encoding tracks poison per bit inside blocks. On the five benchmark programs, 74 of the 79 incorrect optimization pairs involve incorrect handling of undef or poison, and the remaining 5 involve load type punning.

**[11] Alive2.** The bounded translation validation tool in which the encoding is implemented; the memory model adds about 3.0 KLoC plus 0.4 KLoC of analyses. Alive2 generates SMT queries for Z3 and was used to report 21 new LLVM memory bugs and to fix documentation inconsistencies, including the `nonnull` attribute mismatch, where the agreed fix makes a non-conforming pointer poison instead of UB.

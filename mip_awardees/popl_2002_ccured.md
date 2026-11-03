# CCured: Type-safe retrofitting of legacy code

**Summary by:** GPT 6 Astra

**Author:** George C. Necula, Scott McPeak, and Westley Weimer

**Source:** POPL 2002; SIGPLAN Most Influential POPL Paper Award 2012.

**Link:** https://doi.org/10.1145/503272.503286

**Code:** [CCured source, preserved mirror](https://github.com/CTSRD-CHERI/ccured)

## Key insight

Different C pointers need different safety mechanisms. Infer which pointers retain a trustworthy static type, and reserve expensive metadata and checks for the pointers whose uses defeat that reasoning.

## Basic idea

CCured infers pointer kinds [1] and translates C into code with appropriate runtime checks. SAFE pointers [2] support ordinary typed dereferences, SEQ pointers [3] support typed pointer arithmetic with bounds information, and DYNAMIC pointers [4] support uses whose pointee type cannot be trusted statically. Constraints propagate through assignments, casts, and aliases so that a dynamically typed write cannot invalidate an alias's assumed static type. Memory-lifetime handling is also required; classifying pointer arithmetic alone does not establish complete memory safety.

## Illustrative example

**Setup.** Consider a typed integer array and an index chosen at runtime:

```c
int values[4] = {3, 6, 9, 12};
int *cursor = values;
int *selected = cursor + index;
int answer = *selected;
```

Assume the array remains alive through the read. The code shown is input to the analysis, not a safe routine for arbitrary `index` without instrumentation.

**Inference.** Arithmetic on `cursor` requires a SEQ pointer. Because `selected` is only dereferenced and is not itself used in arithmetic, it can be SAFE after a checked conversion. The types of the underlying cells remain reliably integer because this fragment contains no incompatible pointer cast.

**Instrumentation.** The SEQ representation identifies the allocated region and the current position. Converting the computed pointer to SAFE checks that it is a genuine pointer and points within the region. For `index = 2`, the check succeeds and the read returns 9. For `index = 4`, conversion to a dereferenceable SAFE pointer fails; a one-past position must not become permission to load an element.

SAFE pointers may be null, so their dereference discipline still includes a null check unless another analysis eliminates it. Calling a pointer SAFE does not mean every runtime check disappears.

**Incompatible uses.** If the same memory can also be accessed through pointer types with incompatible element interpretations, the analysis must use its DYNAMIC machinery and propagate that decision to relevant aliases. Runtime tags distinguish pointer-bearing data from ordinary integer contents, preventing an integer write through one alias from becoming an unchecked pointer read through another.

## Concepts and terms

**[1] Pointer kind.** An inferred qualifier determining allowed pointer operations, representation, and required checks. The analysis generates and solves constraints instead of asking programmers to annotate every pointer.

**[2] SAFE pointer.** A null pointer or a valid address of the statically declared pointee type. It disallows unrestricted arithmetic and incompatible reinterpretation.

**[3] SEQ pointer.** A pointer capable of arithmetic within a statically typed allocation, carrying enough allocation information for bounds and validity checks.

**[4] DYNAMIC pointer.** A pointer into memory whose contents cannot be assigned one trustworthy static type. It requires extra metadata and checks, and its aliases must respect the same dynamic-memory invariant.


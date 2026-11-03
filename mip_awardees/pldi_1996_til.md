# TIL: A Type-Directed Optimizing Compiler for ML

**Summary by:** GPT 6 Astra

**Author:** David Tarditi, Greg Morrisett, Perry Cheng, Christopher Stone, Robert Harper, Peter Lee

**Source:** PLDI 1996; SIGPLAN Most Influential PLDI Paper Award, 2006

**Link:** https://doi.org/10.1145/231379.231414

## Key insight

Retaining types through optimization lets polymorphic programs use specialized data representations instead of forcing every value into one universal format.

## Basic idea

TIL uses typed intermediate languages [1], intensional polymorphism [2], and nearly tag-free garbage collection [3]. Polymorphic operations receive runtime type information when needed, while inlining and specialization remove type dispatch when types become known. Representation information also tells the collector which live values are pointers. Conventional and loop-oriented optimizations operate within this typed framework; type checking catches some compiler mistakes but does not prove semantic equivalence.

## Illustrative example

**Generic operation.** Consider a polymorphic array accessor that returns the element at position `k`. An array of floating-point values can store those values directly, while an array of references stores pointers. A shared accessor cannot blindly use one representation-specific load for both.

**Type-directed execution.** Compile the generic operation with a type argument describing the element representation. When that argument denotes floating-point values, select a floating-point array load; when it denotes references, select a pointer load. This is an internal implementation mechanism, not a demand that the source programmer manually dispatch on types.

**Specialization.** At a call where the array is statically known to contain floating-point values, inline the accessor and evaluate the type test during compilation. The resulting code performs the appropriate direct load, without allocating a separate box for the returned number merely to fit a universal polymorphic representation.

**Collection.** Suppose a live stack slot contains that number and another contains an array pointer at a collection point. Compiler-generated layout information says to trace the array pointer but not the numeric bits. For a live value whose type is still unknown, sufficient runtime type information must remain available. Heap records and arrays retain descriptive tags in the paper's nearly tag-free scheme, so "tag-free" must not be read as "no metadata anywhere."

## Concepts and terms

**[1] Typed intermediate language.** A compiler representation with explicit typing rules that transformations preserve and a checker can validate.

**[2] Intensional polymorphism.** Polymorphic execution can inspect a representation of its type argument to choose type-specific operations.

**[3] Nearly tag-free garbage collection.** Collection guided by compiler-generated stack/register layouts and necessary runtime metadata, avoiding per-value tags while retaining tags on heap-allocated structures.

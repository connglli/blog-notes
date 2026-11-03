# Halide: A Language and Compiler for Optimizing Parallelism, Locality, and Recomputation in Image Processing Pipelines

**Summary by:** GPT 6 Astra

**Author:** Jonathan Ragan-Kelley, Connelly Barnes, Andrew Adams, Sylvain Paris, Frédo Durand, Saman Amarasinghe

**Source:** PLDI 2013; SIGPLAN Most Influential PLDI Paper Award, 2023

**Link:** https://doi.org/10.1145/2491956.2462176

**Code:** [Halide](https://github.com/halide/Halide)

## Key insight

Specify what each image stage computes separately from when, where, and how often its values are computed and stored.

## Basic idea

Halide represents an image-processing pipeline as functions over coordinates and gives it a separate schedule [1]. The schedule controls iteration order, parallelism, and the storage and computation levels of intermediate stages. Compiler bounds inference [2] derives the regions each stage needs, allowing schedules to trade locality [3] against recomputation [4] without rewriting the algorithm. Search can evaluate candidate schedules, but a schedule is an execution choice, not an approximation of the requested result.

## Illustrative example

**Algorithm.** Let `h(x,y) = input(x,y) + input(x+1,y)` and `out(x,y) = h(x,y) + h(x,y+1)`. Request output coordinates `0 <= x < 4` and `0 <= y < 2`, with input available through column 4 and row 2. Use exact integer arithmetic within range.

**Whole-stage schedule.** Compute all 12 required `h` values for four columns and three rows, store them, then compute the eight outputs. Each intermediate is computed once, but a large image would require a correspondingly large intermediate buffer.

**Inline schedule.** Substitute the expression for `h` at every use. Eight outputs each require two `h` computations, making 16 in total. The middle intermediate row is recomputed, but no intermediate image is stored. Both schedules still read the same mathematical input values and produce the same outputs.

**Row schedule.** Store two intermediate rows and advance output rows sequentially. To produce row 0, compute `h` rows 0 and 1. For output row 1, reuse intermediate row 1 and replace row 0's storage with row 2. This computes 12 intermediate values while holding eight at once. Columns can run independently, whereas the chosen row-reuse scheme relies on sequential progress through rows. Bounds inference derives the extra input column and row from the coordinate expressions, rather than silently assuming input and output bounds match.

## Concepts and terms

**[1] Schedule.** Instructions for loop structure and placement of stage evaluation and storage. Storage must outlive the computations that use it.

**[2] Bounds inference.** Backward calculation of the coordinate ranges required by consumers.

**[3] Locality.** Keeping values near their subsequent uses so that less data moves through the memory hierarchy.

**[4] Recomputation.** Evaluating a value more than once to avoid storing or communicating it; it changes cost, not the value's definition.

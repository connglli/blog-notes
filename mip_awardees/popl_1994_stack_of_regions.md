# Implementation of the typed call-by-value lambda-calculus using a stack of regions

**Summary by:** GPT 6 Astra

**Author:** Mads Tofte and Jean-Pierre Talpin

**Source:** POPL 1994; SIGPLAN Most Influential POPL Paper Award 2004.

**Link:** https://doi.org/10.1145/174675.177855

**Code:** [ML Kit with Regions project](https://github.com/melsman/mlkit)

## Key insight

A compiler can infer lifetimes for groups of allocated values and reclaim each group at a lexical boundary. Region parameters let the same function allocate results with different lifetimes at different calls.

## Basic idea

The translation assigns every runtime value, including a closure, to a region [1]. Region and effect inference [2] annotates allocations and identifies regions that can be created and destroyed around an expression. Region polymorphism [3] lets functions receive allocation destinations as arguments. The resulting program uses a stack of region lifetimes, but individual regions can grow dynamically and need not be contiguous hardware-stack frames.

## Illustrative example

**Setup.** A function computes `x * 3`. Its caller needs the returned number after the function call, but the constant 3 used inside the function need not survive that call. Use the paper's allocation notation informally: `v at r` stores a freshly produced value in region `r`.

**Placement.** Give the function an input region `r_in` and a result region `r_out`. Its body creates a local region `r_tmp`, allocates the constant 3 there, reads `x` from `r_in`, and places the product in `r_out`. Exiting the body destroys `r_tmp`, while the product remains available in the caller-provided destination.

For input 4, the runtime briefly contains the input value, the local constant, and the result 12 in their respective regions. Deallocating the temporary region removes only the constant. Returning the result in `r_tmp` instead would leave an invalid reference and cannot justify this local-region boundary.

**Inference.** Types carry region information, and effects describe region reads and writes. A region variable occurring only in the expression's internal effect, but neither in the surrounding type environment nor in the result type, can be locally bound and discharged. A result closure that captures an object can keep the object's region visible in its type information, preventing premature reclamation.

At another call, the same function can receive a different `r_out`. This separates the lifetime of the function's code from the lifetimes of its results without generating a different function body for each destination.

The method guarantees safe use of regions under its translation, not minimal memory use. Values sharing one region survive until that region is reclaimed even if some become individually unreachable earlier.

## Concepts and terms

**[1] Region.** A collection of allocated values reclaimed together. `letregion r in e end` creates a region, evaluates `e`, and deallocates the region when `e` returns.

**[2] Region and effect inference.** A static analysis extending type inference with allocation places and access effects such as reading or writing a region. Unification groups compatible values; effect information determines safe region boundaries.

**[3] Region polymorphism.** Parameterizing a function over region names, allowing callers to select concrete regions for its arguments and results. The translation also permits a restricted form of polymorphic recursion in these region parameters.


# A Fast Fourier Transform Compiler

**Summary by:** GPT 6 Astra

**Author:** Matteo Frigo

**Source:** PLDI 1999; SIGPLAN Most Influential PLDI Paper Award, 2009

**Link:** https://doi.org/10.1145/301618.301661

**Code:** [FFTW](https://www.fftw.org/)

## Key insight

Generate small Fourier-transform kernels from mathematical decompositions, then simplify their arithmetic graph before asking a conventional compiler to produce machine code.

## Basic idea

The `genfft` compiler constructs an expression graph [1] for a fixed-size discrete Fourier transform [2]. It simplifies algebra, shares common subexpressions, and can specialize for real inputs. A scheduling phase [3] orders the graph to limit temporary-storage traffic, then emits a C codelet [4]. The paper concerns generation of these kernels, distinct from selecting a complete execution plan for an arbitrary large transform.

## Illustrative example

**Generate.** For four real inputs `a,b,c,d`, define the forward transform using coefficients `exp(-2*pi*i*k*j/4)`. An unsimplified generator can expand all four outputs as complex sums, including multiplications by zero, one, minus one, and the imaginary unit.

**Simplify.** Create shared real temporaries `s = a+c`, `t = b+d`, `u = a-c`, and `v = b-d`. The outputs are `X0 = s+t`, `X2 = s-t`, `X1 = u-i*v`, and `X3 = u+i*v`. Multiplication by the imaginary unit becomes placement and sign change of real components, not a general complex multiplication. The conjugate relationship between the last two outputs follows from the real-input restriction.

**Check.** For inputs `(1,2,4,8)`, the temporaries are `(5,10,-3,-6)`. Therefore the transform is `(15, -3+6i, -5, -3-6i)`. These numbers can be checked directly against the defining four-term sums.

**Schedule.** Emit the two sums and their outputs, then the two differences and their outputs, rather than keeping every intermediate alive until the end. For larger graphs, recursive graph partitioning seeks useful evaluation orders without assuming a particular register count. Algebraic simplification preserves the mathematical transform; floating-point implementations still have rounding behavior, so mathematical equality is not a promise of bitwise equality with every alternative evaluation order.

## Concepts and terms

**[1] Expression graph.** A directed acyclic graph whose nodes are operations and whose edges carry values; multiple users can share one computed node.

**[2] Discrete Fourier transform.** For length `N`, output `k` is the sum of input `j` times `exp(-2*pi*i*k*j/N)` over all `j`.

**[3] Scheduling.** Choosing a dependency-respecting evaluation order, including when temporary values become dead.

**[4] Codelet.** A generated kernel specialized for a fixed transform size and input/output form.

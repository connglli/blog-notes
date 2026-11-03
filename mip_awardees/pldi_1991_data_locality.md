# A Data Locality Optimizing Algorithm

**Summary by:** GPT 6 Astra

**Author:** Michael E. Wolf, Monica S. Lam

**Source:** PLDI 1991; SIGPLAN Most Influential PLDI Paper Award, 2001

**Link:** https://doi.org/10.1145/113445.113449

## Key insight

Reusing a value is useful only if its reuse occurs while it remains in fast memory; loop transformations should organize iteration order around that requirement.

## Basic idea

The algorithm models reuse [1] in array accesses whose indices are integer-linear functions of loop counters plus constants, and uses unimodular transformations [2] to combine loop interchange, reversal, and skewing. Dependence legality [3] restricts which transformed orders are permitted. Tiling [4] then makes reuse in several dimensions occur within smaller working sets. The method addresses suitable perfectly nested loops; cache conflicts and tile sizes still affect actual performance.

## Illustrative example

**Computation.** Compute a matrix product with updates `C[i,j] += A[i,k] * B[k,j]`, starting from zeroed C. Assume the arrays do not overlap, use row-major layout, and preserve increasing `k` for each C element. Take all dimensions to be four for a small illustration.

**Reuse analysis.** `A[i,k]` is reused as `j` varies, `B[k,j]` as `i` varies, and `C[i,j]` across `k`. An `i,j,k` loop order keeps one C element active, but traverses B down a column in the inner loop. Changing to `i,k,j` accesses contiguous elements of B and C while reusing one A element.

**Legality.** Exchanging `j` and `k` is a coordinate permutation with determinant minus one, hence unimodular. Updates to distinct C elements are independent under the nonaliasing assumption. For each fixed `(i,j)`, `k` still increases, so this transformation preserves the accumulation order, including for floating-point addition.

**Tiling.** Split i, j, and k into blocks of size two. For one output block, process a two-by-two A block and a two-by-two B block, accumulating into a two-by-two C block. These three blocks contain twelve scalar slots in this illustration. Move through k blocks in increasing order before completing that output block. If these working data fit in cache, their nearby repeated accesses can reuse cached values. A size-two tile is illustrative, not a universal optimum or a guarantee against cache-set conflicts.

## Concepts and terms

**[1] Reuse.** Multiple accesses to the same value, or to nearby values sharing a cache line; temporal proximity turns potential reuse into locality.

**[2] Unimodular transformation.** An integer matrix with determinant plus or minus one, giving an invertible change of integer iteration coordinates.

**[3] Dependence legality.** Operations that must retain their order remain forward ordered under the transformed loop schedule.

**[4] Tiling.** Partitioning an iteration domain into blocks whose accesses are executed close together.

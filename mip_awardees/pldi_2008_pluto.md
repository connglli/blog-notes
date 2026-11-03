# A Practical Automatic Polyhedral Parallelizer and Locality Optimizer

**Summary by:** GPT 6 Astra

**Author:** Uday Bondhugula, Albert Hartono, J. Ramanujam, P. Sadayappan

**Source:** PLDI 2008; SIGPLAN Most Influential PLDI Paper Award, 2018

**Link:** https://doi.org/10.1145/1375581.1375595

**Code:** [Pluto](https://github.com/bondhugula/pluto)

## Key insight

Choose loop transformations with tiling and communication in mind, rather than maximizing fine-grained parallelism first and treating locality as an afterthought.

## Basic idea

Pluto represents suitable loop iterations and dependences in the polyhedral model [1]. It solves integer linear constraints for affine transformations [2] that respect dependences [3] while limiting producer-to-consumer distances. Compatible transformation dimensions form permutable bands [4] that can be tiled [5], after which code generation exposes legal parallel execution. The formulation selects transformations, not a universally optimal tile size or hardware performance guarantee.

## Illustrative example

**Dependences.** Consider cells `grid[i,j] = grid[i-1,j] + grid[i,j-1]` for `1 <= i,j <= 4`, with initialized row 0 and column 0. Use exact arithmetic. Cell `(i,j)` depends on `(i-1,j)` and `(i,j-1)`, giving forward dependence differences `(1,0)` and `(0,1)`.

**Transformation.** The original two dimensions already form a permutable band because both dependence components are nonnegative. Divide each dimension into tiles of size two: tile `(I,J)` contains rows `2I+1..2I+2` and columns `2J+1..2J+2`.

**Scheduling.** Tile `(0,0)` executes first, using row-major order internally. Tiles `(0,1)` and `(1,0)` may then execute in parallel: each needs completed boundary values from `(0,0)`, but neither depends on the other. Tile `(1,1)` waits for both. More generally, tile diagonals with equal `I+J` can run in parallel after earlier diagonals finish.

**Locality.** Completing a small tile keeps many producer values close to their consumers, while synchronizing between tiles rather than individual cells. Simply parallelizing all four tiles would be incorrect. For harder loop nests, Pluto finds affine skewing, fusion, and other transformations that create suitable bands; the small example shows the dependence constraints and resulting tiled execution without claiming a particular solver must choose size two.

## Concepts and terms

**[1] Polyhedral model.** Integer points describe statement executions; affine inequalities describe iteration domains and dependence relations.

**[2] Affine transformation.** New coordinates formed from integer linear combinations of iteration indices and parameters, plus constants.

**[3] Dependence.** An ordering requirement between operations that access shared data and cannot safely be reversed.

**[4] Permutable band.** A group of loop dimensions whose relevant dependence components are nonnegative, allowing permutation and rectangular tiling.

**[5] Tiling.** Grouping neighboring iteration points into blocks, with both inter-block and intra-block orders respecting dependences.

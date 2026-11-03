# Automatically Characterizing Large Scale Program Behavior

**Summary by:** GPT 6 Astra

**Author:** Timothy Sherwood, Erez Perelman, Greg Hamerly, Brad Calder

**Source:** ASPLOS 2002; ASPLOS Influential Paper Award 2017

**Link:** https://doi.org/10.1145/605397.605403

**Code:** [SimPoint project and downloads](https://cseweb.ucsd.edu/~calder/simpoint/)

## Key insight

A long execution often revisits similar mixtures of code. Identify those recurring phases, simulate representative intervals in detail, and weight their measurements by how much of the execution they represent.

## Basic idea

The method divides execution into fixed instruction-count intervals and summarizes each with a basic-block vector [1]. Dimension reduction and clustering [2] group intervals with similar code-execution distributions. A real interval near each cluster's center becomes a simulation point [3]. Weighted statistics [4] estimate whole-program behavior, subject to representative phases and appropriate architectural-state warmup.

## Illustrative example

**Profile intervals.** A toy program has four equal-length intervals and two dominant basic blocks. The normalized instruction contributions are `(0.8, 0.2)` in three intervals and `(0.2, 0.8)` in the fourth. Counting only block entries would distort this comparison if the blocks had different lengths, so each entry count is multiplied by its block's instruction count first.

**Choose representatives.** Cluster the first three intervals together and the fourth separately. Select one actual interval from each group, not the mathematical centroid itself, because a centroid is not an executable program location. Their weights are three quarters and one quarter.

**Simulate and combine.** Suppose detailed simulation yields two and six cycles per instruction for the representatives. The estimated whole-program cost is `0.75*2 + 0.25*6 = 3` cycles per instruction. Its reciprocal is one third of an instruction per cycle. Directly averaging the two IPC values with these instruction-fraction weights would give the wrong rate.

**Prepare the state.** Fast-forwarding to a representative must also provide suitable cache, predictor, and other architectural state before measurement. Starting each selected interval with empty caches measures a different experiment. Similar basic-block proportions are evidence of a recurring phase, not a proof that every memory-access pattern inside it is identical.

## Concepts and terms

**[1] Basic-block vector.** One coordinate per static basic block, containing executions of that block multiplied by its instruction count. Normalize by the interval's total instruction contribution. The vector summarizes where execution occurs but discards the exact order of instructions and their data addresses.

**[2] Projection and clustering.** Random linear projection reduces vector dimensionality, and k-means groups nearby projected points. A model-selection score balances fit against the number of clusters. The paper's algorithm compares candidate cluster counts rather than assuming every loop is automatically a distinct phase.

**[3] Simulation point.** The start of a selected real interval whose vector is close to a cluster center. Detailed simulation runs that interval, while less expensive execution can reach it and establish state. The selected points depend on the program, its input, and the collected execution.

**[4] Weighting and limits.** A cluster's weight reflects the fraction of the profiled execution it represents. Combine counts or suitably normalized costs before forming rates. Sampling can miss unusual behavior, and code similarity need not guarantee identical microarchitectural behavior. The technique estimates performance; it is not exhaustive functional verification.

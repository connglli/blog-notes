# The Cache Performance and Optimizations of Blocked Algorithms

**Summary by:** GPT 6 Astra

**Author:** Monica S. Lam, Edward E. Rothberg, Michael E. Wolf

**Source:** ASPLOS 1991; ASPLOS Influential Paper Award 2021

**Link:** https://doi.org/10.1145/106973.106981

## Key insight

A tile can fit within a cache's capacity and still perform badly because its addresses map to too few cache locations. Choosing a blocking factor therefore requires reasoning about cache conflicts and layout, not only counting the tile's bytes.

## Basic idea

Blocking [1] rearranges loop work to reuse a small part of a larger dataset. The paper models interference misses [2] to explain why performance can vary sharply with matrix dimensions and block size. It uses that model to guide blocking choices and considers copying data into a favorable temporary layout [3]. The useful optimization depends on both reuse and the actual cache mapping [4].

## Illustrative example

**Fit the capacity.** Consider a toy direct-mapped cache with four sets and one matrix element per line. A two-by-two tile contains four elements, so a capacity-only argument says it fits. Let the original matrix row stride be four elements and its base address be zero.

**Check the mapping.** The tile's element addresses are `0, 1, 4, 5`. Using `address modulo 4` as the set index, they map to sets `0, 1, 0, 1`. Accessing the second row evicts the first even though sets 2 and 3 remain unused. Repeating the tile traversal therefore loses reuse that the capacity calculation predicted.

**Change the layout.** A row stride of six gives addresses `0, 1, 6, 7`, occupying all four sets. Alternatively, copying the tile into consecutive temporary locations `0, 1, 2, 3` also removes this tile's self-conflicts. Neither change automatically removes conflicts with other arrays accessed by the computation.

**Pay for the improvement.** Copying requires extra reads and writes. It helps only if enough later reuse compensates for that cost. Reducing the tile size may avoid a problematic mapping without copying, but can also reduce available reuse. The example illustrates the model's purpose rather than asserting one universally optimal block size.

## Concepts and terms

**[1] Blocking.** Partition iteration and data spaces so several operations reuse a bounded working region before moving on. A block size changes both the amount of reuse and the access pattern. It does not alter mathematical results when the transformation preserves the program's dependence requirements.

**[2] Interference miss.** A reused cache line has been displaced by another access. Self-interference arises among locations of the same array; cross-interference arises between different arrays. Matrix stride and cache size can create systematic collisions that are invisible in a total-byte estimate.

**[3] Copying optimization.** Place selected data in a contiguous temporary buffer with a controlled layout, then execute the repeatedly using computation against it. The copying overhead and extra storage must be included in the cost model. Copying is not useful merely because it reduces the miss rate of the inner kernel.

**[4] Cache mapping and model scope.** Cache line size, number of sets, associativity, and replacement behavior constrain which data can coexist. The toy example uses a direct-mapped organization for clarity. The paper's analytical treatment and experiments motivate informed selection, not a universal cache-independent blocking constant.

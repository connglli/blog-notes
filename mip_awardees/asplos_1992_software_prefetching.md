# Design and Evaluation of a Compiler Algorithm for Prefetching

**Summary by:** GPT 6 Astra

**Author:** Todd C. Mowry, Monica S. Lam, Anoop Gupta

**Source:** ASPLOS 1992; ASPLOS Influential Paper Award 2022

**Link:** https://doi.org/10.1145/143371.143488

## Key insight

Prefetch early enough to overlap a future cache miss with useful computation, but avoid issuing prefetches for accesses already served by locality. Address calculations, redundant requests, and added control flow can otherwise erase the benefit.

## Basic idea

The compiler analyzes regular array references and their temporal and spatial locality [1] to derive prefetch predicates [2]. Loop splitting [3] isolates iterations needing prefetches without necessarily adding a conditional to every iteration. Software pipelining [4] moves the requests ahead of their eventual uses. The method targets predictable access patterns and evaluates total execution cost, not merely the number of demand misses removed.

## Illustrative example

**Analyze a loop.** A loop reads consecutive entries of an aligned array and performs computation on each entry. Suppose a cache line holds four entries. Under a simple streaming model, the first access to each line may miss, while its next three accesses reuse that line.

**Select requests.** A locality-derived condition identifies one prefetch per four elements, rather than one per element. Another scalar value reused throughout the loop needs no repeated prefetch after it is resident. These decisions assume that the predicted reuse survives intervening cache activity.

**Split and schedule.** Unroll the streaming loop in groups of four so a prefetch can occur once per group. If the modeled memory delay is eight cycles and useful work takes two cycles per element, starting approximately four iterations ahead provides the desired overlap. Peel or otherwise handle startup and the end boundary separately so the transformed loop remains valid. These timing numbers define the toy model, not an evaluation result.

**Check the tradeoff.** Prefetching only when the element is needed is too late to hide its delay. Prefetching much earlier can evict the data before use. Issuing a request for every element adds redundant traffic and instructions. The compiler must balance these costs with its estimated latency and locality.

## Concepts and terms

**[1] Locality analysis.** Temporal reuse accesses the same value again; spatial reuse accesses other values in the same cache line; group reuse occurs across different references to related locations. Reuse becomes useful locality only if intervening accesses do not evict the data. The compiler reasons about affine array subscripts and loop structure rather than arbitrary pointer-chasing behavior.

**[2] Prefetch predicate.** A condition on iteration indices identifying the accesses expected to fetch new data. First-iteration conditions capture temporal locality; modular conditions capture cache-line boundaries. Combined reuse can reduce several references to one leading request.

**[3] Loop splitting.** Peeling separates selected iterations, while unrolling groups periodic ones. This can implement prefetch predicates without testing them repeatedly inside the original inner loop. Code growth may make splitting unattractive, so it is itself a cost tradeoff.

**[4] Software-pipelined prefetch.** Issue a request during earlier iterations and consume its data later. The lead distance depends on expected latency and loop execution time. A prefetch is a performance hint, not a replacement for the program's load or its correctness requirements; missed predictions or inadequate bandwidth can reduce or reverse the speedup.

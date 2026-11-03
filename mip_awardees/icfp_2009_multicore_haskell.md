# Runtime support for multicore Haskell

**Summary by:** GPT 6 Astra

**Author:** Simon Marlow, Simon Peyton Jones, and Satnam Singh

**Source:** ICFP 2009; SIGPLAN Most Influential ICFP Paper Award 2019.

**Link:** https://doi.org/10.1145/1596550.1596563

**Code:** [Glasgow Haskell Compiler project](https://github.com/ghc/ghc)

**Artifact:** [Nofib benchmark suite](https://github.com/ghc/nofib)

## Key insight

Pure computation supplies safe opportunities for parallel evaluation, but the runtime must distribute work without making the sequential path too expensive. Scheduling, sharing, and memory management jointly determine whether those opportunities become speedups.

## Basic idea

The paper studies semi-explicit parallel Haskell, where `par` creates a spark [1] suggesting work and `pseq` imposes a useful evaluation order [2]. Per-processor execution contexts [3] maintain work queues, allocation state, and runnable threads. Work stealing [4], parallel collection, and coordination on shared thunks [5] distribute execution while controlling overhead. A spark is optional parallel work, not a guaranteed new operating-system thread or a promise of speedup.

## Illustrative example

**Program.** Two pure computations produce integer results `left` and `right`. Use the expression `par left (pseq right (left + right))`. It sparks evaluation of `left`, evaluates `right` in the current computation, and then adds the results.

Suppose evaluating `left` takes roughly as much work as evaluating `right`. On one processor the spark may never be executed separately; demand from the addition still computes the correct result. On two processors, an idle execution context may take the spark while the first context works on `right`.

**Scheduling.** Place the spark in the local queue. A worker normally handles local work and can steal older sparks from another context's queue when it runs out. The queue must synchronize competing accesses, but local operations should avoid unnecessary shared locking.

The runtime can reuse a worker thread to process several sparks rather than creating a fresh heavyweight thread for every candidate expression. A spark whose value is already evaluated provides no useful work.

**Shared demand.** If the first worker reaches the addition while another worker is evaluating `left`, it encounters a shared thunk under evaluation. Black-hole machinery records this condition and can arrange waiting and wakeup instead of uncontrolled repeated evaluation. The paper evaluates tradeoffs in how eagerly to install such markers; it does not require every race to be eliminated at any cost.

**Memory.** Both computations allocate, so their speed also depends on collection and memory traffic. Increasing the number of runnable sparks does not help if they are too small, retain unnecessary data, or spend most time contending over runtime structures.

## Concepts and terms

**[1] Spark.** A reference to a thunk offered as candidate parallel work. The runtime may evaluate it on another processor, discard it as redundant, or leave ordinary demand to evaluate it.

**[2] Evaluation order.** `pseq a b` evaluates `a` to weak-head normal form before continuing with `b`. For an integer this exposes the number; for a list it exposes only the outer constructor, not every element.

**[3] Execution context.** GHC's per-processor runtime structure containing the resources needed to execute Haskell threads.

**[4] Work stealing.** An idle worker takes queued work from another worker, distributing tasks without central assignment of each spark.

**[5] Shared thunk.** A deferred computation referenced from several places. A black hole marks evaluation in progress and supports coordination among threads demanding that computation.


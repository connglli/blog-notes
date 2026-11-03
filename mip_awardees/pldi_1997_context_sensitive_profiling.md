# Exploiting Hardware Performance Counters with Flow and Context Sensitive Profiling

**Summary by:** GPT 6 Astra

**Author:** Glenn Ammons, Thomas Ball, James R. Larus

**Source:** PLDI 1997; SIGPLAN Most Influential PLDI Paper Award, 2007

**Link:** https://doi.org/10.1145/258915.258924

**Documentation:** [PP path profiler](https://pages.cs.wisc.edu/~larus/pp.html)

## Key insight

A procedure's aggregate cost can hide radically different behavior along its internal paths and under different callers.

## Basic idea

The profiler associates hardware-counter measurements [1] with intraprocedural paths [2] and distinguishes procedure invocations through a calling context tree [3]. Path instrumentation identifies the executed path and accumulates its measured costs. Repeated invocations with the same context share records instead of storing a complete dynamic call tree. Instrumentation perturbation [4] remains a limitation: the observed hardware events are not automatically the events of an untouched execution.

## Illustrative example

**Program.** `main` calls `interactive` and `batch`; both call `lookup`. Inside `lookup`, one path checks a small cache and returns, while another scans a larger table. Suppose ten interactive calls each incur one measured cache miss and two batch calls each incur twenty. These are invented measurements.

**Path measurement.** At the beginning of a measured path, clear the event counter. At its end, read the counter and add the value to that path's accumulator, alongside an execution count. If the path calls another procedure, save and restore the counter around that nested execution according to the profiling convention, rather than inadvertently charging all callee events to the caller path.

**Context records.** Maintain separate tree paths `main -> interactive -> lookup` and `main -> batch -> lookup`. Repeated interactive calls reuse the first lookup record. Its measured miss total is ten, whereas the second record's total is forty. A single aggregate of fifty misses over twelve calls, about 4.17 each, describes neither invocation class well.

**Interpretation.** Keeping path identities can further separate lookup's fast and scanning paths. The data suggests investigating the batch scan, but does not prove that every miss was caused by original lookup instructions: added profiling accesses may disturb the cache. A complete implementation must also handle recursion, nonlocal returns, and finite counter widths; the simple nonrecursive example avoids those complications rather than assuming they do not exist.

## Concepts and terms

**[1] Hardware counter.** A processor facility counting selected events, such as cycles or cache misses, over an execution interval.

**[2] Intraprocedural path.** A sequence of control-flow edges within one procedure; loop boundaries break an unbounded execution into manageable path segments.

**[3] Calling context tree.** A compact representation distinguishing call chains while aggregating repeated occurrences of the same context.

**[4] Instrumentation perturbation.** Changes in measured execution caused by the act of observing it, including additional instructions and altered cache behavior.

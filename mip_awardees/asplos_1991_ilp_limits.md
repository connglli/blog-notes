# Limits of Instruction-Level Parallelism

**Summary by:** GPT 6 Astra

**Author:** David W. Wall

**Source:** ASPLOS 1991; ASPLOS Influential Paper Award 2016

**Link:** https://doi.org/10.1145/106972.106991

## Key insight

Very high parallelism under perfect prediction and unlimited resources does not imply similar parallelism under merely good mechanisms. The useful question is which assumptions remove each dependency and how the remaining limitations interact.

## Basic idea

Wall uses instruction-trace simulation [1] to measure parallelism under controlled assumptions. The experiments vary register renaming [2], memory-dependence knowledge [3], branch prediction, and the instruction window [4]. Comparing ideal and constrained cases reveals how much optimistic mechanisms can inflate the apparent opportunity. These are limits within a trace and machine model, not direct predictions of achievable processor speedup.

## Illustrative example

**Build a dependency chain.** A trace loads a value into `r1`, computes `r2 = r1 + 1`, then assigns an unrelated constant to `r1`. The computation of `r2` truly depends on the load, while the later assignment must wait only because it reuses the name `r1` before the earlier value has been consumed.

**Remove only false dependencies.** Give the later assignment a different physical register. It can overlap with independent work, but the addition still cannot use the load's result before it exists. Renaming does not remove true data dependence.

**Expose memory uncertainty.** Add a store through pointer `target` near a load through pointer `source`. An ideal trace model knows their actual addresses and can separate them when different. A conservative mechanism may serialize them when it cannot establish that fact soon enough. Measuring the ideal case therefore includes knowledge unavailable to a real scheduler at the relevant time.

**Limit the view.** Put another independent operation beyond an unresolved branch and outside a small scheduling window. Perfect prediction and a larger window can expose it; a finite window or misprediction boundary can prevent that overlap. Improving one mechanism alone may leave the other as the limiting factor.

## Concepts and terms

**[1] Trace-driven parallelism measurement.** Observe the dynamic instructions of a particular program execution and pack them into modeled cycles subject to selected constraints. The ratio of instruction count to cycle count measures parallelism under that model. Different inputs can produce different traces, and modeled cycles omit costs unless explicitly included.

**[2] Register renaming.** Map successive definitions of one architectural register to distinct physical storage. This removes output and anti-dependencies caused by reusing names, while preserving true producer-consumer dependencies. Unlimited renaming is an upper-limit assumption, not a free hardware implementation.

**[3] Alias knowledge.** Determine whether memory references access overlapping locations and thus must preserve order. Perfect knowledge uses actual trace addresses; realistic mechanisms may learn them too late or remain conservative. The paper studies the effect of this uncertainty separately from register naming.

**[4] Prediction and window.** Branch prediction determines which future instructions are available along an assumed path; the instruction window bounds how far the scheduler can search for parallel work. Their effects interact with dependencies and renaming. An optimistic scheduling result does not account automatically for clock frequency, recovery latency, cache behavior, or implementation complexity.

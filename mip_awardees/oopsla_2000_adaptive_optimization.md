# Adaptive Optimization in the Jalapeño JVM

**Summary by:** GPT 6 Astra

**Author:** Matthew Arnold, Stephen Fink, David Grove, Michael Hind, Peter F. Sweeney

**Source:** OOPSLA 2000; SIGPLAN Most Influential OOPSLA Paper Award, 2010

**Link:** https://doi.org/10.1145/353171.353175

**Code:** [Jikes RVM](https://github.com/JikesRVM/JikesRVM)

## Key insight

Recompile when estimated future execution savings exceed compilation cost, using ongoing measurements even after code has been optimized.

## Basic idea

Jalapeño's adaptive optimization system separates runtime measurement [1], a controller [2], and background recompilation [3]. Samples identify costly methods; the controller selects compilation plans using an estimated cost-benefit model. Compiler and profiling components communicate through queues and shared analysis information. Continued observation permits further decisions as execution changes, but forecasts and average speedup estimates can be wrong.

## Illustrative example

**Measure.** A service has run for ten seconds. Decayed execution samples attribute about one fifth of recent execution to `parsePacket`. Use the paper's simple horizon heuristic: predict that the program will run for another ten seconds. Without recompilation, the estimated remaining time in this method is two seconds.

**Choose.** Suppose one optimization level costs 0.2 seconds to compile and is expected to double method speed, giving total predicted cost `0.2 + 2/2 = 1.2` seconds. A stronger level costs 0.8 seconds and is expected to triple speed, giving about `0.8 + 2/3 = 1.47` seconds. Choose the first level, since 1.2 is lower than both 1.47 and the two-second no-recompile estimate. These costs and speedups are illustrative.

**Compile.** Enqueue a plan carrying the chosen optimizations and relevant profile information. A compiler thread builds the new method version while application execution continues. This background recompilation differs from compiling a never-before-invoked method in the requesting application thread.

**Reassess.** If subsequent samples show that packet parsing is rare, recompiling it again may not repay the cost. If the program terminates immediately after the first decision, the predicted savings never materialize. The decision procedure optimizes an estimate, not knowledge of future inputs. Sampling optimized code as well as initial code prevents the policy from becoming blind to a method simply because it has already received one optimization pass.

## Concepts and terms

**[1] Runtime measurement.** Low-overhead sampling or instrumentation collecting facts about actual execution; older samples can be downweighted.

**[2] Controller.** The component deciding what to measure and whether estimated compilation cost plus optimized future time beats leaving code unchanged.

**[3] Background recompilation.** Producing a replacement for an existing compiled method in separate runtime threads, with an explicit optimization and instrumentation plan.

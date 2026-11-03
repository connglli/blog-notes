# ATOM: A System for Building Customized Program Analysis Tools

**Summary by:** GPT 6 Astra

**Author:** Amitabh Srivastava, Alan Eustace

**Source:** PLDI 1994; SIGPLAN Most Influential PLDI Paper Award, 2004

**Link:** https://doi.org/10.1145/178243.178260

## Key insight

Many profilers and simulators need the same executable-editing machinery; their differences can be expressed as where to insert calls and what those calls compute.

## Basic idea

ATOM performs link-time instrumentation [1] using separate instrumentation and analysis routines [2]. The instrumentation traverses procedures, basic blocks [3], and instructions to select observation points. The resulting executable calls analysis code directly in the same address space, avoiding a mandatory full execution trace and separate trace-processing process. ATOM preserves application state and presents original program addresses where required by its interface.

## Illustrative example

**Tool definition.** Count entries into each basic block of a single-threaded application. At instrumentation time, give every block an integer identifier. Insert `count[id] += 1` through a small analysis routine at each block entry, plus initialization and final reporting calls. Assume the counters do not overflow and execution terminates normally.

**Build.** Feed the program's object-module representation and the two kinds of routines into ATOM. It produces a new executable containing both application and analysis code. The instrumentation traversal does not run on every application event; only the inserted analysis calls do.

**Run.** Suppose the path is `Entry, Loop, Body, Loop, Body, Loop, Exit`. The report records counts 1, 3, 2, and 1 for those four blocks. No disk record of all seven transitions is necessary when counts are the desired result. A different tool could insert calls only at memory operations and maintain a simulated cache instead.

**Preservation.** The count routine must not overwrite live application registers. Its variables and library state are distinct from the application's. If a report identifies an instruction address, relocating the instrumented text must not make that address masquerade as the original location. Preserving these functional observations does not mean execution timing or the physical cache effects of the instrumentation are unchanged.

## Concepts and terms

**[1] Link-time instrumentation.** Rewriting the assembled program representation before execution to add observations.

**[2] Instrumentation and analysis routines.** The former chooses inserted calls and their arguments; the latter executes those calls to collect or interpret runtime information.

**[3] Basic block.** A straight-line instruction sequence with one entry and no internal control transfer, allowing one entry counter to represent its executions under the assumed execution model.

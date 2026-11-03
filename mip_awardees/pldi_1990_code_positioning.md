# Profile Guided Code Positioning

**Summary by:** GPT 6 Astra

**Author:** Karl Pettis, Robert C. Hansen

**Source:** PLDI 1990; SIGPLAN Most Influential PLDI Paper Award, 2000

**Link:** https://doi.org/10.1145/93542.93550

## Key insight

Frequently adjacent execution should usually occupy nearby addresses, even when source order places unrelated or rarely executed code between those instructions.

## Basic idea

Execution profiles [1] guide procedure clustering, basic-block chaining [2], and procedure splitting [3]. Frequently communicating procedures are placed together, while heavily traversed block edges become straight-line layout where possible. Cold code is separated without removing its behavior. The goal is improved instruction locality [4] and fewer costly transfers, not a guarantee that one training profile predicts every workload.

## Illustrative example

**Profile.** A parser has blocks `Start`, `Token`, `Accept`, `Error`, and `Done`. In a training run, `Start -> Token` executes 100 times, `Token -> Accept` 95 times, `Token -> Error` five times, and both alternatives reach `Done`. A separate recovery procedure is never called in this run.

**Chains.** Begin with one chain per block. Process edges from highest count downward. Merge `Start` with `Token`, then append `Accept` and `Done` when their edges join a chain tail to another chain head. The edge to `Error` cannot also make it the fall-through successor of `Token`, since `Token` is already inside the main chain.

**Layout.** Place the hot chain contiguously and place `Error` elsewhere, with the branch condition and jumps adjusted to preserve every original successor. Move the unexecuted recovery body out of the hot code area, but keep it callable. A zero profile count means unobserved, not unreachable.

**Procedure placement.** If the parser frequently calls a scanning procedure, place their procedure regions near one another using the measured call relationship. This may reduce the number of instruction pages needed for common work. The arrangement can perform differently on an input dominated by errors, and even frequent neighbors can conflict in a particular cache. The profile is an optimization input, not a semantic assumption.

## Concepts and terms

**[1] Execution profile.** Counts of observed calls and control-flow edges from representative runs.

**[2] Basic-block chain.** A sequence of straight-line blocks chosen for contiguous placement, generally connecting hot successor edges as fall-throughs.

**[3] Procedure splitting.** Physically separating cold portions of a procedure from its main body while retaining necessary branches.

**[4] Instruction locality.** Executing code close in address and time, improving opportunities for reuse of instruction-cache lines and translated pages.

# A Simpler, Safer Programming and Execution Model for Intermittent Systems

**Summary by:** GPT 6 Astra

**Author:** Brandon Lucia, Benjamin Ransford

**Source:** PLDI 2015; SIGPLAN Most Influential PLDI Paper Award, 2025

**Link:** https://doi.org/10.1145/2737924.2737978

## Key insight

Restarting saved control flow is insufficient when persistent memory contains writes performed after that saved point. Recovery must restore matching versions of both kinds of state.

## Basic idea

DINO divides execution at programmer-placed task boundaries [1]. Each boundary checkpoints volatile state [2] and versions nonvolatile variables [3] identified by analysis as potentially inconsistent on reexecution. After power loss, recovery restores both and restarts at the last completed boundary. This provides task-atomic memory behavior [4], assuming the device eventually has enough energy to complete a task.

## Illustrative example

**Setup.** A small energy-harvesting device maintains persistent integers `count = 4` and `sum = 20`. A sampled value `sample = 7` is in volatile memory. A task adds the sample to the sum and increments the count, with a boundary before and after these two updates. Assume arithmetic does not overflow and this task performs no external output.

**Failure without matching versions.** Execution writes `sum = 27`, then loses power before incrementing `count`. Restoring just the saved instruction position and `sample` reexecutes the addition against 27, producing 34. The final count becomes 5, but the one new sample was counted twice in the sum.

**Checkpoint and recovery.** At the starting boundary, DINO saves the old `sum` and `count` with the register and stack state. After the same failure, recovery restores `(20, 4, 7)`. Reexecution produces `(27, 5)`. The ending boundary makes that completed state the restart point for the next task.

**Boundary interruption.** Checkpoints are double buffered and marked complete only after writing finishes. If power fails during checkpoint construction, recovery selects the earlier complete checkpoint. Repeated failures may repeat work, but do not justify selecting a partially written checkpoint. The example's memory argument does not make a radio transmission or physical actuator effect undoable.

## Concepts and terms

**[1] Task boundary.** A static program point delimiting dynamic paths of execution. A task is the path between consecutive boundary crossings, not necessarily a lexical block.

**[2] Volatile state.** Registers and memory that lose their contents without power. A checkpoint copies the necessary execution state into persistent storage.

**[3] Nonvolatile variable version.** A saved value used to undo partial persistent updates; restoring only volatile state would leave those updates in place.

**[4] Task-atomic memory behavior.** Recovery exposes a consistent boundary state rather than a partially completed task. Atomicity does not guarantee that power will last long enough for progress.

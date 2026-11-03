# The Structure of the "THE"-Multiprogramming System

**Summary by:** GPT 6 Astra

**Author:** Edsger W. Dijkstra

**Source:** SOSP 1967; Communications of the ACM 11(5), 1968; SIGOPS Hall of Fame Award 2005

**Link:** https://doi.org/10.1145/800001.811672

## Key insight

A system becomes easier to reason about when each layer hides one class of low-level activity behind a stable abstraction. Explicit synchronization then describes cooperation without depending on accidental relative execution speeds.

## Basic idea

THE organizes operating-system activities as sequential processes [1] arranged in a strict hierarchy [2]. Lower layers implement processor allocation and storage management, while higher layers use logical processes and segments [3] instead of managing those physical details again. Explicit synchronization [4] prevents a process from using unavailable data or a busy resource. Construction and testing proceed from lower layers upward, so higher-level arguments can assume the abstractions already established. The paper reports a disciplined design and verification method, not a modern machine-checked proof of the entire implementation.

## Illustrative example

**Start with processor allocation.** A user computation prepares output while a device process sends previously prepared output to a printer. The processor-allocation layer schedules whichever processes are eligible. Neither process assumes that it receives a fixed number of instructions for every instruction of the other; synchronization determines when progress is logically permitted.

**Hide storage movement.** The producer records output in logical segment S. The segment controller arranges where S's data resides in core or on backing storage. The output-buffering process refers to S, not to a drum address chosen independently by the producer. Relocating S therefore changes storage-controller bookkeeping without changing the meaning of the output request.

**Synchronize use.** The producer cannot announce an output segment as ready before its contents are complete. The consumer cannot reuse the buffer while the producer still owns it. A semaphore-style readiness signal permits the consumer to wait until data exists, while a corresponding availability signal controls reuse. Checking elapsed time instead would fail whenever the producer or device runs more slowly than expected.

**Reason by layer.** Test processor allocation with cooperating test processes that provoke the relevant scheduling situations. Then test segment movement using those process abstractions. Finally test the output-buffering layer assuming logical segments behave correctly. The printer layer need not enumerate every interleaving of clock interrupts and backing-store interrupts because those details belong to lower-layer obligations.

The actual THE hierarchy also includes a console-message interpreter between storage management and buffered peripherals, so device processes can communicate with the operator through an established abstraction. The example focuses on the dependency principle rather than replacing the paper's hierarchy with an invented inventory.

Layering alone does not remove deadlock or a bad specification. Each abstraction must be implemented correctly, synchronization dependencies must permit required progress, and tests must cover the relevant modeled states. Its benefit is to make these obligations separable enough to reason about.

## Concepts and terms

**[1] Sequential process.** A sequence of state changes whose local order matters but whose speed relative to other processes is unspecified. The machine can multiplex several such processes on available processors.

**[2] Strict hierarchy.** An arrangement in which higher-level mechanisms rely on lower-level abstractions rather than reimplementing or depending on their hidden physical details.

**[3] Segment.** A logical information unit managed independently of the core and backing-store pages currently holding it. Higher layers use its identity instead of a fixed physical location.

**[4] Explicit synchronization.** Operations constraining when processes may proceed. A semaphore can represent available permits or events; waiting blocks progress until the required condition has been established by another process.

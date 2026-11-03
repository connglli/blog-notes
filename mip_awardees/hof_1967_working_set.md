# The Working Set Model for Program Behavior

**Summary by:** GPT 6 Astra

**Author:** Peter J. Denning

**Source:** SOSP 1967; Communications of the ACM 11(5), 1968; SIGOPS Hall of Fame Award 2005

**Link:** https://doi.org/10.1145/800001.811670

## Key insight

A process's recently used pages provide an estimate of the memory it needs to run efficiently. Scheduling more work than memory can support can increase paging instead of useful computation.

## Basic idea

The working set [1] contains pages referenced during a chosen window of process time [2]. It estimates memory demand [3] rather than prescribing one fixed allocation for a process's lifetime. Memory management and scheduling are coupled: a process should run only when enough memory is available for its working set. The window parameter [4] controls how much recent history remains relevant.

## Illustrative example

**Measure a trace.** Consider a toy process P that references pages at process times 1 through 6 in this order: A, B, A, C, D, C. Assume one unit of execution time between references and choose a three-unit window. Just after time 3, the recent references are A, B, A, so the set is `{A, B}`. Repetition counts once: demand is two pages, not three references.

**Advance the window.** Just after time 4, the recent references are B, A, C, giving `{A, B, C}`. Just after time 5, they are A, C, D, giving `{A, C, D}`. Just after time 6, they are C, D, C, giving `{C, D}`. Page A can leave the estimated active set even though the process used it repeatedly earlier.

One rough implementation stores each page's last-reference process time. At a sampling point, retain pages whose last-reference times fall inside the window. A timestamp exactly on the boundary requires a consistent interval convention; choose sample times half a unit after the listed references here to avoid that ambiguity.

**Account for suspension.** Suppose P stops receiving processor service after its sixth reference. Ten seconds of wall time pass while another process runs. P's own execution clock does not advance merely because it waits, so its working-set estimate does not age in the same way as a wall-clock inactivity timeout.

**Choose runnable work.** Assume three available frames, P's estimated set `{C, D}`, and another process Q's distinct estimated set `{E, F}`. Both sets together need four frames. An illustrative scheduler can run P and defer Q, then reconsider after P's demand changes or it blocks. Running both with too little resident space risks repeated eviction of pages each soon needs again.

This tiny trace demonstrates the calculation, not a guarantee that recent use predicts every next reference. A new execution phase can demand pages outside the estimate.

## Concepts and terms

**[1] Working set.** `W(t, τ)`, the distinct pages referenced during the process-time interval `(t - τ, t)`.

**[2] Process time.** Time accumulated while the process executes, excluding time spent waiting for processor service.

**[3] Memory demand.** An estimate based on working-set size, used when deciding which computations can be supported together.

**[4] Window parameter.** The duration τ defining recent use. A small window can discard still-useful pages; a large one can retain inactive pages.

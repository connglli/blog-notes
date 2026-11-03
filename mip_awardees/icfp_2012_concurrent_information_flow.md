# Addressing covert termination and timing channels in concurrent information flow systems

**Summary by:** GPT 6 Astra

**Author:** Deian Stefan, Alejandro Russo, Pablo Buiras, Amit Levy, John C. Mitchell, and David Mazières

**Source:** ICFP 2012; SIGPLAN Most Influential ICFP Paper Award 2022.

**Link:** https://doi.org/10.1145/2364527.2364557

**Code:** [LIO library project](https://github.com/PLSysSec/lio)

## Key insight

Waiting for a secret-dependent computation is itself an observation of secret information. Isolate that computation in a labeled thread, and raise the observer's label before allowing it to wait.

## Basic idea

The system tracks a current information-flow label [1] for each computation and offers labeled futures [2] through `lFork` and `lWait`. Forking returns a handle without waiting for the secret-dependent work, while waiting raises the observer's label before inspecting completion. Labeled shared synchronization primitives extend this discipline to concurrent communication. The formal result covers termination and internal timing [3] under its scheduler model; a separate output mitigator [4] bounds rather than eliminates external timing leakage.

## Illustrative example

**Problem.** A service must run a private search that finishes quickly for some secret inputs and loops for others. After starting the search, it wants to publish a public message saying `"accepted"`.

Running the search synchronously and publishing only when it returns leaks information through whether the message appears. In a concurrent system, racing such work against other public actions can reveal information through their order as well.

**Fork.** Start the search with a future labeled High. The Low parent immediately receives its handle and can emit `"accepted"` without awaiting the private result. Whether the child finishes does not control this parent's public continuation in the language model.

**Wait.** If the parent calls `lWait` on that handle, its current label rises to High before waiting. If the child returns, the parent cannot then write a Low result. If the child does not return, the blocked parent's absence cannot be used as permission to perform a Low action from that High computation.

A result label also limits the information the child may successfully expose through that future. Labeling a secret computation's result Low does not make secret-dependent work safely public.

**External observer.** A real network client can still measure elapsed time or resource effects outside the formal language's visible actions. The paper interposes a mitigator that releases outputs according to a predicted schedule. If an output misses its scheduled slot, the schedule changes and leaks some information. Such adaptation is controlled leakage, not a proof of constant-time execution.

The formal semantics uses deterministic round-robin scheduling. Claims about arbitrary production schedulers, caches, or operating-system resource contention require additional analysis.

## Concepts and terms

**[1] Current label.** The accumulated sensitivity of information a computation has observed. Reading more-sensitive information raises the label and restricts subsequent writes.

**[2] Labeled future.** A handle for a concurrently computed result, carrying the label of observing that result and its completion. Waiting is checked and label-raising, not a neutral scheduling operation.

**[3] Internal timing channel.** Disclosure through the order of observable actions among threads, without requiring an external clock. Termination can likewise become observable through blocking or completion.

**[4] Output mitigator.** A component buffering external outputs and releasing them on a schedule. Schedule mispredictions and adjustments can reveal information, so the goal is a bounded channel rather than complete elimination.


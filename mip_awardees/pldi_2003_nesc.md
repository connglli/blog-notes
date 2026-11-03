# The nesC Language: A Holistic Approach to Networked Embedded Systems

**Summary by:** GPT 6 Astra

**Author:** David Gay, Philip Levis, Robert von Behren, Matt Welsh, Eric Brewer, David Culler

**Source:** PLDI 2003; SIGPLAN Most Influential PLDI Paper Award, 2013

**Link:** https://doi.org/10.1145/781131.781133

**Code:** [nesC](https://github.com/tinyos/nesc)

## Key insight

Make component connections and interrupt-driven concurrency explicit enough that a compiler can analyze and optimize an entire embedded application together.

## Basic idea

nesC assembles modules through statically wired, bidirectional interfaces [1]. Split-phase operations [2] start through commands and complete through events instead of blocking a thread. Tasks and interrupt-reachable asynchronous code [3] have different concurrency rules; atomic sections [4] protect shared updates. Whole-program knowledge supports inlining and detection of potentially racing accesses, but individually protected accesses do not automatically make a compound protocol correct.

## Illustrative example

**Components.** Connect a logger module's sensor interface to a sensor driver. The logger calls a request command, and the driver later signals a completion event carrying the sample. Wire the logger's output interface to a separate storage component. These connections are fixed when the application is built.

**Request.** A timer event tries to start sampling. It atomically reads `busy` and changes it from false to true. Only the invocation that observed false requests the sensor. The atomic test-and-set matters: protecting the read and write in separate atomic sections could allow two invocations to both observe false.

**Completion.** An interrupt-driven sensor completion stores the sample in a shared slot and posts a task. Assume the slot's reads and writes are protected, requests are accepted, task posting succeeds, and no new sampling request starts while `busy` is true. The task copies the sample, initiates storage, and leaves `busy` true until the storage completion event clears it.

**Concurrency.** Tasks run to completion without preempting each other, but interrupts may occur during a task. Thus task serialization alone does not protect the sample slot from its interrupt writer. The compiler uses reachability from interrupt handlers to identify this sharing. The full sampling-and-storage operation spans callbacks and is not one atomic task; its `busy` protocol supplies the needed application-level exclusion.

## Concepts and terms

**[1] Bidirectional interface.** A contract containing commands implemented by the provider and events implemented by the user; wiring connects their calls statically.

**[2] Split-phase operation.** A nonblocking initiation followed by a later completion notification.

**[3] Asynchronous code.** Code reachable from interrupts; unlike ordinary tasks, it can preempt other execution in the paper's model.

**[4] Atomic section.** A short region protected from conflicting concurrent execution, implemented with interrupt masking on the paper's single-processor platforms.

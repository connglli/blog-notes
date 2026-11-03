# IX: A Protected Dataplane Operating System for High Throughput and Low Latency

**Summary by:** GPT 6 Astra

**Author:** Adam Belay, George Prekas, Ana Klimovic, Samuel Grossman, Christos Kozyrakis, and Edouard Bugnion

**Source:** OSDI 2014; SIGOPS Hall of Fame Award 2026

**Link:** https://www.usenix.org/conference/osdi14/technical-sessions/presentation/belay

**Code:** [IX source](https://github.com/ix-project/ix)

## Key insight

Fast networking can preserve a protection boundary between application code and the protocol stack. Dedicated resources, bounded adaptive batches, and processing through the complete request path reduce overhead without deliberately waiting to collect more work.

## Basic idea

IX separates a Linux control plane from application-specific networking dataplanes [1]. Hardware virtualization provides three protection levels [2] for Linux, the dataplane kernel, and the application. Each worker polls its assigned network queues and processes bounded batches through a run-to-completion cycle [3]. Per-thread flow ownership [4] avoids synchronization on the common networking path, while a shared-memory API supports batched calls and zero-copy access [5]. The design targets network-intensive applications and retains privileged protocol processing rather than trusting application code to implement the network stack correctly.

## Illustrative example

**Provision and isolate.** A small key-value service uses two hardware threads. Linux assigns queues and memory to its IX dataplane. The dataplane kernel runs with guest-kernel privileges, while the application's lookup code runs at user privilege. The application cannot rewrite the dataplane's connection state or Linux's resource assignments merely because it shares the fast I/O path.

**Place a flow.** The network adapter consistently directs packets from connection C to worker 0's queue. Worker 0 owns C's flow identifier and connection state. Worker 1 handles other flows and cannot directly issue operations on C. This avoids a shared connection lock in the ordinary packet-processing path; it does not remove locks needed by the application's shared key-value table.

**Process a bounded batch.** Use an illustrative maximum batch size of four. If only one packet is ready, worker 0 processes it immediately rather than waiting for three more. If six are ready, it processes at most four through TCP/IP, enters application mode to handle the resulting events, and then processes the application's batched send and buffer-release calls. Timers and transmission work run before the next receive cycle, preventing an unbounded receive batch from monopolizing processing.

**Use the buffer contract.** A receive event lets the application inspect its payload directly through a read-only mapping. After using it, the application submits the corresponding release operation. For a zero-copy send, the application must keep outgoing bytes unchanged until the peer acknowledges them; modifying them prematurely can corrupt its own response payload. A wrapper can present familiar event-driven socket operations, but the native API exposes flow-control and lifetime obligations explicitly.

**Keep the scope clear.** Polling consumes dedicated execution resources. Linux retains mechanisms to regain control, and reallocating cores or updating shared networking state requires coordination. The paper concentrates on dataplane mechanisms rather than supplying a complete automatic policy for deciding resource allocations across arbitrary changing workloads.

## Concepts and terms

**[1] Control plane and dataplane.** The control plane provisions and manages resources at coarse granularity. A dataplane performs frequent networking work for one application, potentially using several worker threads.

**[2] Three-way protection.** Hardware virtualization separates host and guest execution; privilege rings separate kernel and application code within a guest. Linux uses host ring 0. Dune, a Linux module exposing virtualization features, enables the dataplane to use guest ring 0 and the application guest ring 3.

**[3] Run-to-completion cycle.** A worker performs receive processing, application handling, outgoing-call processing, timers, and transmission in a coordinated cycle. Adaptive batching uses available work up to a bound without adding a wait to fill the batch.

**[4] Flow ownership.** Queue steering and separate identifier spaces assign a connection's protocol state to one worker. Common operations remain local; exceptional management and shared application data can still require synchronization.

**[5] Zero-copy access.** Data is accessed in existing buffers instead of copied across the API boundary. Protection and explicit lifetime rules preserve safety while shared arrays communicate events and system-call requests.

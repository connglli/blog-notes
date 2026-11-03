# GeePS: Scalable Deep Learning on Distributed GPUs with a GPU-Specialized Parameter Server

**Summary by:** GPT 6 Astra

**Author:** Henggang Cui, Hao Zhang, Gregory R. Ganger, Phillip B. Gibbons, Eric P. Xing

**Source:** EuroSys 2016; EuroSys Test-of-Time Award 2026

**Link:** https://doi.org/10.1145/2901318.2901323

**Code:** [GeePS](https://github.com/cuihenggang/geeps)

## Key insight

A parameter server should manage GPU-resident data and its movement, not force the training application to shuttle every access through CPU memory. Repeated training access patterns let the server prepare transfers and buffers ahead of computation.

## Basic idea

GeePS supports data-parallel training [1] through a parameter server [2] with GPU-resident caches and batched accesses. Applications borrow managed buffers [3] for reading parameters, producing updates, and accessing private intermediate data. An access-sequence hint [4] enables prefetching and GPU-memory placement, including moving data to CPU memory when the whole model does not fit. Per-table clocks [5] control when updates become visible across workers, separating the communication schedule from the GPU computation schedule.

## Illustrative example

**Setup.** Two machines train the same two-layer network using different minibatches. Each worker needs parameters `weights_a` and `weights_b`, plus its own intermediate activations. Its GPU can hold the active layer's working data, but not all parameters and activations simultaneously.

**Describe accesses.** Before training, a virtual iteration records the sequence of parameter and local-data operations without running the network. GeePS uses this sequence to build lookup indices and plan data placement. It remains a hint: a changed access sequence can hurt performance without changing the access contract.

**Run the forward pass.** A worker calls `Read` for `weights_a` and receives a pointer to a filled GPU buffer. It obtains its activation buffer through `LocalAccess`, launches the layer computation, and releases the buffers with `PostRead` and `PostLocalAccess`. While useful computation runs, background threads can prepare the next layer's transfers. Local activations belong only to this worker; they are not distributed model parameters.

**Return updates.** In the backward pass, the worker obtains a buffer with `PreUpdate`, fills it with parameter increments, and returns it with `Update`. `TableClock` commits accumulated updates for that layer's table. With bulk-synchronous operation, a later read requiring the next clock waits until the required updates from the other worker are available. Updating the second layer can overlap communication for a completed layer.

**Handle capacity.** GeePS retains selected data on the GPU and transfers other data between managed GPU buffers and CPU memory. This does not eliminate transfers or guarantee that they are hidden: insufficient computation, bandwidth, or buffering can still cause stalls.

## Concepts and terms

**[1] Data-parallel training.** Workers execute the same model on different training examples and contribute parameter updates. A minibatch is the group of examples processed together; throughput alone does not establish how quickly training reaches a desired accuracy.

**[2] Parameter server and cache.** Model parameters are divided among server shards. Each worker maintains a local cached view and accumulates updates before sending them to the owning shards. Keeping cache operations on the GPU makes parallel gathering and update application possible. Network communication still uses CPU-side staging in this design.

**[3] Managed buffers.** The library controls the lifetime and location of access buffers. A parameter read uses a separate buffer because background communication may modify the cached parameters during computation. Private local data can be accessed directly when resident; release operations allow storage reuse or movement.

**[4] Access-sequence hint.** Recording a real or virtual iteration reveals which groups of keys are used together and when. The library prepares batch indices, prefetches data, and chooses what to keep resident. Correctness does not require perfect prediction.

**[5] Clocks and staleness.** A clock marks progress for a parameter table. Bulk-synchronous reads require prior-clock updates; bounded-staleness execution permits a specified amount of lag. Looser synchronization can increase training iterations even when it reduces waiting. Server shards are not replicated; the paper uses checkpointing for fault recovery.

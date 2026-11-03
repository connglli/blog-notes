# Dryad: Distributed Data-Parallel Programs from Sequential Building Blocks

**Summary by:** GPT 6 Astra

**Author:** Michael Isard, Mihai Budiu, Yuan Yu, Andrew Birrell, Dennis Fetterly

**Source:** EuroSys 2007; EuroSys Test-of-Time Award 2017

**Link:** https://doi.org/10.1145/1272996.1273005

## Key insight

Describe a distributed computation as a graph of ordinary programs connected by record streams. The runtime can schedule, pipeline, and retry these programs without making each vertex implement distributed coordination.

## Basic idea

Dryad represents a job as a directed acyclic dataflow graph [1] whose vertices execute application code and whose channels [2] carry records. A job manager [3] starts vertices when their inputs are ready and places them near data where possible. Versioned executions and re-execution [4] handle worker or intermediate-data failures under the default deterministic-computation contract. Runtime graph refinement [5] can add locality-aware aggregation without changing the intended result.

## Illustrative example

**Build the graph.** Four immutable log partitions contain event categories. Four reader vertices independently produce integer counts by category. A final vertex adds the partial counts. Each reader is an ordinary sequential routine; parallelism comes from executing several readers at once.

**Choose channels.** If partial counts travel through files, the final vertex's corresponding input becomes ready when the file is complete. With a TCP pipe, it can begin once the producing execution is running and consume records as they arrive. The latter enables pipelining but couples failures more closely.

**Refine for locality.** Suppose two readers run in each of two racks. Insert one combining vertex per rack, then send their smaller count tables to the final vertex. Integer count addition is associative and commutative, so this regrouping preserves the result. The same argument would not justify arbitrary regrouping of rounded floating-point calculations.

**Retry.** If one reader's output file disappears, mark its producing execution as failed and rerun that reader from its original input. Output filenames include execution versions, so retried and speculative attempts do not overwrite each other's files. A successful consumer can use output from a different successful producer version because deterministic readers produce equivalent records for these fixed inputs.

**Respect the boundary.** Sending a payment from a vertex would create an external effect that retries could repeat. The default dataflow recovery mechanism is not an exactly-once guarantee for arbitrary external actions. Failure of the prototype's job-manager machine also terminates the job.

## Concepts and terms

**[1] Dataflow graph.** Vertices consume input records and produce output records; directed edges express their dependencies. Acyclicity permits scheduling and recovery in dependency order. Unlike a fixed map-then-reduce structure, the graph can contain multiple stages and different communication patterns.

**[2] Channel.** A record stream implemented through a file, TCP pipe, or shared-memory FIFO. File channels materialize data and separate producer and consumer lifetimes. Pipes and FIFOs allow overlap but can propagate a failure through an entire connected pipeline.

**[3] Job manager.** A controller tracks vertex executions, input readiness, resource availability, and placement constraints or preferences. Worker daemons run assigned programs and report progress. The manager can also start duplicate attempts for slow vertices.

**[4] Versioned re-execution.** Each attempt records which producer versions supplied its inputs and writes separately named outputs. Missing input can trigger regeneration of the responsible producer. The default recovery argument assumes immutable inputs and deterministic vertices; it does not cover every nondeterministic application.

**[5] Graph refinement.** Stage-management callbacks can change the physical graph after data sizes and locations become known. Inserting a combining tree is valid only when the application's aggregation laws justify it. The runtime does not infer arbitrary algebraic equivalence from a vertex executable.

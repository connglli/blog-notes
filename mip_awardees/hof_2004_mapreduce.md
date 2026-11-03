# MapReduce: Simplified Data Processing on Large Clusters

**Summary by:** GPT 6 Astra

**Author:** Jeffrey Dean and Sanjay Ghemawat

**Source:** OSDI 2004; SIGOPS Hall of Fame Award 2015

**Link:** https://www.usenix.org/legacy/event/osdi04/tech/dean.html

## Key insight

Many large computations can be expressed as producing intermediate key-value pairs and then combining all values for each key. Restricting the interface this way lets a runtime handle placement, communication, retries, and slow workers.

## Basic idea

A map function [1] converts input records into intermediate key-value pairs, and a reduce function [2] consumes the values grouped under each intermediate key. The runtime partitions and shuffles [3] map output to reducers, using a master to schedule tasks and track their files. Failed workers trigger re-execution, and backup tasks [4] reduce delays from unusually slow workers. Deterministic user functions plus atomic publication of task outputs give results equivalent to a failure-free sequential execution of the same computation.

## Illustrative example

**Map.** Two input partitions contain sales records: A has `(tea, 2)` and `(coffee, 4)`; B has `(tea, 3)` and `(tea, 1)`. The map function emits each product as the key and its quantity as the value. A more realistic map might parse and filter a large log first, but the grouping contract is unchanged.

**Shuffle.** Choose two reducers and a partition function based on the key. All `tea` values must go to the same reducer, regardless of which mapper produced them. The reducers fetch their partitions of map output, sort or otherwise group by key, and obtain `tea -> [2,3,1]` and `coffee -> [4]`.

**Reduce.** Summing each group yields `(tea, 6)` and `(coffee, 4)`. A local combiner can sum repeated tea entries before network transfer if the reduction's semantics permit partial aggregation. It is an optimization, not an additional stage whose invocation count application correctness may depend on.

**Recover.** If mapper B's worker dies, its intermediate files on local disk may be lost even though the task had finished. The master reassigns that map task and tells reducers where to obtain the replacement output. Completed reducer files live in the distributed file system and need not be recomputed solely because their worker disappears.

Each task writes temporary output. The master accepts one completion for a map task; a reducer publishes its output using atomic rename. Thus a retried or backup attempt does not concatenate another complete output into the result. This protection covers managed output files, not arbitrary external effects such as sending a payment from inside the map function.

For nondeterministic functions, different reducers may consume outputs from different map attempts, weakening whole-job equivalence. The paper's implementation also aborts the job if its single master fails; worker fault tolerance does not imply transparent recovery from every component failure.

## Concepts and terms

**[1] Map function.** A user operation taking an input key-value record and emitting zero or more intermediate pairs. Independent input partitions can be mapped in parallel.

**[2] Reduce function.** A user operation taking one intermediate key and its associated values and producing output records. The interface groups by key, not by input partition.

**[3] Partition and shuffle.** A partition function assigns each key to a reducer; data transfer and grouping bring all values of that key together. Key-consistent assignment is required for the reduction contract.

**[4] Backup task.** An additional execution of a slow outstanding task near job completion. Either attempt can supply the result, so publication and retry semantics must tolerate duplicate execution.

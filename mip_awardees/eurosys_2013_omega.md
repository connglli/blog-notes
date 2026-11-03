# Omega: Flexible, Scalable Schedulers for Large Compute Clusters

**Summary by:** GPT 6 Astra

**Author:** Malte Schwarzkopf, Andy Konwinski, Michael Abd-El-Malek, John Wilkes

**Source:** EuroSys 2013; EuroSys Test-of-Time Award 2023

**Link:** https://doi.org/10.1145/2465351.2465386

**Code:** [Paper's lightweight simulator](https://github.com/google/cluster-scheduler-simulator)

## Key insight

Let independent schedulers examine the whole cluster and resolve conflicting decisions when they commit. Sharing resource state through optimistic transactions avoids assigning each scheduler an exclusive resource pool while it thinks.

## Basic idea

Omega separates scheduling policy [1] from a shared record of cluster allocations called cell state [2]. Each scheduler plans against a local copy and submits proposed placements through optimistic concurrency control [3]. The shared state accepts compatible changes and rejects conflicts, after which the scheduler refreshes its view and retries. Incremental commits [4] can retain successful placements from a partially conflicting job; workloads requiring all tasks together can request all-or-nothing behavior.

## Illustrative example

**Read the state.** Two machines, `amber` and `blue`, each have eight free CPU units. A service scheduler and a batch scheduler independently read this state. They do not reserve these units just by inspecting them.

**Make competing plans.** The service scheduler proposes one six-unit task on `amber`. The batch scheduler proposes one four-unit task on `amber` and another four-unit task on `blue`. Their plans are individually feasible against their snapshots.

**Commit.** The service scheduler commits first, leaving two units free on `amber`. Under fine-grained resource-conflict checking, the batch task on `amber` cannot commit because it needs four units. Its task on `blue` can commit. The shared state therefore never records the incompatible six-plus-four allocation on the eight-unit machine.

**Retry the remainder.** The batch scheduler refreshes its state and replans only the rejected task. A coarse machine-version check could reject a placement merely because another allocation changed that machine, even when enough resources remained; checking actual resource conflicts avoids such unnecessary rejection.

**Change the job's contract.** If the batch job needs both tasks allocated together, it instead requests an all-or-nothing commit. The conflict on `amber` then rejects the complete proposal, including the otherwise feasible placement on `blue`. The scheduler must retry the whole job. Atomic resource allocation is not a guarantee that all application processes execute their first instruction simultaneously.

## Concepts and terms

**[1] Scheduling policy.** A scheduler chooses where and when tasks should run, considering resources, priority, constraints, and workload-specific goals. Independent implementations can serve different workload classes. Concurrency alone does not establish fairness, eliminate starvation, or make conflicting policies compatible.

**[2] Cell state.** The authoritative record of available machines and committed allocations. Schedulers hold private, periodically refreshed copies, so a decision may already be stale when submitted. Shared visibility permits choices requiring knowledge beyond the unused resources offered to one scheduler.

**[3] Optimistic concurrency control.** Compute a candidate change without holding an exclusive allocation lock during planning. At commit, compare the change with current state and accept it only when the relevant constraints still hold. Rejected work must be reconsidered. This moves coordination to a short commit step; it does not eliminate coordination or the cost of retries.

**[4] Incremental versus all-or-nothing transactions.** Incremental scheduling commits nonconflicting task placements and leaves the rest pending. All-or-nothing scheduling rejects the complete proposed allocation if any part conflicts. The paper evaluates both conflict-check granularity and commit policy because they independently affect wasted scheduler work. Its results come from workload-driven simulations, not a theorem that arbitrary numbers of schedulers scale without contention.

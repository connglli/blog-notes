# Delay Scheduling: A Simple Technique for Achieving Locality and Fairness in Cluster Scheduling

**Summary by:** GPT 6 Astra

**Author:** Matei Zaharia, Dhruba Borthakur, Joydeep Sen Sarma, Khaled Elmeleegy, Scott Shenker, Ion Stoica

**Source:** EuroSys 2010; EuroSys Test-of-Time Award 2020

**Link:** https://doi.org/10.1145/1755913.1755940

## Key insight

The next available worker need not be the best worker for the job entitled to run next. Let that job yield a few opportunities for data locality, but relax locality after a bounded wait so it cannot wait forever solely for a preferred location.

## Basic idea

A fair scheduler [1] can lose throughput by placing a task away from its input data [2] just to obey queue order immediately. Delay scheduling temporarily skips a job that has no local task for the offered worker, letting another job use that slot. A per-job delay counter [3] eventually permits nonlocal placement, and successful local placement resets the counter. Hierarchical locality [4] extends the same idea from a machine to its rack and then to the whole cluster.

## Illustrative example

**Start with fairness.** Jobs `oak` and `pine` share workers `east` and `west`. `oak` has fewer running tasks and should receive the next slot, but its pending input block is on `west`. A slot becomes available on `east`, where `pine` has local input.

**Yield briefly.** Use the paper's simple skip-count version with threshold two. The scheduler skips `oak` for this offer, increments its counter to one, and gives the slot to a local `pine` task. No worker is deliberately left idle while useful alternative work can run.

**Get a local placement.** If `west` becomes free next, launch `oak` there and reset its counter to zero. The short relaxation of queue order avoids a remote data transfer.

**Bound the locality wait.** Alternatively, suppose another unsuitable offer raises `oak`'s counter to two. On a later offer, the threshold permits a nonlocal task. Importantly, that nonlocal launch does not reset the counter: subsequent launches may also be nonlocal until a local launch resets it. Resetting after every nonlocal launch would repeatedly penalize jobs whose preferred machines remain unavailable.

**Add racks.** If a preferred machine is busy but another machine in its rack becomes free, a two-threshold policy can first permit rack-local execution and only later permit cross-rack execution. The waiting thresholds trade scheduling delay against data-transfer cost.

## Concepts and terms

**[1] Fair sharing.** A policy determines how much cluster capacity each job or user should receive. The simple example orders jobs by running-task count; the deployed Hadoop scheduler supports richer sharing policies. Delay scheduling modifies placement opportunities, not the definition of entitlement itself.

**[2] Data locality.** A task is node-local when its input is on the executing machine, rack-local when it is elsewhere in the same rack, and nonlocal otherwise. This matters when input transfer is expensive. The paper primarily applies locality decisions to map tasks rather than claiming all reduction inputs can be local.

**[3] Delay counter.** Track skipped scheduling opportunities, or waiting time in the fuller implementation. Skip a pending job while it lacks an acceptable local task and remains below its threshold. Afterward allow less-local work. This bounds waiting imposed by locality preference, not delays caused by missing resources, priority, or failed machines.

**[4] Hierarchical locality and assumptions.** Broaden acceptable placement gradually as waiting accumulates. The mechanism works particularly well when tasks finish frequently enough that suitable slots become available soon. Long-running tasks, hotspots, or scarce preferred machines can make waiting unhelpful; the fallback prevents permanent insistence on locality.

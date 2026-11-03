# Large-Scale Cluster Management at Google with Borg

**Summary by:** GPT 6 Astra

**Author:** Abhishek Verma, Luis Pedrosa, Madhukar Korupolu, David Oppenheimer, Eric Tune, John Wilkes

**Source:** EuroSys 2015; EuroSys Test-of-Time Award 2025

**Link:** https://doi.org/10.1145/2741948.2741964

## Key insight

Treat a shared cluster as a managed pool of resources, with explicit priorities and continuous reconciliation between requested tasks and actual machine state. High utilization depends on combining placement, isolation, and reclamation rather than merely finding an idle machine.

## Basic idea

Borg turns submitted jobs into tasks [1] that request resources and specify placement constraints. Admission control uses quota and priority [2], while the scheduler separates feasibility checking from scoring [3]. Resource reclamation [4] lets lower-priority tasks use capacity that higher-priority tasks reserve but do not consume. A replicated controller and machine agents [5] maintain task state and restart eligible work after failures or eviction; this does not recover application-level state automatically.

## Illustrative example

**Admit work.** A cell contains two machines, `north` and `south`. A user submits a service with two tasks, each requiring two CPU units and four memory units. The user must have enough quota for the requested resources at the service's priority. Passing this check admits the job; it does not promise immediate placement if constraints or fragmentation prevent it.

**Choose placements.** The scheduler checks each task against machine resources and constraints, then scores feasible placements. Suppose the service prefers separate failure domains and only `north` already has its executable package. Package locality favors `north`, while spreading replicas favors placing the second task on `south`. These are placement considerations, not a proof of globally optimal packing.

**Reuse spare capacity.** A service task reserves four memory units but consistently uses two. Borg's usage-based reservation estimate can expose some unused capacity to a low-priority batch task. If demand rises and the machine runs short, the batch task can be killed and returned to the pending queue. The service must not depend on the speculative capacity assigned to batch work.

**Repair state.** If `south` stops responding, the controller marks it unavailable and reschedules eligible tasks elsewhere. When communication returns, it orders obsolete task instances to stop. Running tasks do not immediately stop merely because they lose contact with the controller. Applications still need their own durable storage and coordination when duplicate or restarted execution matters.

## Concepts and terms

**[1] Job, task, and cell.** A job describes a collection of tasks with shared properties. A task is an independently scheduled process instance. A cell is the set of machines managed by one Borg control plane. Resource requests are multidimensional, so unused CPU cannot compensate for insufficient memory.

**[2] Quota and priority.** Quota limits resource requests admitted for a user at a priority and over a specified period. Priority determines scheduling order and eligibility to displace other work. Preemption kills a lower-priority task; Borg requeues it rather than migrating its running memory image. Production tasks are restricted from preempting one another within the production band.

**[3] Feasibility and scoring.** Feasibility filters machines by required constraints and available or reclaimable resources. Scoring then balances preferences such as package reuse, spreading failure risk, packing, and avoiding preemption. Sampling candidate machines and caching decisions reduce scheduler work.

**[4] Reclamation.** Resource limits describe permitted consumption, while reservations estimate actual needs from usage. Low-priority tasks may be placed into the difference. Incorrect estimates can cause eviction or throttling, so reclamation trades additional utilization against disruption to that work.

**[5] Controller and machine agents.** Borgmaster records cluster state in a replicated Paxos-based store and has an elected state-changing leader. Borglets start and monitor tasks and report machine state. Replication protects control-plane state, not the contents of each application process; failure detection and task recovery remain asynchronous.

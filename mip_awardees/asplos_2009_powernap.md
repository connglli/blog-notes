# PowerNap: Eliminating Server Idle Power

**Summary by:** GPT 6 Astra

**Author:** David Meisner, Brian T. Gold, Thomas F. Wenisch

**Source:** ASPLOS 2009; ASPLOS Influential Paper Award 2025

**Link:** https://doi.org/10.1145/2528521.1508269

## Key insight

Short idle gaps can save substantial energy if the whole server enters and leaves a low-power state quickly enough. Efficient power delivery must span those low loads too, or power-supply losses consume part of the savings.

## Basic idea

PowerNap proposes a whole-system active/nap design [1] instead of relying only on proportional power scaling within individual components. New work wakes the server, while the empty work queue permits another nap. Transition delay and queueing [2] determine whether frequent naps hurt response time. RAILS [3] supplies power through selectively enabled small power supplies so conversion efficiency remains useful across the resulting load range.

## Illustrative example

**Define an idealized server.** Suppose an active server consumes 100 watts, a conventional idle server consumes 60 watts, and a napping server consumes 2 watts. A workload needs active execution for one fifth of a long observation interval. These values are chosen for this example, not taken from the evaluation.

**Compare steady-state energy.** Ignoring transitions, conventional average power is `0.2*100 + 0.8*60 = 68` watts. Idealized PowerNap average power is `0.2*100 + 0.8*2 = 21.6` watts. The difference comes from the idle periods, not from making the useful computation itself cheaper.

**Add the transition constraint.** A request arriving during a nap cannot execute until wakeup completes. If gaps are shorter than the combined transitions, the idealized calculation is misleading: repeated sleep and wake operations consume time and power while queued work waits. Components that detect incoming work or timer expiration must remain able to initiate wakeup.

**Supply changing loads.** Imagine a chassis in which most servers are napping. Keeping every large supply lightly loaded can be inefficient. RAILS disables unnecessary small supplies and spreads the current load over the enabled ones. More supplies come online as servers wake, while the design retains its chosen redundancy. Server-side power reduction and conversion efficiency are separate parts of the energy budget.

## Concepts and terms

**[1] Active and nap states.** Active operation provides full performance; the nap state suspends computation and minimizes component power while retaining necessary wake detection. The paper derives requirements and outlines component mechanisms; it does not demonstrate that an ordinary server already supports an arbitrarily fast, near-zero-power whole-system sleep instruction.

**[2] Transition and queueing cost.** Arrival patterns, service demand, and suspend/resume latency jointly determine how long requests wait and what fraction of time is actually spent asleep. PowerNap analyzes this tradeoff using a queueing model and workload traces. Average utilization alone cannot determine latency impact or achievable energy savings.

**[3] RAILS.** A Redundant Array for Inexpensive Load Sharing connects multiple low-wattage supplies in parallel, enables enough to support current demand, and isolates unused units. Supply sizing aims to keep active units near efficient operating points even when all blades nap. It addresses electrical conversion and redundancy, not scheduling application work between servers.

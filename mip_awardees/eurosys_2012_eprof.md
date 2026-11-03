# Where Is the Energy Spent Inside My App? Fine Grained Energy Accounting on Smartphones with Eprof

**Summary by:** GPT 6 Astra

**Author:** Abhinav Pathak, Y. Charlie Hu, Ming Zhang

**Source:** EuroSys 2012; EuroSys Test-of-Time Award 2022

**Link:** https://doi.org/10.1145/2168836.2168841

## Key insight

A function can stop executing while hardware it activated continues consuming power. Energy profiling therefore needs a model of hardware state and an explicit attribution policy, not just a count of CPU time spent in each function.

## Basic idea

Eprof combines program execution traces [1] with system-call-driven power-state machines [2] to estimate component energy. It attributes lingering consumption using a last-trigger policy [3] and reports productive and tail energy separately. Its bundle presentation [4] groups each component's activity between returns to the idle state, exposing scheduling and batching opportunities. The measurements explain an observed execution; attributed energy is not automatically the amount saved by deleting the attributed routine.

## Illustrative example

**Model a radio.** For a deliberately simplified example, ignore the brief transmissions themselves and consider only excess tail power. A send keeps the radio at one watt above idle for two seconds after the latest send. Routine `upload_status` sends at time 0; `upload_metrics` sends at time 1. Both return immediately.

**Replay events.** The first send starts a tail interval. The second send resets its timer, so the radio returns to idle at time 3. Integrating the one-watt excess over three seconds gives three joules, despite negligible CPU execution in the two routines. These values define the example's model, not measurements from the paper.

**Attribute consumption.** The first second belongs to the first trigger. The two seconds after the second send belong to the second trigger. Eprof's last-trigger accounting therefore assigns one joule to `upload_status` and two joules to `upload_metrics` for these tail intervals.

**Interpret the bundle.** Both sends are part of one radio bundle. Moving the second send next to the first could shorten the modeled tail to approximately two seconds. Removing the second routine also leaves a two-second tail caused by the first: it saves one joule, not the two joules attributed to it. The bundle explains this distinction and exposes the timing relationship that an ordinary per-function profile hides.

## Concepts and terms

**[1] Execution trace.** Instrumentation records system calls, the routines responsible for them, and relevant thread or process execution. Postprocessing connects hardware-triggering events to program entities. The required trace and power model are device- and operating-system-dependent; the profiler is not a direct measurement of every instruction's energy.

**[2] Power-state machine.** Hardware components occupy states with characteristic power draw. System calls and timeouts trigger transitions. Energy is accumulated over the time spent in each state, with workload-dependent modeling where appropriate. A tail state continues drawing power after useful I/O has ended. Wakelocks can similarly keep components active until a later release.

**[3] Last-trigger accounting.** Lingering energy is charged to the most recent entity that triggered the relevant power behavior. An acquisition can therefore receive energy charges after its routine has returned. The paper presents this as an understandable accounting convention, not a unique physical decomposition of causality. Concurrent accesses require additional accounting rules; the example uses sequential triggers.

**[4] I/O energy bundle.** A continuous excursion from a component's base state until its next return to that state, including active and tail intervals. Annotating this state trajectory with responsible routines helps explain why activity lasts so long or repeats so often. Optimizations suggested by the profile, such as batching transmissions or shortening gaps, must preserve application behavior and be measured again.

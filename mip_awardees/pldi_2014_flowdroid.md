# FlowDroid: Precise Context, Flow, Field, Object-sensitive and Lifecycle-aware Taint Analysis for Android Apps

**Summary by:** GPT 6 Astra

**Author:** Steven Arzt, Siegfried Rasthofer, Christian Fritz, Eric Bodden, Alexandre Bartel, Jacques Klein, Yves Le Traon, Damien Octeau, Patrick McDaniel

**Source:** PLDI 2014; SIGPLAN Most Influential PLDI Paper Award, 2024

**Link:** https://doi.org/10.1145/2594291.2594299

**Code:** [FlowDroid](https://github.com/secure-software-engineering/FlowDroid)

## Key insight

An Android leak can cross callbacks that have no explicit call edge in the app. Precise data-flow tracking therefore needs an explicit model of the app's lifecycle as well as its code.

## Basic idea

FlowDroid constructs a synthetic entry point that models lifecycle and callback [1] orderings, then performs static taint analysis [2]. Taint facts use access paths [3]; heap writes trigger a backward alias search [4] coupled to forward propagation. Context and activation information prevent an alias from being tainted in the wrong invocation or before the write occurs. The analysis models explicit data flows, not a complete security guarantee against every information channel.

## Illustrative example

**Setup.** An activity creates two distinct records, `privateRecord` and `publicRecord`, each with `text` and `label` fields. A registered button callback obtains a secret string and calls `fill(privateRecord, secret)`. A later callback sends `privateRecord.text` to a server. The helper `fill(record, value)` first sets local `alias = record`, then assigns `alias.text = value`.

**Lifecycle.** The synthetic entry point includes a path through activity startup, the button callback, and the later sending callback. It also allows other modeled callback sequences. An analysis starting only at the constructor would miss this path.

**Propagation.** The secret source taints the helper's `value`. The assignment taints `alias.text`. Searching backward discovers that `alias` and `record` refer to the same object, so the effect returns to the caller as tainted `privateRecord.text`. The network operation receives that taint and is reported.

**Precision.** `privateRecord.label` is a different field, and `publicRecord.text` belongs to a different object. Calling `fill(publicRecord, "hello")` does not inherit the first call's tainted argument. If a send appears before the secret assignment, finding the alias backward must not make that earlier send a leak: the propagated alias becomes active at the assignment. These distinctions avoid several false alarms without assuming that every modeled lifecycle path is feasible.

## Concepts and terms

**[1] Callback.** A method invoked by the framework in response to an event, rather than through an ordinary app call.

**[2] Static taint analysis.** Propagation of possible dependence on designated sources toward designated sinks without executing the app.

**[3] Access path.** A local variable followed by field selections, such as `record.text`, used to name tracked memory.

**[4] Alias.** A different expression referring to the same object. Matching call contexts and activation points matters when transferring taint through aliases.

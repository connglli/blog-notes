# Impossibility of distributed consensus with one faulty process

**Summary by:** GPT 6 Astra

**Author:** Michael J. Fischer, Nancy A. Lynch, and Michael S. Paterson

**Source:** Journal of the ACM 32(2), 1985; PODC Influential-Paper Award 2001.

**Link:** https://doi.org/10.1145/3149.214121

## Key insight

In a fully asynchronous system, a delayed process cannot be distinguished from a failed one. A deterministic protocol cannot guarantee both agreement and eventual decision in every permitted execution when even one process may stop.

## Basic idea

The paper studies deterministic consensus [1] with reliable asynchronous message passing [2] and at most one crash failure. It identifies bivalent configurations [3], from which executions can still decide either value. A critical-event lemma [4] shows how to schedule steps while preserving bivalence. Repeating the construction produces an admissible execution [5] that never decides, so the failure is a worst-case termination guarantee, not the claim that consensus never completes in practice.

## Illustrative example

**Uncertain communication.** Processes Ash, Birch, and Cedar run a proposed deterministic protocol. Ash has not heard from Cedar. One permitted situation is that Cedar stopped; another is that Cedar is correct but its next message is delayed. Ash's local history is identical in those situations, so it cannot use an ordinary timeout as certain evidence of failure.

This observation motivates the theorem but is not its complete proof.

**Bivalent starting point.** Arrange the initial Boolean inputs in a chain, changing only one process's input between neighboring assignments. The protocol must permit both decision values somewhere. If every initial assignment already forced a unique value, some neighboring pair would force opposite values while differing only at Cedar. A run where Cedar takes no steps would be indistinguishable to the others, contradicting those forced outcomes. Thus some initial configuration must be bivalent.

**Extend without deciding.** From a bivalent configuration, choose a pending message-delivery event for Ash. The critical-event lemma supplies a finite schedule of other steps followed by that event that leaves the system bivalent. The proof uses independence of steps at different processes and the ability to run without one process to rule out an unavoidable immediate commitment.

Repeat for Birch, Cedar, and then Ash again, always selecting old pending messages fairly. Each chosen event is eventually processed, yet each constructed stage ends with both decision outcomes still possible. A decision would make the configuration univalent, so none occurs.

**Boundary.** The execution is not obtained by permanently dropping messages to correct processes. Randomization, stronger timing assumptions, or failure information change the model and can support different termination guarantees.

## Concepts and terms

**[1] Deterministic consensus.** Processes must not decide different values, the decision problem must be nontrivial, and the required executions must eventually decide. Local next steps are determined by local state and the received message.

**[2] Asynchronous message passing.** There is no known bound on relative execution speeds or message delay. Reliability supplies eventual delivery to correct processes, not a deadline.

**[3] Bivalent configuration.** A complete system state from which both a 0 decision and a 1 decision remain reachable. A univalent configuration allows only one decision value.

**[4] Critical-event lemma.** The proof's extension result allowing a selected enabled event to occur after some finite schedule without forcing loss of bivalence.

**[5] Admissible execution.** An execution with at most one faulty process and eventual delivery of messages sent to nonfaulty processes. The nontermination construction respects these conditions.


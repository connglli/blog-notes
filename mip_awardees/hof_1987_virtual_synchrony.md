# Exploiting Virtual Synchrony in Distributed Systems

**Summary by:** GPT 6 Astra

**Author:** Kenneth P. Birman and Thomas A. Joseph

**Source:** SOSP 1987; SIGOPS Hall of Fame Award 2013

**Link:** https://doi.org/10.1145/41457.37515

## Key insight

Replicas need a consistent account of both messages and membership changes. A communication layer can present those events in a coordinated logical order while allowing independent work to proceed asynchronously underneath.

## Basic idea

Virtual synchrony [1] structures a distributed application as process groups [2] with coordinated communication and failure notifications. ISIS supplies atomic ordered broadcast, ABCAST [3], causal broadcast, CBCAST [4], and group-management broadcast, GBCAST [5], for different ordering requirements. The application chooses stronger ordering when operations conflict and weaker ordering when causal dependencies suffice. Membership and state transfer are integrated with communication so a failure notification cannot simply race unrelatedly with the messages whose effects surviving replicas must agree on.

## Illustrative example

**Replicate a queue.** Three processes, A, B, and C, maintain one logical work queue. Two clients concurrently submit tasks `red` and `blue`. Appending these tasks is order-sensitive because it determines which task a later dequeue returns. Send queue operations with ABCAST so every operational recipient processes them in the same order, say `red` then `blue`.

**Change membership.** C fails during communication. The group service orders the failure event consistently with relevant message deliveries. A and B must not independently decide that one task was before C's removal at one replica but after an incompatible membership transition at the other. They continue from the same logical sequence of queue operations and group changes under the service's guarantees.

**Use weaker ordering where justified.** Alongside the queue, each client publishes updates to a distinct progress variable. If one computation publishes `started` and later `finished`, CBCAST preserves that causal order at replicas. Independent progress updates from unrelated clients need not receive one common total order. This weaker primitive is appropriate only because those updates do not require the queue's global ordering semantics.

**Join with state.** A replacement process D joins the group. The system's group and state-transfer facilities establish a starting state consistent with the membership and communication history before D participates as an ordinary replica. Copying arbitrary memory from A while B continues applying messages, with no agreed boundary, would not achieve the abstraction.

The example relies on the group service's failure and partition-handling rules. A timeout is not a proof that a remote machine physically stopped; excluded members must be prevented from continuing as if they still belonged to the same active group. Virtual synchrony is also not a promise that every message category has total order: the paper deliberately offers different primitives.

## Concepts and terms

**[1] Virtual synchrony.** An execution model in which relevant communication, membership, and failure events appear coordinated in a logically synchronous order, without requiring lockstep physical execution of all processes.

**[2] Process group.** A named collection of cooperating processes whose membership is managed as part of the distributed service rather than independently guessed by each application component.

**[3] ABCAST.** A multicast primitive providing atomic delivery and the same delivery order among recipients, appropriate for order-sensitive replicated operations.

**[4] CBCAST.** A multicast primitive preserving potential causal order: if information from one multicast could have influenced another's initiation, their common recipients deliver them accordingly.

**[5] GBCAST.** A group-management primitive ordered relative to the other broadcast classes, used for events such as membership and configuration changes.

# Time Is Not a Healer

**Summary by:** GPT 6 Astra

**Author:** Nicola Santoro, Peter Widmayer

**Source:** STACS 1989; Edsger W. Dijkstra Prize in Distributed Computing, 2024

**Link:** https://doi.org/10.1007/BFb0028994

## Key insight

Synchronized rounds and reliable processors do not make deterministic consensus possible when communication failures can move between senders over time.

## Basic idea

The paper studies agreement under mobile communication faults [1], focusing here on omissions in a synchronous complete network [2]. Even a restricted adversary that selects one sender per round and drops any subset of that sender's outgoing messages can prevent deterministic consensus [3]. All other messages arrive within their round, and no processor needs to crash. A bivalency [4] argument constructs an endless legal execution in which decisions remain unresolved. Detecting a missing message by a deadline does not reveal which omissions other processes experienced or constrain the next round's faulty sender.

## Illustrative example

**Model a round.** Three replicas, Ash, Birch, and Cedar, propose bits. In one round the adversary selects Ash and drops Ash-to-Birch and Ash-to-Cedar, while delivering all other messages. In the next round it may select Birch and drop only Birch-to-Ash. The replicas continue computing throughout. This fault allowance is at most two omitted messages per round in this example, not one omitted message for the whole system.

**Find an unresolved input.** Assume an always-terminating consensus protocol exists. Consider initial input vectors `000`, `100`, `110`, and `111`. Validity fixes the endpoints' decisions to zero and one. If every vector already forced a unique outcome, some adjacent pair would force opposite outcomes while differing only at one replica q. Suppress q's outgoing messages forever. The other replicas have identical observations in both executions and must terminate, so they cannot produce the required opposite decisions. Hence some initial configuration is bivalent.

**Preserve uncertainty.** From a bivalent configuration, consider all possible next-round delivery patterns. For a fixed faulty sender, removing one additional delivery changes only its recipient's resulting local state. The all-delivered pattern connects the possibilities for different faulty senders. If every next configuration were already univalent, both decision values would occur in this connected collection, producing adjacent configurations with different forced outcomes. Their sole differing replica can again be silenced to give all other replicas identical futures, a contradiction. At least one next configuration therefore remains bivalent.

**Repeat.** Choose such a delivery pattern each round. No process can have decided in a bivalent configuration: an irrevocable decision would force all legal continuations to agree with it. This constructs a nonterminating execution even though every process takes a step each round. The result permits omissions to continue indefinitely; it does not establish impossibility under a promise that omissions eventually stop.

## Concepts and terms

**[1] Mobile communication fault.** A transmission failure whose location may change over time, rather than being restricted to one permanently faulty process or link. An omission loses a sent message without changing its contents.

**[2] Synchronous complete network.** Every pair can communicate, and computation proceeds in rounds with a known delivery deadline for nonomitted messages.

**[3] Deterministic consensus.** Processes must eventually choose one common irrevocable output; identical inputs require that same output. Choices follow the protocol without randomization.

**[4] Bivalency.** A complete system configuration has legal continuations deciding zero and others deciding one. A univalent configuration permits only one decision value.

# The Click Modular Router

**Summary by:** GPT 6 Astra

**Author:** Eddie Kohler, Robert Morris, Benjie Chen, John Jannotti, and M. Frans Kaashoek

**Source:** ACM Transactions on Computer Systems 18(3), 2000; SIGOPS Hall of Fame Award 2013

**Link:** https://doi.org/10.1145/354871.354874

**Code:** [Click repository](https://github.com/kohler/click)

## Key insight

A router can be a graph of small packet-processing components rather than one monolithic implementation. Distinguishing producer-driven delivery from consumer-driven requests lets the same composition model express both packet handling and scheduling.

## Basic idea

Click connects elements [1] through typed input and output ports. Push processing [2] moves arriving packets forward, while pull processing [3] lets a consumer request its next packet. Queue elements [4] bridge those modes and make buffering explicit. Configuration checks reject incompatible connections, while optional interfaces and packet annotations [5] let components cooperate without forcing every operation into one fixed router pipeline. Performance comes from lightweight element calls and careful packet handling, not from giving each element a separate operating-system process.

## Illustrative example

**Receive and classify.** A router handles ordinary traffic and latency-sensitive control traffic. Its receive element pushes each packet to a classifier. The classifier sends control packets to queue C and ordinary packets to queue D. Each queue has a push input, so arrivals can be stored immediately without waiting for the output device to request them.

**Pull to schedule.** When the output device can transmit, it pulls from a priority scheduler. The scheduler first pulls from C; if C has no packet, it pulls from D. The selected queue removes one packet and returns it through the scheduler to the device. Scheduling policy is therefore a local element's choice among pull inputs, not a hidden decision embedded in both queues.

**Change policy.** Replacing the priority scheduler with a suitable round-robin scheduler changes service selection while preserving the queues and classifier. A strict-priority configuration can starve D under continuous control traffic; modularity does not make an unfair policy fair. The chosen scheduler's contract must match the desired resource policy.

**Check composition.** Connecting the receive element's push output directly to a device's pull input is invalid: neither end agrees on who initiates transfer. A queue is the explicit boundary that receives pushed packets and later answers pull requests. An agnostic element, such as a simple counter, can operate in either mode, but a particular compatible connection still needs a resolved mode.

**Share packet metadata.** A classifier can attach an annotation, such as information needed later in forwarding, without altering the packet's wire-format bytes. Downstream elements must agree on what that annotation means. A packet buffer can be shared where appropriate, with private copying when a component needs to modify shared data safely.

The graph describes composition, not automatic semantic verification of arbitrary elements. An element that corrupts packet memory or uses an annotation incorrectly can still break the router; type-compatible connections establish only part of the required contract.

## Concepts and terms

**[1] Element.** A reusable packet-processing component with ports, configuration, and possibly additional interfaces for control or inspection. Elements can implement tasks such as classification, lookup, queuing, or device access.

**[2] Push processing.** The upstream element initiates transfer by handing a packet to the downstream element, which must process, forward, queue, or discard it.

**[3] Pull processing.** The downstream element asks upstream for a packet and may receive none. This exposes demand and allows scheduling decisions among upstream sources.

**[4] Queue element.** An explicit buffering component with a push side for arrivals and a pull side for departures, separating reception from transmission timing.

**[5] Packet annotation.** Metadata carried alongside packet contents for internal processing, distinct from bytes transmitted on the network.

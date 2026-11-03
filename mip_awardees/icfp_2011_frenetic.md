# Frenetic: A network programming language

**Summary by:** GPT 6 Astra

**Author:** Nate Foster, Rob Harrison, Michael J. Freedman, Christopher Monsanto, Jennifer Rexford, Alec Story, and David Walker

**Source:** ICFP 2011; SIGPLAN Most Influential ICFP Paper Award 2021.

**Link:** https://doi.org/10.1145/2034773.2034812

**Code:** [Frenetic language and runtime project](https://github.com/frenetic-lang/frenetic)

## Key insight

Network applications should describe the packets they observe and the forwarding behavior they want, rather than coordinate competing low-level switch rules themselves. A runtime can reconcile these descriptions into the rules and counters supported by switches.

## Basic idea

Frenetic separates declarative traffic queries [1] from reactive forwarding policies [2]. Queries filter and aggregate packets into event streams [3], while the policy library combines high-level packet-processing behavior. The runtime installs and maintains OpenFlow rules [4] so applications can reason with a see-every-packet abstraction, even when most traffic stays on the switches. Compositionality concerns this language model; it does not imply arbitrary distributed network updates happen instantaneously.

## Illustrative example

**Requirements.** A switch connects an internal segment on port 3 to an uplink on port 7. A forwarding component sends packets arriving on port 3 to port 7. Independently, a monitor counts packets arriving on port 3 whose destination transport port is 443, reporting one count per ten-second window.

**Low-level conflict.** Installing a broad forwarding rule and a separate overlapping monitoring rule is not sufficient. OpenFlow selects a matching rule according to its priority behavior, so the monitor's rule can hide the forwarding rule or the broad rule can hide the monitor's counter.

**Frenetic description.** The forwarding component specifies its input predicate and output action. The query selects packet counts, filters by ingress port and destination port, and groups arrivals into ten-second windows. Its output is a stream of counts, not a stream containing every packet's payload.

**Runtime reconciliation.** The runtime can distinguish the overlapping class, packets on port 3 destined for 443, from the rest of the forwarding class. The resulting switch behavior both forwards the relevant traffic and accounts for it in the requested statistics. Query results combine the relevant rule counters and runtime observations so the query's meaning does not depend on which packets triggered a controller miss.

In one window, suppose four matching packets and six other packets arrive on port 3. All ten are forwarded by this policy, while the monitoring event reports 4. The denominator is the ten arrivals in this example, not all traffic traversing every switch in the network.

**Cost boundary.** A query requesting packet contents may require controller traffic that a count-only query can avoid. The restricted query language makes this distinction explicit rather than promising that every query runs entirely in switch hardware.

## Concepts and terms

**[1] Declarative traffic query.** A request describing which packets to select, how to group them, and whether to return packets, counts, or sizes.

**[2] Reactive forwarding policy.** A packet-processing policy whose value can change in response to event streams, composed using the language's policy operators.

**[3] Event stream.** A time-indexed sequence of discrete results. Query windows and grouping determine which observations contribute to each result.

**[4] OpenFlow rule.** A low-level entry containing a match pattern, priority, actions, and associated counters. Overlapping rules must be managed to preserve the intended higher-level semantics.


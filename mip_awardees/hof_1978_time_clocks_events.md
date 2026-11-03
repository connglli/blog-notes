# Time, Clocks, and the Ordering of Events in a Distributed System

**Summary by:** GPT 6 Astra

**Author:** Leslie Lamport

**Source:** Communications of the ACM 21(7), 1978; SIGOPS Hall of Fame Award 2007; PODC Influential-Paper Award 2000

**Link:** https://doi.org/10.1145/359545.359563

## Key insight

Distributed events have a causal partial order even without synchronized physical clocks. Counters can preserve that order and, with a tie-breaker, extend it to a consistent total order.

## Basic idea

The happened-before relation [1] follows local process order and message transmission, including their transitive consequences. Lamport logical clocks [2] assign increasing counters so that every causally earlier event receives a smaller timestamp. A receiver advances beyond the timestamp carried by a message as well as its own preceding counter. Adding a fixed process ordering breaks ties and produces a total order [3] consistent with causality. This ordering supports distributed coordination, but the numeric comparison alone does not tell whether two events were causally related.

## Illustrative example

**Advance locally.** Processes A and B begin with counter 0. A performs a local event with timestamp 1 and then sends message M with timestamp 2. Independently, B performs a local event with timestamp 1. Neither process has yet received information about the other's events.

**Receive.** B receives M. It sets its counter to `max(1, 2) + 1 = 3` and timestamps the receive event with 3. A's send therefore precedes B's receive numerically, as required. If B then sends a reply at timestamp 4, A receives it at `max(2, 4) + 1 = 5`.

The causal chain is A's send at 2, B's receive at 3, B's reply at 4, and A's receive at 5. Transitivity makes the first event precede the last without requiring A to know every intermediate physical time.

**Break ties.** Order event identifiers lexicographically by `(counter, process-name)`, choosing A before B for ties. A's local event `(1,A)` is ordered before B's `(1,B)`. That choice is consistent but arbitrary: those two events were concurrent [4], and the total order is not evidence that A influenced B.

**Use the order carefully.** In a coordination protocol, processes can order requests by these pairs. They still need communication sufficient to know when an earlier request cannot arrive unseen. Sorting only the messages received so far does not by itself solve agreement, exclusion, or failure recovery. The paper's mutual-exclusion construction adds request queues, acknowledgments, and release messages under its communication assumptions.

Logical counters measure ordering, not elapsed seconds. A large difference between two counters does not imply a long duration, and `C(a) < C(b)` does not imply that a happened before b. The implication guaranteed by the clock condition goes in the other direction.

## Concepts and terms

**[1] Happened-before relation.** The smallest transitive relation containing each process's local event order and every message-send-before-receive pair. It captures possible causal influence through the modeled system.

**[2] Logical clock.** A per-process counter advanced between events and adjusted on receipt to exceed the received timestamp. It satisfies `a happened-before b => C(a) < C(b)`.

**[3] Total order.** An ordering comparing every pair of distinct events. Counter order plus a consistent process tie-breaker extends the causal partial order without identifying physical simultaneity.

**[4] Concurrent events.** Events for which neither happened before the other. They need not occur at the same wall-clock instant; the definition concerns causal order.

# The tail at scale

**Summary by:** GPT 6 Astra

**Author:** Jeffrey Dean and Luiz André Barroso

**Source:** Communications of the ACM 56(2), 2013; SIGOPS Hall of Fame Award 2025

**Link:** https://doi.org/10.1145/2408776.2408794

## Key insight

A request that waits for many servers inherits their slowest response. Replication can reduce this latency variability as well as tolerate failures, provided duplicate work is controlled.

## Basic idea

In a fan-out service [1], rare delays on individual machines become common delays for complete requests. The paper proposes tail-tolerant execution [2]: reduce interference where practical, then use alternative replicas to avoid waiting for an unusually slow one. A hedged request [3] sends a delayed duplicate and accepts the first answer; tied requests [4] let servers cancel queued duplicates when execution starts. These mechanisms work best when replicas provide interchangeable answers and slowdowns are not shared by every replica.

## Illustrative example

**Setup.** A search request reads 40 independent index partitions and must receive every answer. Suppose each partition has a 2% chance of exceeding the response deadline. Under the example's independence assumption, the probability that the complete request exceeds the deadline is `1 - 0.98^40`, about 55.4%, not 2%.

**Hedging.** Partition 7 has two replicas with equivalent read-only data. Send its read to replica A at time 0. If no answer arrives by 8 ms, send the same read to B. Suppose A is delayed by a background task until 90 ms, while B answers 4 ms after receiving its request. Accept B's answer at 12 ms and cancel A's outstanding request. Other partitions follow the same policy independently.

Choose the delay from measurements for this request class. If 95% of original requests finish before it, approximately 5% of original requests generate one duplicate, assuming the latency distribution remains unchanged. That is a statement about request counts, not a guarantee of only 5% extra CPU work: cancellation timing and workload feedback matter.

**Tying queued work.** Alternatively, enqueue copies at A and B, with each copy naming its partner. If B starts processing first, it sends A a cancellation. A removes its still-queued copy. If both start before cancellation arrives, both may execute; the protocol does not provide mutual exclusion. A small launch delay can reduce this race when both queues are empty.

**Contract.** This example duplicates side-effect-free reads. Sending an arbitrary payment operation twice would require a separate duplicate-suppression contract. If both replicas share the same overloaded disk or the request itself is intrinsically expensive, duplication may not shorten the delay and can add load.

## Concepts and terms

**[1] Fan-out service.** One request creates subrequests to several workers. When all results are required, its latency includes the maximum worker completion time. Independence is useful for the example's calculation, but is not a general property of real systems.

**[2] Tail-tolerant execution.** Techniques that keep high-percentile response times low despite occasional component delays. A percentile describes the fraction of requests completing by a given time, rather than the average completion time.

**[3] Hedged request.** A duplicate sent after the original has remained outstanding for a chosen interval. The client uses the first acceptable result and cancels the other requests.

**[4] Tied requests.** Copies that coordinate at execution start, allowing another server to remove work from its queue before spending resources on it. Cancellation is best effort and has a communication delay.

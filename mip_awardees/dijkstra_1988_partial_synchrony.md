# Consensus in the presence of partial synchrony

**Summary by:** GPT 6 Astra

**Author:** Cynthia Dwork, Nancy Lynch, and Larry Stockmeyer

**Source:** Journal of the ACM 35(2), 1988; Edsger W. Dijkstra Prize in Distributed Computing 2007.

**Link:** https://doi.org/10.1145/42282.42283

## Key insight

A protocol can preserve agreement during arbitrarily bad timing and require improved timing only to finish. Unknown timing bounds and an unknown time after which bounds hold are meaningful intermediate assumptions between full synchrony and full asynchrony.

## Basic idea

Partial synchrony [1] allows fixed but unknown bounds, or known bounds that hold only after an unknown stabilization time [2]. The paper constructs consensus protocols with safety [3] independent of timely delivery and termination once the required timing conditions apply. Coordinated phases, value locks [4], and controlled lock release prevent conflicting decisions across unsuccessful attempts. Fault thresholds depend on the precise model; the illustrated crash/omission algorithm uses `N >= 2f+1`.

## Illustrative example

**Model.** Three processors tolerate at most one crash. Use the paper's basic round model: rounds have common numbers, but messages may be missing before stabilization; sufficiently late rounds deliver messages between correct processors within the round.

Each processor tracks proposed input values it has learned. A phase has a designated coordinator and three trying rounds followed by a lock-release round.

**Try.** Suppose A coordinates after all correct processors know proposed value 6. In the first round, processors report acceptable known values. A needs `N-f = 2` reports accepting 6 before proposing it.

In the second round, A sends a lock request for 6. Recipients lock 6 with this phase number. In the third round they acknowledge. Receiving `f+1 = 2` acknowledgments permits A to decide 6.

**Preserve decisions.** Two processors having locked 6 prevent a later coordinator from obtaining two reports accepting a conflicting value. A processor cannot discard a lock just because its timer expired.

During lock release, processors exchange their locked values and phase numbers. A lock can be released upon learning of a different value locked in a phase at least as new. The protocol's argument shows that the locks supporting the first actual decision cannot be displaced in this way.

**Progress.** Before stabilization, delayed messages can prevent an attempt from gathering the required responses. After a sufficiently late lock-release phase, correct processors' remaining locks agree on at most one value. A subsequent correct coordinator can collect the required reports and acknowledgments and decide.

Implementing this basic round protocol on partially synchronous processors additionally needs the paper's round/clock machinery. A local timeout alone does not establish that other processors are in the same phase.

## Concepts and terms

**[1] Partial synchrony.** A timing model with some eventual or unknown boundedness, stronger than unrestricted asynchronous execution but weaker than known bounds holding from the beginning.

**[2] Stabilization time.** An execution-dependent time after which the stipulated bounds hold. Processes are not told when it occurs.

**[3] Safety.** Agreement and validity requirements that must not be violated even during unsuccessful or delayed phases. Termination is the separate requirement that correct processors eventually decide.

**[4] Value lock.** Persistent protocol state restricting which values a processor considers acceptable, associated with a phase number. Release follows evidence from the protocol rather than an unchecked timeout.


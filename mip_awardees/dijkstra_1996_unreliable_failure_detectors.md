# Unreliable failure detectors for reliable distributed systems

**Summary by:** GPT 6 Astra

**Author:** Tushar Deepak Chandra and Sam Toueg

**Source:** Journal of the ACM 43(2), 1996; Edsger W. Dijkstra Prize in Distributed Computing 2010.

**Link:** https://doi.org/10.1145/226643.226647

## Key insight

Consensus does not require every suspicion of failure to be correct. Separate failure detection from the protocol and state exactly which eventual information is sufficient for progress.

## Basic idea

A failure detector [1] reports suspected crashed processes and is classified by completeness and accuracy [2]. With a correct majority, eventual strong completeness together with eventual protection of one correct process, the class usually written diamond-S [3], suffices for consensus. A rotating coordinator gathers timestamped estimates, proposes the newest, and waits for majority acknowledgments [4]. Detector mistakes can delay progress, but the estimate and quorum rules preserve agreement.

## Illustrative example

**State.** Five processes run a crash-tolerant consensus instance, with at most two crashes. A coordinator needs three responses. Each process stores a proposed value and the round in which it last adopted an estimate.

Suppose a coordinator receives estimates `(0,0)`, `(1,2)`, and `(0,0)`, written as value and timestamp. It selects value 1 because timestamp 2 is largest, then proposes 1 for the current round.

**Accept or suspect.** A recipient that receives the proposal adopts 1, timestamps it with this round, and acknowledges. A recipient that suspects the coordinator before receiving its proposal instead sends a negative acknowledgment and can advance. A false suspicion is permitted; it is not proof that the coordinator stopped.

If the coordinator obtains three positive acknowledgments, it reliably broadcasts a decision for 1. Those acknowledgments establish that a majority adopted the estimate.

**Carry agreement forward.** Any later collection of three estimates intersects that acknowledging majority. The timestamp rule and the protocol's induction ensure that a value supported in the deciding round cannot be displaced by an incompatible later proposal. Mere intersection without the timestamp discipline would not establish this property.

**Eventual progress.** Strong completeness eventually prevents a crashed coordinator from blocking correct processes forever. Eventual weak accuracy supplies one correct process that, after some point, is never suspected by any correct process. When that process coordinates a sufficiently late round, correct processes can collect responses and decide.

Other correct processes may still be falsely suspected indefinitely. The detector contract therefore need not converge to an exact list of all failed processes.

## Concepts and terms

**[1] Failure detector.** An abstract source of failure information attached to each process. Its outputs are assumptions provided to the protocol, not something implementable with guaranteed accuracy in every fully asynchronous execution.

**[2] Completeness and accuracy.** Completeness specifies which crashed processes eventually become permanently suspected. Accuracy limits erroneous suspicions of correct processes, possibly only after an unknown time.

**[3] Diamond-S.** Strong completeness and eventual weak accuracy: every crashed process is eventually permanently suspected by every correct process, and some correct process eventually stops being suspected by any correct process.

**[4] Majority acknowledgment.** Confirmation from more than half the processes that they adopted a proposed estimate. Majority sets intersect, and timestamps preserve the information required across coordinator changes.


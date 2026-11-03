# Reaching agreement in the presence of faults

**Summary by:** GPT 6 Astra

**Author:** Marshall Pease, Robert Shostak, and Leslie Lamport

**Source:** Journal of the ACM 27(2), 1980; Edsger W. Dijkstra Prize in Distributed Computing 2005.

**Link:** https://doi.org/10.1145/322186.322188

## Key insight

A faulty participant can tell different stories to different recipients, so being a minority is not enough to make simple voting reliable. Agreement requires enough independent relaying to reconcile these inconsistent reports.

## Basic idea

The paper formalizes interactive consistency [1]: correct processors must produce the same vector of reported inputs and preserve every correct processor's actual input. Under its reliable, identifiable-sender communication model, Byzantine faults [2] can equivocate [3], and tolerating up to `f` such faults requires at least `3f+1` processors. Recursive information exchange and majority reconstruction achieve that bound. A stronger authenticated-relay assumption [4] changes the problem and is analyzed separately.

## Illustrative example

**One vector entry.** Four processors A, B, C, and D must agree on the input attributed to A, with at most one faulty processor. Suppose A is faulty and sends 0 to B, 1 to C, and 1 to D.

**Relay.** B, C, and D forward to one another what they received from A. Because A is the only faulty processor in this case, their relays are honest. Each correct recipient assembles the same three reports: B's report 0, C's report 1, and D's report 1. Taking the majority gives 1 everywhere.

The chosen value need not be A's genuine private input: the contract imposes no such validity requirement for a faulty sender. It requires consistency among correct recipients.

**Correct sender case.** If A is correct with input 0 and one of B, C, or D is faulty, each correct recipient has the direct 0 from A, a 0 relayed by the other correct recipient, and at most one arbitrary report. Majority therefore preserves A's input.

Applying this construction to each sender gives a consistent vector for the one-fault, four-processor case. Missing messages are assigned agreed default values according to the communication model; absence cannot silently create different local conventions.

**Threshold.** With only three processors and one possible fault, a recipient can be unable to distinguish a lying sender from a lying relay. The paper's indistinguishability argument establishes that no algorithm in this model can always satisfy the requirements. The four-processor example illustrates the sufficient construction, not a replacement for that impossibility proof.

## Concepts and terms

**[1] Interactive consistency.** Agreement on one input value for every processor. Entries for correct processors equal their true inputs; entries for faulty processors may be arbitrary but must agree across correct processors.

**[2] Byzantine fault.** Arbitrary deviation from the protocol, including sending false or inconsistent information. This is stronger than a process simply stopping.

**[3] Equivocation.** Sending incompatible reports to different recipients. An identifiable immediate sender does not provide proof that its account of another processor's message is truthful.

**[4] Authenticated relay.** A stronger assumption preventing a processor from falsely attributing a relayed statement to another sender. Cryptographic techniques can approximate this assumption, which has different resilience limits from the unauthenticated model.


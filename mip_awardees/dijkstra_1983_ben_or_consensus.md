# Another Advantage of Free Choice: Completely Asynchronous Agreement Protocols

**Summary by:** GPT 6 Astra

**Author:** Michael Ben-Or

**Source:** PODC 1983; Edsger W. Dijkstra Prize in Distributed Computing, 2015

**Link:** https://dl.acm.org/citation.cfm?id=806707

## Key insight

Random choices can eventually break an adversarially maintained tie without weakening agreement, even when message delays have no known bound.

## Basic idea

The crash-failure protocol solves binary consensus [1] asynchronously [2] when fewer than half the processes may stop. Each logical round has two message phases: collect estimates, then collect support for a value seen from a strict majority of all processes. Strong support permits a decision, weaker support propagates the value, and absence of support triggers a private random choice [3]. Under fair delivery and continued steps of correct processes, termination has probability one; this is not a fixed round bound.

## Illustrative example

**Parameters.** Use three processes A, B, C and tolerate one crash. Each phase waits for messages from two distinct processes, including itself if applicable. Initial estimates are A=1, B=1, C=0; attach round numbers to messages.

**First phase.** A and B each receive estimates from A and B, both one. Since two exceeds half of three, each broadcasts support for one. C receives A's one and its own zero, so it sends an unknown marker. Two different values cannot both acquire a strict majority in this phase.

**Second phase.** A receives the two support messages and decides one, because two exceeds the crash bound one. C receives one support message and an unknown marker; it adopts one for its next round without deciding yet. A decision is propagated by the continued protocol, so other correct processes can finish consistently rather than treating an immediate local halt as sufficient.

**Tie breaking.** In a round where a process sees no support, it chooses its next estimate randomly. A favorable collection of choices can align the remaining processes. Agreement follows from intersecting support thresholds, while randomness supplies eventual progress. The paper also gives a Byzantine variant under the stricter condition `N > 5t`; the crash protocol's majority threshold must not be reused unchanged against malicious messages.

## Concepts and terms

**[1] Binary consensus.** Correct processes decide one common bit, respecting the common input when all initial inputs agree.

**[2] Asynchrony and crash failure.** No known bound exists on message delay or process speed; a failed process stops rather than sending arbitrary lies.

**[3] Private random choice.** A process draws a fresh local bit when deterministic evidence does not force an estimate; probabilities affect termination, not permission to decide conflicting values.

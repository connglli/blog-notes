# Randomized Byzantine Generals

**Summary by:** GPT 6 Astra

**Author:** Michael O. Rabin

**Source:** FOCS 1983; Edsger W. Dijkstra Prize in Distributed Computing, 2015

**Link:** https://doi.org/10.1109/SFCS.1983.48

## Key insight

A common random choice, hidden until processes have committed enough information, can break an adversary's control over repeated disagreement much faster than independent local coins.

## Basic idea

The protocol alternates polling, a shared lottery [1], and an update rule for Byzantine agreement [2]. A trusted dealer distributes signed secret shares [3] of future random bits, enabling correct processes to recover the same bit without allowing the faulty minority to learn it early. The paper's analyzed general protocol uses `t < n/10`, not the optimal modern fault threshold. It presents both bounded-round probabilistic agreement and an errorless variant with bounded expected rounds under its setup and delivery assumptions.

## Illustrative example

**Setup.** Take eleven processes and at most one faulty process. Before execution, a correct dealer prepares independent random bits and gives each process a signed share of each bit, labeled by lottery round. Two shares reconstruct a bit; one share does not reveal it. Authentication prevents the faulty process from inventing another valid dealer share.

**Polling.** In a round, each process collects ten authenticated estimates and selects the most frequent value. Suppose eight correct processes favor Cedar and two favor Birch. Even a ten-message sample omitting one Cedar vote and including the faulty process contains at least seven Cedar votes. Thus every correct process selects Cedar as its local plurality.

**Lottery and update.** After the required polling stage, processes exchange valid shares to recover the common bit. For one bit value, the update rule accepts a plurality exceeding half the population; seven exceeds `11/2`, so all correct processes adopt Cedar. For the other value, the rule demands support at least `n-2t = 9`, otherwise adopting a distinguished fault value. The common bit, rather than separate independent coins, makes these choices coordinated.

**Boundary.** This favorable round illustrates the mechanism, not the complete correctness proof or stopping test. Reusing an already exposed lottery bit would let the adversary anticipate the choice. Removing the trusted dealer or digital-signature assumptions requires a different construction; secret sharing alone does not supply authenticated unpredictable common randomness.

## Concepts and terms

**[1] Shared lottery.** Correct participants obtain the same random bit, with timing constraints preventing premature adversarial knowledge.

**[2] Byzantine agreement.** Correct processes agree despite arbitrary deviations by faulty processes, and preserve a common correct initial value.

**[3] Signed secret shares.** Pieces reconstructing a secret only when enough are combined, authenticated by a dealer so forged pieces can be rejected.

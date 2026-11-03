# Computation in Networks of Passively Mobile Finite-State Sensors

**Summary by:** GPT 6 Astra

**Author:** Dana Angluin, James Aspnes, Zoë Diamadi, Michael J. Fischer, René Peralta

**Source:** PODC 2004; Distributed Computing 18(4), 2006; Edsger W. Dijkstra Prize in Distributed Computing, 2020

**Link:** https://doi.org/10.1007/s00446-005-0138-3

## Key insight

Agents with only finitely many states can collectively compute useful global predicates through repeated pairwise encounters, without knowing the population size or controlling movement.

## Basic idea

A population protocol [1] specifies initial states, pairwise transition rules, and an output for each state. The population size is finite but unbounded, while each agent's state set is fixed independently of that size. Under a fairness condition [2], correct stable computation [3] requires all agents eventually to report the right result permanently, without necessarily detecting that stabilization has occurred. The paper also studies a random-interaction model, which is a stronger scheduling assumption than fairness alone.

## Illustrative example

**Predicate.** Decide whether at least two sensors initially detect an alarm. Use three states: `quiet`, `witness`, and `confirmed`. Initialize each positive sensor to witness and each other sensor to quiet. Only confirmed outputs yes; both other states output no.

**Rules.** Two witnesses meeting become two confirmed agents. A confirmed agent meeting any other agent makes both confirmed. Every other interaction leaves states unchanged. These rules use only three states, whether there are five sensors or five million.

**Run.** Start five agents in states `(witness, quiet, witness, quiet, quiet)`. When the two witnesses meet, there are two confirmed agents. Encounters with quiet agents spread confirmation until all five output yes. If there was only one initial witness, no transition could create a confirmed agent, and every agent would correctly output no throughout.

**Correctness.** A first confirmation requires two distinct witnesses, and no rule duplicates an unconfirmed witness. Thus a false yes cannot appear. With at least two witnesses, an execution that forever avoids both confirmation and its subsequent spread violates the relevant fairness requirement. Once every agent is confirmed, further interactions cannot change the output. No agent needs a counter for the total population or a global termination announcement; the guarantee is eventual stabilization, not a known number of encounters.

## Concepts and terms

**[1] Population protocol.** A fixed finite-state transition system applied to pairs of indistinguishable mobile agents.

**[2] Fairness.** If a population configuration occurs infinitely often, every configuration obtainable from it by one allowed interaction must also occur infinitely often. This is not a probability distribution over pairs.

**[3] Stable computation.** Eventually every reachable continuation preserves the correct output at all agents, even though internal transitions may continue.

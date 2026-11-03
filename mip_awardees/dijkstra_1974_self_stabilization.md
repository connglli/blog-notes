# Self-stabilizing systems in spite of distributed control

**Summary by:** GPT 6 Astra

**Author:** Edsger W. Dijkstra

**Source:** Communications of the ACM 17(11), 1974; PODC Influential-Paper Award 2002.

**Link:** https://doi.org/10.1145/361179.361202

## Key insight

Local rules can restore a global coordination invariant even when the initial state is arbitrary. Correctness requires both eventual recovery and preservation of the recovered invariant.

## Basic idea

A self-stabilizing system [1] reaches a legitimate state [2] from every initial state and thereafter stays legitimate. Dijkstra gives ring protocols whose local privileges [3] identify machines permitted to move. A central daemon [4] selects one enabled move at a time, with no prescribed selection order. In the K-state construction, one distinguished machine increments its value when it equals its predecessor, while every other machine copies a different predecessor value.

## Illustrative example

**Rules.** Use four machines in a directed ring, indexed 0 through 3, with values modulo 5. Machine 0 is enabled when its value equals machine 3's value; it then increments modulo 5. Machine `i > 0` is enabled when its value differs from machine `i-1`; it then copies that predecessor.

This satisfies the paper's stated parameter condition: for machines 0 through `N`, use `K > N`. Here `N = 3` and `K = 5`.

**Recovery trace.** Start in state `[0,2,2,3]`. Machines 1 and 3 are both enabled, so the global single-privilege condition does not hold.

Choose machine 1, producing `[0,0,2,3]`. Choose machine 2, producing `[0,0,0,3]`. Choose machine 3, producing `[0,0,0,0]`. Only machine 0 is enabled in the resulting state.

**Legitimate execution.** Machine 0 increments to produce `[1,0,0,0]`. Only machine 1 is enabled, and copying propagates the 1 around the ring until `[1,1,1,1]`. The privilege returns to machine 0, which introduces the next value.

This one recovery trace illustrates the rules, not the universal convergence argument. The construction's guarantee quantifies over every initial state and every sequence of enabled selections by the central daemon. The distinguished machine and sufficiently many values are essential parts of that construction; removing them creates a different protocol.

**Failure model.** Arbitrary transient state corruption can be treated as choosing a new initial state after the disruption stops. The guarantee is not that a system remains legitimate while an adversary keeps corrupting variables or while machines permanently cease executing the protocol.

## Concepts and terms

**[1] Self-stabilization.** Convergence to legitimate behavior from arbitrary state, followed by closure: subsequent allowed steps preserve legitimacy.

**[2] Legitimate state.** A global state satisfying the chosen coordination criterion. In the illustrated construction, exactly one privilege is present, representing a unique circulating permission to act.

**[3] Privilege.** A Boolean guard on a machine's state and neighboring states. When true, it permits a specified local update.

**[4] Central daemon.** An abstract scheduler executing one currently enabled move atomically at a time. It does not compute the update or supply global information to the machine; replacing it with a different concurrency model requires another argument.


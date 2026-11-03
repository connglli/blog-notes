# Defining Liveness

**Summary by:** GPT 6 Astra

**Author:** Bowen Alpern, Fred B. Schneider

**Source:** Information Processing Letters 21(4), 1985; Edsger W. Dijkstra Prize in Distributed Computing, 2018

**Link:** https://doi.org/10.1016/0020-0190%2885%2990056-0

## Key insight

A safety violation becomes irreversible after some finite prefix, while a pure liveness requirement always leaves every finite prefix extendable to a successful execution.

## Basic idea

Represent a property as a set of infinite executions [1]. Safety [2] excludes executions with finite, irreparable bad prefixes; liveness [3] permits a satisfying continuation from every finite prefix. In the prefix topology [4], safety properties are closed sets and liveness properties are dense sets. Every property can be expressed as the intersection of one safety property and one liveness property.

## Illustrative example

**Execution alphabet.** A service produces a sequence of `idle`, `grant`, and `error` events. Require that it never emits `error` and emits `grant` infinitely often. This is a property of complete infinite traces, not merely the states reached during a finite test.

**Safety part.** "No error ever occurs" is safety. After the prefix `idle, grant, error`, no extension can remove the recorded error. A monitor can therefore establish a violation after observing that finite prefix, even though it cannot certify that an error-free finite execution will remain error-free forever.

**Liveness part.** "Grants occur infinitely often" is liveness. Extend any finite prefix by infinitely many grants and the resulting trace satisfies it. Even a million consecutive idle events cannot prove failure: a later infinite sequence of grants remains possible. The all-idle infinite trace violates liveness despite having no finite bad prefix.

**General construction.** For an arbitrary property P, form C from executions whose every finite prefix can still be extended to some execution in P. C is P's smallest containing safety property. Set `L = P union complement(C)`. Then `C intersection L = P`, and every finite prefix has an extension in L. In the service example, C is precisely the error-free traces; the construction supplies a liveness factor, though it need not be the most intuitive or unique decomposition.

## Concepts and terms

**[1] Infinite execution.** An infinite state or event sequence; a terminating computation can be represented by repeating its final state.

**[2] Safety.** Every excluded execution has a finite prefix that no satisfying execution extends.

**[3] Liveness.** Every finite prefix has at least one infinite extension satisfying the property, considered over the specified execution universe.

**[4] Prefix topology.** Basic open sets contain all executions extending a chosen finite prefix; closed sets contain their limit executions, and dense sets intersect every nonempty basic open set.

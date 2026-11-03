# Anytime, anywhere: Modal logics for mobile ambients

**Summary by:** GPT 6 Astra

**Author:** Luca Cardelli and Andrew D. Gordon

**Source:** POPL 2000; SIGPLAN Most Influential POPL Paper Award 2010.

**Link:** https://doi.org/10.1145/325694.325742

## Key insight

A specification for mobile computation must describe both the shape of nested locations and how that shape can change. Spatial and temporal operators can express these two dimensions within one logic.

## Basic idea

The ambient calculus [1] represents movable, named locations containing other processes and locations. Spatial formulas [2] describe how a process decomposes into adjacent components or a named container, while temporal possibility [3] describes configurations reachable by execution. The paper defines satisfaction against the process semantics, logical reasoning rules, and a model-checking method for a restricted finite setting. The presented calculus uses public names; private-name restriction is outside its treatment.

## Illustrative example

**Setup.** A parcel is beside a depot and can enter it. Write the process as `parcel[in depot.0] | depot[0]`. Here `0` does nothing, square brackets enclose a location's contents, and the vertical bar places two components side by side.

Initially the parcel executes the capability `in depot`. The ambient movement rule allows a location to enter a sibling location with that name, giving `depot[parcel[0]]`.

**Spatial query.** The formula `depot[parcel[0]]`, interpreted as a formula rather than a process, describes precisely a depot containing an empty parcel, with no additional components hidden by the notation. It is false initially and true after the move.

For a less restrictive property, use `depot[parcel[true] | true] | true`. The inner `true` allows arbitrary parcel contents, the next allows other depot contents, and the outer one allows other top-level processes. This property says that some top-level depot directly contains a parcel, without requiring either location to be otherwise empty.

**Temporal query.** Prefixing the latter property with the eventual-possibility operator asks whether some sequence of reductions reaches a matching configuration. The single movement step witnesses that claim. It does not say that every execution delivers the parcel, nor that delivery occurs within a time deadline.

A small checker for this example enumerates reachable configurations, modulo harmless structural rearrangements, and tests the spatial formula at each. Testing a parallel-composition formula requires finding a decomposition whose two parts satisfy the respective subformulas. General replication and unbounded behavior cannot be handled by assuming this finite search always terminates.

## Concepts and terms

**[1] Ambient calculus.** A process language in which named containers move using capabilities such as entering a sibling, leaving a parent, or dissolving a boundary. Structural congruence identifies harmless rearrangements, such as swapping parallel components.

**[2] Spatial formula.** A proposition about a process's current arrangement. `n[A]` requires a location named `n` whose contents satisfy `A`; `A | B` requires a decomposition into components satisfying the two formulas.

**[3] Temporal possibility.** A modality true when zero or more execution steps can reach a process satisfying its argument. Possibility is existential over executions and is distinct from a universal progress guarantee.


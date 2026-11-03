# Views: Compositional reasoning for concurrent programs

**Summary by:** GPT 6 Astra

**Author:** Thomas Dinsdale-Young, Lars Birkedal, Philippa Gardner, Matthew Parkinson, and Hongseok Yang

**Source:** POPL 2013; SIGPLAN Most Influential POPL Paper Award 2023.

**Link:** https://doi.org/10.1145/2429069.2429104

**Artifact:** [Original Coq proofs and examples](https://sites.google.com/site/viewsmodel/)

## Key insight

Concurrent reasoning needs an abstraction of each thread's knowledge and permissions, together with a way to compose those abstractions. A shared metatheory can then establish the soundness of many different logics and type systems.

## Basic idea

A view [1] summarizes machine state and the rights available to a thread. Views have a composition operator [2] and a reification [3] into concrete states. Each atomic-command axiom must remain sound when composed with an arbitrary environment view, which is the central locality condition [4]. Once these obligations are established, generic rules for sequencing, choice, iteration, and parallel composition support reasoning about whole programs.

## Illustrative example

**Choose an instance.** Use views describing exclusive ownership of heap cells. Let `p` mean ownership of cell `left` containing 2, and `r` ownership of distinct cell `right` containing 5. Their composition `p * r` describes ownership of both cells. Attempting to compose incompatible exclusive claims about the same cell gives an impossible view.

**Atomic axiom.** Thread A atomically writes 3 to `left`. Its local axiom changes `p` to `q`, where `q` owns `left` containing 3. To use this as a framework axiom, establish that the command maps every concrete state described by `p * environment` into one described by `q * environment`.

For the environment `r`, the write leaves `right` at 5. The check must work for every compatible environment, not only this convenient example.

**Parallel composition.** Thread B independently writes 9 to `right`, changing `r` to `s`. The generic parallel rule combines the local specifications into a specification changing `p * r` to `q * s`. Either interleaving gives `left = 3` and `right = 9`.

The heap example resembles separation logic, but disjoint heaps are not built into the framework. Another instance might compose type environments by agreement on shared values, or incorporate assumptions about interference. In each case the author of the instance must supply the view algebra, reification, and valid atomic axioms.

**Implementation boundary.** A small checker can represent the heap instance with finite ownership maps and reject overlapping claims. That implements this instance's resource compatibility, not an automatic procedure for finding every useful concurrent invariant.

## Concepts and terms

**[1] View.** An abstract assertion representing the local perspective from which a thread is verified. It can encode permissions as well as facts about values.

**[2] Composition operator.** An associative, commutative way to combine compatible views into a joint view. It supplies the meaning of combining thread specifications.

**[3] Reification.** A mapping from an abstract view to the concrete machine states it describes. It connects algebraic reasoning to operational execution.

**[4] Locality condition.** Atomic axioms must preserve arbitrary composable environment views. This framed condition allows a thread's proof to remain valid when other compatible threads are present.


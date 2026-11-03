# Subject-Oriented Programming (A Critique of Pure Objects)

**Summary by:** GPT 6 Astra

**Author:** William Harrison, Harold Ossher

**Source:** OOPSLA 1993; SIGPLAN Most Influential OOPSLA Paper selection for 1986-1996 (retrospective award)

**Link:** https://doi.org/10.1145/165854.165932

## Key insight

Independently developed applications can share an object's identity without agreeing on one complete class, state representation, or implementation of its behavior.

## Basic idea

A subject [1] defines the classes, state descriptions, and behavior relevant to one application, and a subject activation [2] supplies its runtime state. Different activations associate their own class and fields with the same object identifier [3]. Composition rules [4] connect these views by matching operations and classes and deciding which methods execute for a call. The paper's merge rule [5] illustrates coordinated behavior across subjects, but composing arbitrary applications still requires agreement about their interfaces and classifications.

## Illustrative example

**Separate views.** A library's circulation subject classifies a volume as `LoanItem`, with `borrower` and `loanBlocked` fields. Its conservation subject classifies that same volume as `Repairable`, with a `damageCount` field. Both activations use identifier 73 for the volume, but neither method implementation can directly access fields declared only by the other subject. The subjects describe many objects and classes; a subject is not another name for one object or one class.

**Create.** A composition rule matches circulation's `LoanItem` to conservation's `Repairable` and matches their `reportDamage` operations. Allocate identifier 73, assign its class separately in each activation, and initialize the two state records. A simple implementation keeps per-activation maps from identifiers to classes and state. The paper also permits deferred state initialization when an activation first needs an object.

**Dispatch.** Call `reportDamage(73)`. Under merge, dispatch sequentially within each participating activation, in arbitrary order. Circulation's local method records that the volume cannot be loaned; conservation's method increments its damage count. Each method is selected using that activation's classification of identifier 73. With separate state and no result, these effects do not depend on the dispatch order.

**Check the contract.** Suppose both subjects also supply a Boolean `isDamaged(73)` query. If one returns true and the other false, merge raises an exception rather than silently choosing a view. Operations with in-out parameters need commutative updates for this unordered composition to behave consistently. A new insurance subject can add its own value field without changing either existing state layout, but its class and operation correspondences still need a composition rule.

## Concepts and terms

**[1] Subject.** A specification of a partial view of the world, including its own class hierarchy and method definitions; the specification itself contains no runtime object state.

**[2] Subject activation.** An executing instance of a subject, mapping relevant object identifiers to its classes and state. Multiple activations of one subject may hold different state.

**[3] Object identifier.** A unique identity in the composed universe, independent of any subject's representation of the object.

**[4] Composition rule.** The policy connecting subjects, including class and interface matching, method combination, and any shared state or scope boundaries.

**[5] Merge.** A composition policy calling each applicable local implementation sequentially, requiring returned values to agree, and expecting commutative use of in-out parameters.

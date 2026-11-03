# Ivy: Safety Verification by Interactive Generalization

**Summary by:** GPT 6 Astra

**Author:** Oded Padon, Kenneth L. McMillan, Aurojit Panda, Mooly Sagiv, Sharon Shoham

**Source:** PLDI 2016; SIGPLAN Most Influential PLDI Paper Award, 2026

**Link:** https://doi.org/10.1145/2908080.2908118

**Code:** [Ivy](https://github.com/microsoft/ivy)

## Key insight

Make a failed proof concrete: show a state that defeats induction, then let the user help generalize the reason that state should be unreachable.

## Basic idea

Ivy checks safety by constructing an inductive invariant [1] for a relational transition system [2]. Its restricted language keeps the relevant logical queries decidable [3]. If a candidate fails, Ivy displays a counterexample to induction [4]; the user removes irrelevant facts, and automatic generalization checks and simplifies the resulting conjecture. Bounded checking can reject a conjecture, but only the final induction checks establish unbounded safety.

## Illustrative example

**Model.** Consider arbitrarily many clients and one Boolean `free`. Initially `free` is true and no client holds a resource. `acquire(n)` requires `free`, sets it false, and sets `holds(n)` true. `release(n)` requires `holds(n)`, clears it, and sets `free` true. Actions are atomic. The goal is that two distinct clients never hold the resource together.

**Failed induction.** Let the candidate invariant state only that goal. The state `holds(A)`, not `holds(B)`, and `free` satisfies it. Yet `acquire(B)` produces two holders. This is a failed induction step, not an execution from initialization: the starting state combines a holder with a free resource.

**Generalization.** Forget B and all other clients. Retain just `free` and `holds(A)`. Excluding this smaller pattern gives the conjecture `forall n. not (free and holds(n))`. A bounded search can test whether such a pattern is reachable; passing that test alone proves nothing about longer runs.

**Proof.** Conjoin the conjecture with the original goal. Initialization satisfies both. Acquisition starts with no holders because `free` is true. Release starts with exactly one holder, clears it, and restores `free`. Thus both clauses survive every action, proving the goal for any number of clients and steps.

## Concepts and terms

**[1] Inductive invariant.** A predicate true initially and preserved by every transition; it proves a safety property when it implies that property.

**[2] Relational transition system.** A state assigns truth values to relations; actions update those relations. A unary relation such as `holds` represents a set.

**[3] Decidable query.** A logical question with a terminating decision procedure. Ivy uses restrictions related to effectively propositional logic, not unrestricted arithmetic.

**[4] Counterexample to induction.** A candidate-satisfying state and an allowed successor violating the candidate. The first state need not be reachable.

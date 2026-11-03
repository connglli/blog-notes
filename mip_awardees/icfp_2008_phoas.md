# Parametric higher-order abstract syntax for mechanized semantics

**Summary by:** GPT 6 Astra

**Author:** Adam Chlipala

**Source:** ICFP 2008; SIGPLAN Most Influential ICFP Paper Award 2018.

**Link:** https://doi.org/10.1145/1411204.1411226

**Artifact:** [Lambda Tamer releases, ICFP 2008 release dated 20080328](https://ltamer.sourceforge.net/old.html)

## Key insight

Represent bound variables using the host language's binders, but keep their representation abstract. Instantiating that abstract variable type differently lets one traverse syntax without manually implementing name substitution throughout every proof.

## Basic idea

Parametric higher-order abstract syntax, PHOAS [1], defines syntax as `term(V)`, where `V` is the type used to represent variables. A binder contains a host-language function `V -> term(V)`, and a closed representation quantifies over `V`. Parametricity [2] motivates why such terms cannot inspect the representation of variables, while strict positivity [3] permits the datatype in Coq. The mechanized correctness development explicitly uses suitable well-formedness properties [4] rather than assuming a proved general parametricity theorem for all of Coq.

## Illustrative example

**Represent a term.** Consider the untyped expression `lambda first. lambda second. first second first`. Its syntax has two binders, two applications, and three variable occurrences.

Using constructors `Var`, `App`, and `Abs`, represent the first binder by a host function receiving `first : V`. Its result contains a second host function receiving `second : V`, whose body is `App(App(Var first, Var second), Var first)`. No string name is compared to decide which occurrence belongs to which binder.

**Count occurrences.** Instantiate `V` with the one-element type `Unit`. Define the traversal to count a `Var` as 1, add the counts of an application's two children, and process an abstraction by applying its body function to the sole Unit value before recursing.

For the example, the inner application contributes `1 + 1 = 2`, and the outer application contributes `2 + 1 = 3`. This counts occurrences, not distinct variables: replacing both bound variables by the same Unit value is intentional.

**Other traversals.** To distinguish one binder from others, instantiate variables with tags instead. To implement substitution, instantiate them with syntax and then flatten the resulting representation. The operation chooses what information to place in variables; the original uniformly represented term does not choose how to inspect it.

The representation simplifies binding mechanics but does not prove a compiler transformation correct by itself. Type-indexed syntax and semantic-preservation proofs still establish the transformation's substantive properties.

## Concepts and terms

**[1] PHOAS.** A syntax encoding parameterized by a variable representation, using host-language functions for binders and an explicit constructor for variable occurrences.

**[2] Parametricity.** Uniform behavior with respect to an abstract type parameter. In the intended encoding, a polymorphic term can pass variables around but cannot branch on an unknown variable representation.

**[3] Strict positivity.** A restriction on inductive definitions that excludes recursive occurrences in certain function-input positions. Using `V -> term(V)` avoids the problematic `term -> term` binder argument.

**[4] Well-formedness property.** An explicit condition relating different instantiations of a represented term, used in the paper's mechanized proofs to obtain the needed parametric behavior without adding an unjustified global metatheorem.


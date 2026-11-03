# 1ML: Core and modules united (F-ing first-class modules)

**Summary by:** GPT 6 Astra

**Author:** Andreas Rossberg

**Source:** ICFP 2015; SIGPLAN Most Influential ICFP Paper Award 2025.

**Link:** https://doi.org/10.1145/2858949.2784738

**Code:** [1ML prototype interpreter](https://github.com/rossberg/1ml)

## Key insight

ML's separate core and module languages can share one set of constructs. First-class modules become ordinary values, while a small-versus-large type distinction supplies the restrictions needed for tractable type checking.

## Basic idea

1ML unifies records with structures and functions with functors, making modules first-class [1]. Reified types [2] can occur in these values, and abstract interfaces hide representation details. An elaboration [3] translates the language into System Fω rather than requiring unrestricted dependent types. A small/large type distinction [4] controls polymorphic instantiation and inference; inference is intentionally incomplete rather than solving every possible module-type reconstruction problem.

## Illustrative example

**Interface.** A counter package exposes a type `T`, a value `zero : T`, an operation `step : T -> T`, and a renderer `show : T -> String`. One implementation represents counters by integers. Another represents them by lists of unit values, with one list element for each increment.

Both can hide their concrete `T` behind the same interface. Their representation types need not be equal.

**Dynamic selection.** A runtime Boolean chooses one of these packages. The result is an ordinary first-class value `chosen`. The client evaluates `chosen.step chosen.zero` and passes the result to `chosen.show`.

For correctly implemented counters, either package renders one. The typing argument establishes that the operations and values agree on the selected abstract type, not that independently written implementations necessarily obey the same mathematical counter specification.

**Type identity.** The client cannot insert the integer 1 directly where `chosen.T` is expected: after dynamic selection, it does not know which representation was chosen. It also cannot mix a value from one independently abstract package with another package's operations merely because both expose a field named `T`.

**Elaboration.** Conceptually, translate the package into an existentially hidden representation type plus operations over it. The conditional selects values at a common package interface. Unpacking introduces a consistent abstract representation used by all the selected fields.

Type reification makes type-level abstraction available through the same source-language constructs used for values. The small/large distinction prevents unrestricted impredicative module matching, and large types may require explicit annotations. The design therefore unifies syntax and expression forms without promising that every arbitrary computation can determine an admissible static type.

## Concepts and terms

**[1] First-class module.** A module that can be passed to a function, returned, stored, or chosen by an ordinary conditional, rather than existing only in a separate static module layer.

**[2] Reified type.** A type made available through a value-level form so it can participate in module-like abstraction and application. Uses can expose its identity transparently or keep it abstract.

**[3] Elaboration.** Translation from surface expressions and types into a more explicit core calculus, making hidden quantification and abstraction precise. System Fω includes polymorphism and type operators.

**[4] Small and large types.** A semantic stratification restricting which types can instantiate abstract type parameters and be inferred automatically. Large module-style types can contain abstraction structure that requires stronger annotation discipline.


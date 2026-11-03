# Recursive structures for Standard ML

**Summary by:** GPT 6 Astra

**Author:** Claudio V. Russo

**Source:** ICFP 2001; SIGPLAN Most Influential ICFP Paper Award 2011.

**Link:** https://doi.org/10.1145/507635.507644

**Code:** [Moscow ML project](https://github.com/kfl/mosml)

## Key insight

Mutually dependent definitions need not be merged into one module. Explicit forward signatures can name the needed types and values, provided the eventual definitions preserve their identities and recursive initialization is controlled.

## Basic idea

The extension adds recursive signatures [1] for cross-module type dependencies and recursive structures [2] for value dependencies. A forward declaration supplies the information needed to check a recursive reference, and enrichment [3] checks that the body supplies at least that interface. Datatype identity [4] is preserved using the required type realizations and datatype replication rather than inventing unrelated copies. Evaluation constructs the body eagerly with an initially undefined recursive binding and signals an exception if that binding is demanded too soon.

## Illustrative example

**Setup.** Two modules represent mutually recursive syntax. `Expr` contains integer literals and a form embedding a `Test`. `Test` contains a form testing whether an `Expr` is zero. Each module also exports an evaluator.

Checking the declaration of `Expr` requires the name of `Test.t` before the latter's full declaration exists. Checking `Expr`'s evaluator also requires the type of `Test.evaluate`.

**Type knot.** Provide a recursive signature that forward-declares the needed type and then gives the two datatype specifications. The equations must be mediated by datatype constructors, rather than an unproductive circular type abbreviation. The recursive signature ties the forward `Test.t` to the actual datatype specification.

The implementations replicate the datatypes named by this signature. They do not redeclare fresh, merely similar datatypes, which would create different type identities and break the intended cross-module uses.

**Value knot.** Construct one recursive structure containing the two module bodies. Their evaluator definitions are function closures. A call from `Expr.evaluate` to the forward `Test.evaluate` is delayed inside a function body, so it is not performed during initialization.

Once both substructures are built, bind the recursive name to the completed structure. Evaluating a test of literal zero can then call the expression evaluator and return true, with both functions referring to the same completed module family.

**Premature use.** A top-level initializer that immediately calls the forward evaluator before the recursive structure is completed instead raises the initialization exception. Having a suitable static signature does not establish that every initialization order is safe.

## Concepts and terms

**[1] Recursive signature.** A signature expression checked under a forward structure declaration. Its type realization connects forward abstract names to the body's type components, subject to a contractiveness requirement.

**[2] Recursive structure.** A module body evaluated with a recursive name provisionally bound, then tied to the completed value. Its resulting interface is determined by the body, not limited to the forward declaration.

**[3] Enrichment.** The module-matching relation requiring a body to provide the components and types demanded by an interface; additional components are permitted.

**[4] Datatype identity.** The identity associated with a particular datatype definition. Datatype replication reuses that identity and its constructors instead of creating an incompatible fresh definition.


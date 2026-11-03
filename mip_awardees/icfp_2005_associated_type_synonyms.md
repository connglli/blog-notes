# Associated type synonyms

**Summary by:** GPT 6 Astra

**Author:** Manuel M. T. Chakravarty, Gabriele Keller, and Simon Peyton Jones

**Source:** ICFP 2005; SIGPLAN Most Influential ICFP Paper Award 2015.

**Link:** https://doi.org/10.1145/1086365.1086397

**Code:** [Glasgow Haskell Compiler project](https://github.com/ghc/ghc)

## Key insight

When one type determines another, express the dependency as a type-level function belonging to the interface. Equality constraints let clients state relationships between these computed types without requiring the computation to be invertible.

## Basic idea

An associated type synonym [1] is declared within a type class [2] and defined by its instances. Methods can mention the associated type, so their signatures depend directly on the instance's representation type. Type checking reduces applicable type equations and uses equality constraints [3] where computed types must coincide. The paper restricts instance equations to maintain suitable confluence and termination [4]; associated type functions are not assumed injective.

## Illustrative example

**Interface.** A storage interface associates each store representation with the type of its key. In Haskell notation:

```haskell
{-# LANGUAGE TypeFamilies #-}

class Store s where
  type Key s
  lookupText :: s -> Key s -> Maybe String

newtype Numbered = Numbered [(Int, String)]

instance Store Numbered where
  type Key Numbered = Int
  lookupText (Numbered entries) key = lookup key entries
```

The definition is a small illustration using present Haskell syntax. The paper's contribution is the associated equation and its type-checking treatment.

**Reduction.** For a value `db :: Numbered`, the expression `lookupText db 4` requires the second argument to have type `Key Numbered`. The instance equation reduces that type to `Int`, so the integer key is accepted. A string key fails that obligation.

A generic routine comparing keys from stores of types `s` and `t` needs evidence that `Key s = Key t`, in addition to the relevant class constraints. It cannot infer this equality merely because both types implement `Store`.

**Non-injectivity.** Another store representation might also choose integer keys. Thus `Key s = Int` does not imply `s = Numbered`, and `Key s = Key t` does not imply `s = t`. A unifier that decomposed these equalities as if `Key` were an ordinary injective datatype constructor would be incorrect.

**Open definitions.** A new instance can add a new associated equation without editing the class declaration. The instance discipline prevents overlapping definitions from choosing incompatible reductions for the same argument and prevents unchecked recursive type equations from making normalization diverge.

## Concepts and terms

**[1] Associated type synonym.** A type-level function connected to a class, with its equations supplied by class instances. It computes a type rather than declaring a fresh data representation.

**[2] Type class.** An interface whose methods and constraints are selected according to types. Associated synonyms allow the interface to include type-level members as well as value-level methods.

**[3] Equality constraint.** A requirement that two type expressions denote the same type. It can relate associated-type results without equating the inputs that produced them.

**[4] Confluence and termination.** Confluence makes different valid reduction paths agree; termination prevents an endless sequence of type reductions. The paper imposes syntactic conditions on instance definitions to support these properties.


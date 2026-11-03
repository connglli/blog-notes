# Simple unification-based type inference for GADTs

**Summary by:** GPT 6 Astra

**Author:** Simon Peyton Jones, Dimitrios Vytiniotis, Stephanie Weirich, and Geoffrey Washburn

**Source:** ICFP 2006; SIGPLAN Most Influential ICFP Paper Award 2016.

**Link:** https://doi.org/10.1145/1159803.1159811

**Code:** [Glasgow Haskell Compiler project](https://github.com/ghc/ghc)

## Key insight

A constructor match can reveal new type equalities, but inference must distinguish deliberately specified types from types still being guessed. Annotations provide stable information on which branch-local refinement can rely.

## Basic idea

Generalized algebraic datatypes, or GADTs [1], give constructors result types that can specialize a datatype's parameters. Pattern matching reveals local type equalities [2], making ordinary unconstrained unification insufficient for complete inference. The paper distinguishes rigid and wobbly types [3] and uses annotations to control when refinement applies. This supports a practical unification-based algorithm while avoiding a claim of principal, annotation-free inference for every GADT program.

## Illustrative example

**Datatype and interface.** A payload stores either an integer or a Boolean while recording that choice in its type:

```haskell
{-# LANGUAGE GADTs #-}

data Payload a where
  Count :: Int -> Payload Int
  Flag  :: Bool -> Payload Bool

extract :: Payload a -> a
extract (Count n) = n
extract (Flag b) = b
```

**Integer branch.** The signature tells the checker that the scrutinee has type `Payload a` and the result must have type `a`. Matching `Count`, whose result type is `Payload Int`, establishes `a = Int` within this branch. Returning `n :: Int` therefore satisfies the expected result type.

**Boolean branch.** Matching `Flag` instead establishes `a = Bool` locally. The result `b :: Bool` is valid under that equality. The two branches do not globally force `Int = Bool`; each equality belongs to its own matching context.

**Inference boundary.** Without the signature, observing an integer result in one branch and a Boolean result in another does not tell an ordinary unifier to invent the relationship between the input index and the result. The programmer-supplied type establishes the intended polymorphism and supplies rigid information.

A rough checker propagates expected types from annotations, records rigid versus uncertain bindings, and introduces constructor equalities while checking each branch. It must not let a branch-specific equality escape and mutate an unrelated inference variable for the whole function.

For `extract (Count 23)`, the result is 23 with type `Int`. A call attempting to use that same result as a Boolean is rejected by the ordinary application constraints.

## Concepts and terms

**[1] GADT.** A datatype whose constructors may return different instances of the type's parameters. Its index can express relationships between stored values and the type of a computation using them.

**[2] Local type equality.** Information justified by a particular constructor match. It refines the types available inside the matching branch but is not an unconditional equation for all branches.

**[3] Rigid and wobbly types.** Rigid types are fixed by suitable programmer-supplied annotations; wobbly types retain uncertainty from inference. The distinction controls use of GADT equalities rather than blindly refining every inferred type.


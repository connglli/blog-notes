# MLF: Raising ML to the power of System F

**Summary by:** GPT 6 Astra

**Author:** Didier Le Botlan and Didier Rémy

**Source:** ICFP 2003; SIGPLAN Most Influential ICFP Paper Award 2013.

**Link:** https://doi.org/10.1145/944705.944709

**Code:** [MLF prototype, 2011 version](https://gallium.inria.fr/~remy/mlf/proto/)

## Key insight

Inferring first-class polymorphism need not force an early choice about how far to instantiate a polymorphic value. Richer types can retain that choice as a constraint until its use determines the appropriate instance.

## Basic idea

MLF combines ML-style inference [1] with first-class polymorphism [2]. Bounded quantification [3] records relationships between an unknown type and a polymorphic type instead of immediately choosing a monomorphic instance. Programmer annotations identify the higher-order polymorphism that inference cannot reconstruct automatically. Each typable expression with its given annotations has a principal type [4]; this is not unrestricted annotation-free type inference for System F.

## Illustrative example

**Setup.** Let `same` be the polymorphic identity function with type `Id = forall a. a -> a`. Let `pick_first` take two values of the same type and return the first. Consider the partial application `pick_first same`.

One use supplies an integer-to-integer function as the second argument. Another supplies a function that is itself polymorphic at every argument type. Both are sensible uses of the original identity value, but committing too early to one interpretation can lose the other.

**Delay instantiation.** A useful inferred type is conceptually `forall (b >= Id). b -> b`. The bound means that `b` may be an allowed instance of `Id`; it does not mean a numerical ordering or ordinary object-oriented subtyping.

In the first context choose `b = Int -> Int`. The result can be applied to 11 and returns 11. In the second context retain `b = Id`; the returned value can subsequently be instantiated at an integer type and at a Boolean type.

**Annotation boundary.** Now write a function that receives `f` and uses it both on an integer and on a Boolean. Its parameter must be explicitly annotated as polymorphic, for example with `Id`. MLF uses this given information to infer the surrounding program rather than trying to guess every higher-rank annotation.

Flexible bounds permit later instantiation; rigid bounds record explicitly fixed polymorphic information. Unification and the instance relation operate on this richer type language to keep the unresolved alternatives representable.

The example follows the paper's central inference problem but uses its own names and uses. It does not prescribe syntax for a current Haskell or OCaml compiler.

## Concepts and terms

**[1] ML-style inference.** Inferring ordinary polymorphic types, generalizing suitable bindings, and implicitly instantiating a polymorphic binding at its uses.

**[2] First-class polymorphism.** Allowing polymorphic values to occur as arguments and within other types, rather than limiting polymorphism to outermost let-bound type schemes.

**[3] Bounded quantification.** Quantifying a type variable together with an instantiation constraint. MLF distinguishes flexible bounds, which can be further instantiated, from rigid bounds preserving explicit polymorphic information.

**[4] Principal type.** A type representing all permitted inferred instances of an expression. In MLF the theorem is relative to the annotations supplied in that expression; changing annotations can change the principal type.


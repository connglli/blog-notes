# Scrap more boilerplate: Reflection, zips, and generalised casts

**Summary by:** GPT 6 Astra

**Author:** Ralf Lämmel and Simon Peyton Jones

**Source:** ICFP 2004; SIGPLAN Most Influential ICFP Paper Award 2014.

**Link:** https://doi.org/10.1145/1016850.1016883

**Code:** [SYB library source and documentation](https://hackage.haskell.org/package/syb)

## Key insight

A generic traversal becomes a more complete programming interface when it can inspect constructors, rebuild values, and align children of multiple values. Type-safe specialization handles the cases whose intended behavior differs from their raw structural representation.

## Basic idea

The paper extends the Scrap Your Boilerplate approach to datatype-generic programming [1] with reflection [2] and generic construction [3]. Constructor information supports serialization and deserialization, while generic zips [4] combine corresponding children of two structures. Generalized casts [5] let a generic function acquire type-specific behavior without abandoning static typing. The interface relies on datatype instances exposing structure, rather than one handwritten traversal for every application.

## Illustrative example

**Datatype.** Consider values of a Haskell datatype `data Parcel = Parcel Int String`, such as `Parcel 12 "tools"`. We want a generic serializer, parser, and equality check for this representation.

**Inspect and serialize.** Reflection reports the outer constructor `Parcel`. A generic fold visits its immediate children, first 12 and then `"tools"`. Recursively serializing these fields produces a constructor-based representation. Give strings a specialized serializer so the second field is written as a quoted string rather than as a list of individual character constructors.

**Construct.** Parsing starts with the expected result type and a constructor descriptor for `Parcel`. Generic unfolding applies that constructor to values produced by parsers for the required child types. It requests an integer parser and then a string parser, finally building `Parcel 12 "tools"`. A descriptor or field sequence incompatible with the expected type must fail rather than fabricate an ill-typed value.

**Zip and compare.** To compare this parcel with `Parcel 12 "seeds"`, first check the constructors. They match, so pair corresponding children and recursively compare them. The integer comparison succeeds and the string comparison fails, making the overall result false. Constructor mismatch would stop structural comparison before trying to pair incompatible fields.

A type-safe generalized cast can select the string-specific operation only when the encountered type agrees with the specialization's type. It returns failure when the types differ; it is not an unchecked reinterpretation of memory.

## Concepts and terms

**[1] Datatype-generic programming.** Defining an algorithm over structural operations supplied by datatype instances. The same algorithm can traverse many user-defined datatypes.

**[2] Reflection.** Obtaining datatype and constructor descriptions from the generic interface. It exposes constructor identity and available structure without requiring application-specific pattern matches.

**[3] Generic construction.** Building a value from a constructor description and a polymorphic source of correctly typed fields. The paper's `gunfold` operation complements the generic fold used to inspect existing values.

**[4] Generic zip.** Aligning corresponding immediate subterms of structures for a combined operation. Structural agreement must be checked before a generic equality or similar operation can safely compare children.

**[5] Generalized cast.** A checked type-equality operation that can transport a value wrapped in a type constructor when its parameter types agree. This supports type-specific generic-function extensions while retaining typed results.


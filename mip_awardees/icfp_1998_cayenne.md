# Cayenne: A language with dependent types

**Summary by:** GPT 6 Astra

**Author:** Lennart Augustsson

**Source:** ICFP 1998; SIGPLAN Most Influential ICFP Paper Award 2008.

**Link:** https://doi.org/10.1145/289423.289451

**Code:** [Cayenne implementation, preserved mirror](https://github.com/csgordon/cayenne)

## Key insight

If types are computed by the same expression language as values, an interface can describe results whose types depend on inputs. Records containing types and dependent fields also provide module-like abstraction without a separate module calculus.

## Basic idea

Cayenne combines dependent function types [1], dependent records [2], and first-class type expressions [3] in a Haskell-like language. Type checking reduces type expressions to establish the equalities needed at applications and field uses. Because those expressions can compute generally, type equality is undecidable [4]; the implementation bounds its reduction effort and can report that it cannot decide. Unrestricted recursion also means the language is not, without additional checks, a sound total proof language.

## Illustrative example

**Interface.** Define a type-valued function `PayloadType(flag)` that returns `String` when `flag` is true and `Int` when it is false. A packet record contains a Boolean field `textual` and a field `payload` whose type is `PayloadType(textual)`.

This is a description of a Cayenne-style dependent interface, not executable syntax for an ordinary Haskell record.

**Checking values.** A packet with `textual = false` and `payload = 7` is compatible: reducing `PayloadType(false)` yields `Int`. A packet with `textual = true` and `payload = "ready"` is compatible because its payload type reduces to `String`. Pairing true with the integer 7 fails the required type equality.

A constructor function can expose the dependent type `(flag: Bool) -> PayloadType(flag) -> Packet`. Supplying false specializes its next argument to an integer. Supplying true specializes that argument to a string. The dependency is on an ordinary Boolean value, not just a type parameter.

**Implementation.** The checker tracks earlier record fields while checking later fields. At an application, it substitutes the actual argument into the dependent result type, then compares the resulting type expressions by its reduction and equivalence procedure. An interface record could also contain an abstract type field and operations whose input and output types refer to that field, providing a module-like package.

**Limits.** If the flag or a type-valued helper requires unbounded computation to normalize, checking may exhaust its reduction limit. That result is different from exhibiting an incompatible integer/string type. Likewise, assigning a logical proposition a type does not prove it when an alleged proof may diverge.

## Concepts and terms

**[1] Dependent function type.** A function type whose result type can mention its argument value. Application substitutes that value into the result type.

**[2] Dependent record.** A record whose later field types may refer to earlier fields, including fields that themselves contain types.

**[3] First-class type expression.** A type computed using ordinary expression constructs. Cayenne uses a hierarchy of universes to classify types rather than identifying every universe with itself.

**[4] Undecidable type equality.** No algorithm can always decide the language's full equality relation and terminate. A bounded checker can return an inconclusive result when its allowed reduction effort is exceeded.


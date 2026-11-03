# A language with distributed scope

**Summary by:** GPT 6 Astra

**Author:** Luca Cardelli

**Source:** POPL 1995; SIGPLAN Most Influential POPL Paper Award 2005.

**Link:** https://doi.org/10.1145/199448.199516

**Code:** [Obliq in the Modula-3 distribution](https://github.com/modula3/cm3/tree/master/m3-obliq)

## Key insight

Moving a computation to another machine need not change the meanings of its free variables. Obliq transmits closures with their existing bindings, while mutable locations remain at their original sites.

## Basic idea

Obliq extends lexical scope [1] across a network: a remotely executed closure [2] still refers to the environment where it was created. Values are copied on transmission, but embedded mutable locations become network references [3]. Object operations can therefore affect remote state without silently duplicating it. A compute server can pass its own local resources as explicit arguments, keeping them distinct from the resources captured by the incoming computation.

## Illustrative example

**Setup.** Site North owns a mutable object `counter` whose `value` field is 7. It constructs a procedure that takes an increment, updates `counter.value`, and returns the resulting number. The procedure's environment binds `counter` to North's object.

Site South has another object also named `counter`, with value 100. South accepts the procedure and calls it with argument 3. These names do not identify the same object.

**Transmission.** A miniature implementation sends the procedure's code and its free-variable table. The table does not contain a fresh copy of North's mutable counter. It contains a reference identifying the object at North. South evaluates the incoming procedure with this captured table, not with South's top-level variable environment.

The update consequently changes North's value from 7 to 10. South's value remains 100, and the call returns the ordinary integer 10. If South needs the computation to use a South-owned object, the procedure must accept that object as an argument and South must supply it.

**Resource consequences.** The reference retains a live dependency on North. Network failure can prevent the read or update from completing; lexical scope is not a network-availability guarantee. Passing a closed procedure that captures no remote mutable locations removes this particular dependency.

The example assumes no competing updates. The language also supports concurrency, but preserving bindings does not by itself make a read-modify-write sequence atomic. An object that requires serialized access must use the language's synchronization discipline.

## Concepts and terms

**[1] Lexical scope.** An identifier's binding is determined by the surrounding program text where the expression is defined, rather than by the environment of its caller. Distributed lexical scope preserves this rule when execution changes sites.

**[2] Closure.** Procedure code paired with bindings for its free identifiers. Obliq transmits only the values needed by the closure, rather than an entire evaluation stack.

**[3] Network reference.** A reference to mutable state owned by another address space. Basic immutable values can be copied, but transmission of a value containing locations retains access to those locations. Object cloning is an explicit operation, not an implicit consequence of sending the object.


# From System F to typed assembly language

**Summary by:** GPT 6 Astra

**Author:** Greg Morrisett, David Walker, Karl Crary, and Neal Glew

**Source:** POPL 1998; SIGPLAN Most Influential POPL Paper Award 2008.

**Link:** https://doi.org/10.1145/268946.268954

**Documentation:** [TALx86 compiler project](https://www.cs.cornell.edu/talc/)

## Key insight

Types can describe registers, heap objects, and code entry conditions, so compilation need not discard the evidence that a program uses values safely. Existential types hide closure environments without hiding the relationship between the environment and its code.

## Basic idea

The compiler translates System F [1] through continuation-passing style [2], closure conversion [3], explicit allocation, and typed assembly language [4]. Each stage preserves typing. Closures package code with their captured data using an existential type [5], allowing functions with different private environments to share an external type. The assembly checker verifies instruction operands and control transfers independently of the compiler; its safety guarantee does not assert that the compiler preserved the source program's full meaning.

## Illustrative example

**Source.** A function captures an integer increment and returns another function that adds it to an argument. Apply the returned function to 8 with increment 5. The expected result is 13.

**Control and closure conversion.** In continuation-passing form, the addition function receives both its integer argument and a continuation that accepts the result. Its captured increment is moved into a one-field environment. The code becomes closed: it takes the environment explicitly, reads the increment, computes the sum, and invokes the continuation.

Package the code pointer and environment together. Conceptually, their type is `exists E. (E, code(E, int, continuation(int)))`. Here the concrete `E` is a one-integer tuple. A different function could capture two integers and still expose the same function interface.

**Allocation.** Allocate storage for the environment and initialize its field with 5. The intermediate types distinguish an allocated but uninitialized field from an initialized integer field, preventing a load before initialization.

**Assembly checking.** At a call, unpack the closure to obtain one fresh abstract environment type `E`. Load its environment into the register required by the code block and place 8 and the result continuation in their argument registers. The checker accepts the jump only if the current register types satisfy the destination's entry requirements.

The code reads 5 from its environment, adds 8, and passes 13 to the continuation. Substituting an unrelated tuple for the environment is rejected because the unpacked abstract type must agree with the code's argument type. Types guide static checking and can be erased before execution.

## Concepts and terms

**[1] System F.** A typed lambda calculus with explicit abstraction and application over types. The source variant also has integers, tuples, and recursion.

**[2] Continuation-passing style.** Functions receive an explicit representation of what to do with their result. Calls and returns become transfers to functions or code blocks.

**[3] Closure conversion.** Rewriting a function with free variables into closed code plus an explicit environment containing those variables' values.

**[4] Typed assembly language.** Assembly instructions equipped with types for heap contents, registers, and code labels. A code label specifies the register types required on entry.

**[5] Existential type.** A package that conceals a concrete type while exposing operations whose types consistently refer to it. Unpacking introduces a fresh abstract type; consumers cannot assume it is an arbitrary concrete representation.


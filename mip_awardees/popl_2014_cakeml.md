# CakeML: A verified implementation of ML

**Summary by:** GPT 6 Astra

**Author:** Ramana Kumar, Magnus O. Myreen, Michael Norrish, and Scott Owens

**Source:** POPL 2014; SIGPLAN Most Influential POPL Paper Award 2024.

**Link:** https://doi.org/10.1145/2535838.2535841

**Code:** [CakeML implementation and proofs](https://github.com/CakeML/cakeml)

## Key insight

Verifying a compiler's logical algorithm is not enough if the compiler executable is produced by an untrusted translation. CakeML bootstraps its compiler inside the proof system and connects an interactive implementation to both language and machine semantics.

## Basic idea

CakeML defines a subset of Standard ML with formal operational semantics [1] and an interactive read-eval-print loop, or REPL [2]. Verified components cover parsing, type inference, compilation, and runtime support in HOL4 [3]. Proof-producing translation and verified bootstrapping [4] connect the logical implementation to x86-64 machine code. The resulting theorem accounts for successful execution, divergence, and an explicit out-of-memory outcome under the stated machine-model assumptions.

## Illustrative example

**Input.** Feed the REPL two declarations, first defining a function that adds 4 and then applying it to 9:

```sml
fun add_four x = x + 4;
val result = add_four 9;
```

The first declaration extends the environment with a function. The second must use that same binding and establish `result = 13`. This persistent environment makes the example more than compiling two unrelated closed expressions.

**Front end.** Lexing and parsing recover the declarations from characters. Type inference accepts the integer addition and application. The semantic REPL specifies what binding and printed result are permitted; the implementation must agree with that specification, not merely generate some well-formed assembly.

**Compilation and execution.** The implementation compiles an accepted declaration to bytecode, translates the bytecode to x86-64 code, and executes it while preserving the REPL's state. Runtime representation changes, allocation, arbitrary-precision integer operations, and garbage collection are included in the relevant correctness connections.

For this input, a successful run cannot report 14 as the result of the application. If available memory is insufficient, the theorem permits the specified out-of-memory termination rather than promising an answer on every finite machine.

**Bootstrapping.** The compiler is also a program. Translate its logical definition into CakeML with a proof of correspondence, then evaluate the verified compiler on that code inside HOL4. The generated machine-code compiler inherits the established correspondence. Running an unrelated compiler on a source file and assuming its output correct would not provide this link.

The theorem is stated for a formal x86-64 machine with suitable accessible memory and input behavior. Hardware correctness and adequacy of that model remain assumptions, rather than consequences of compiler bootstrapping.

## Concepts and terms

**[1] Operational semantics.** Rules specifying how programs evaluate and what outcomes they may produce, including exceptional or nonterminating behavior.

**[2] REPL.** An interactive loop that reads a declaration, checks and executes it, prints a result, and carries its environment into the next iteration.

**[3] HOL4.** The higher-order-logic proof assistant used for the definitions and machine-checked proofs. Its proof-checking kernel is part of the trusted foundation.

**[4] Verified bootstrapping.** Producing the compiler's executable through a proved translation of the compiler implementation and applying compiler correctness to that translation. It connects a theorem about a logical function to a concrete executable.


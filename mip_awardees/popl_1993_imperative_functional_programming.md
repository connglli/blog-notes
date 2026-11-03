# Imperative functional programming

**Summary by:** GPT 6 Astra

**Author:** Simon L. Peyton Jones and Philip Wadler

**Source:** POPL 1993; SIGPLAN Most Influential POPL Paper Award 2003.

**Link:** https://doi.org/10.1145/158511.158524

**Code:** [Glasgow Haskell Compiler project](https://github.com/ghc/ghc)

## Key insight

An input/output operation can be a value describing an action, rather than an effect caused by evaluating an ordinary expression. Explicit action composition specifies execution order without fixing the evaluation order of pure expressions.

## Basic idea

A lazy language [1] cannot safely let ordinary expression evaluation perform arbitrary input/output, because evaluation order and sharing would become observable. The paper represents an action returning a value of type `a` by the abstract type `IO a` [2]. A sequencing operation, bind [3], connects one action's result to the construction of the next action. Internally, an action can be represented as a function passing a state token [4] through the computation, while the public interface prevents programs from inspecting or duplicating that token.

## Illustrative example

**Setup.** We want to read one character and print it twice. In modern Haskell notation, the following is a small program using the paper's action-composition idea:

```haskell
main :: IO ()
main =
  getChar >>= \letter ->
  putChar letter >>= \_ ->
  putChar letter
```

The expression `putChar letter` denotes an action. Merely giving it a name does not print anything. Executing `main` performs the read, passes its returned character to the continuation, and performs the two writes in order.

**Representation.** For a miniature interpreter, represent a world as an input string and an output string. A read transforms `("QZ", "")` into the result `'Q'` and world `("Z", "")`. The first write receives that world and produces `("Z", "Q")`; the second receives the latter world and produces `("Z", "QQ")`. Bind always passes the returned world to the next action, never the original world.

This model explains the ordering; it does not suggest copying the physical world. A compiler can represent the state token without a material runtime object and turn the dependencies into ordered machine operations.

**Sharing.** Naming the write action once and sequencing it twice still performs two writes. Conversely, sharing the pure value `letter` does not repeat the read. The distinction is between sharing an action value and executing that action.

## Concepts and terms

**[1] Lazy evaluation.** An expression is evaluated only when its value is needed, and a shared expression's result can be reused. This leaves expression evaluation order unsuitable as an implicit order for external effects.

**[2] IO action.** An abstract value which, when executed by the runtime, can interact with the outside world and return a result. An `IO a` is not itself an `a`; the interface does not expose an unrestricted pure function that executes it.

**[3] Bind.** For actions `m` and a function `k`, `m >>= k` performs `m`, obtains its result `x`, and performs `k x`. Together with a result-only action, this supplies the monadic composition interface.

**[4] State token.** An implementation-level dependency representing the world before or after an action. Hiding its representation is what prevents a source program from branching the world-passing implementation into inconsistent executions.


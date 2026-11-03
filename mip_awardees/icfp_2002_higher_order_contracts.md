# Contracts for higher-order functions

**Summary by:** GPT 6 Astra

**Author:** Robert Bruce Findler and Matthias Felleisen

**Source:** ICFP 2002; SIGPLAN Most Influential ICFP Paper Award 2012.

**Link:** https://doi.org/10.1145/581478.581484

**Documentation:** [Racket contract system](https://docs.racket-lang.org/guide/contracts.html)

## Key insight

A function's behavioral contract cannot generally be checked when the function is passed as a value. Wrap it so that obligations are checked when it is called, and track which party is responsible at each boundary.

## Basic idea

A contract [1] can be a predicate on ordinary values or a function contract [2] combining domain and range contracts. Monitoring a function creates a wrapper [3] that checks inputs before calling it and outputs after it returns. Higher-order arguments and results receive further wrappers, so checks follow functions even when they escape their original caller. Blame polarity [4] reverses in an argument position, distinguishing a provider's broken promise from a client's misuse.

## Illustrative example

**Boundary.** A library exports `apply_twice`. It accepts a callback from nonnegative integers to nonnegative integers, accepts a nonnegative starting value, and returns a nonnegative integer. The library calls the callback twice, threading the result of the first call into the second.

A client supplies a callback that subtracts 1. Passing that function across the boundary does not immediately fail: deciding its behavior for every possible argument is not the monitor's job.

**Delayed check.** The client calls the library with starting value 0. The library invokes the wrapped callback on 0. Its input satisfies the nonnegative contract, but the callback returns -1. The wrapper reports a failure and blames the client, which supplied the callback and promised its nonnegative result.

This is not a failure of the library's overall result promise: the callback boundary identifies the violated obligation before the library finishes.

**Opposite misuse.** Suppose the client supplies a callback that returns its nonnegative input unchanged, but a faulty library calls it with -2. The callback's argument wrapper fails before invoking the callback and blames the library for violating the callback's input requirement.

A wrapper implementation can express this by recursively monitoring a function's argument with the two parties' blame roles exchanged, invoking the original function, and monitoring its result with the original roles. The nested callback position is exactly where the exchange matters.

**Lifetime.** If the library saves the callback and invokes it later, it must save the wrapped function. Restricting checking to syntactically visible calls inside `apply_twice` would miss delayed use.

## Concepts and terms

**[1] Contract.** A runtime-enforced behavioral requirement. A flat contract checks a concrete value with a predicate; it need not describe the function's complete intended algorithm.

**[2] Function contract.** A domain contract and a range contract. The domain specifies acceptable inputs, while the range specifies promised outputs.

**[3] Wrapper.** A function replacing a monitored function at a boundary. It performs checks at actual applications and recursively wraps higher-order values instead of trying to inspect all their possible future behavior.

**[4] Blame polarity.** The assignment of obligations to the provider and user of a value. Inputs reverse their roles, while outputs preserve them; this rule composes through nested function contracts.


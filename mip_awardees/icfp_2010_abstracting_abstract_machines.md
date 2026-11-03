# Abstracting abstract machines

**Summary by:** GPT 6 Astra

**Author:** David Van Horn and Matthew Might

**Source:** ICFP 2010; SIGPLAN Most Influential ICFP Paper Award 2020.

**Link:** https://doi.org/10.1145/1863543.1863553

## Key insight

A program analysis can be derived from an interpreter by redirecting recursive runtime structure through a store and then bounding that store. Address collisions become explicit approximation rather than an unrelated set of analysis rules.

## Basic idea

An abstract machine [1] represents execution with an expression, environment, store, and continuation. Store-allocated continuations [2] remove the unbounded recursive stack structure from individual states. Bounding addresses [3] forces multiple concrete objects to share abstract locations, whose contents are joined into sets [4]. Exploring every permitted lookup choice yields a finite-state sound approximation when the other value domains are also finite.

## Illustrative example

**Concrete execution.** A Boolean identity function `echo(x) = x` is called first on false and then on true; the program returns the second result. A concrete machine allocates separate locations for the two invocations' bindings of `x`. Looking up the second binding yields only true.

**Abstract allocation.** Choose a deliberately coarse allocator that always maps this parameter to one abstract address `arg_echo`, independent of calling context. The first call adds false to that address; the second adds true. Its abstract contents become `{false, true}`.

Lookup during the second call must explore both possibilities. The analysis can therefore include false among possible results even though the concrete second call returns true. This is a false positive caused by the chosen address abstraction, not an unsound omission.

**Continuations.** The first call must return to the code that starts the second; the second returns to the program's caller. Represent each continuation frame in the store, with a pointer to the next frame. Allocate those frames from a finite abstract address set too. Reusing a continuation address joins possible frames and can introduce additional return-flow choices.

**Exploration.** Start with the abstract initial state, repeatedly compute successor states, and retain a visited set until no new state remains. Updating a reused address adds information rather than overwriting an older possibility. Finer addresses, such as ones incorporating bounded call history, distinguish more executions but enlarge the state space.

If the language includes unbounded integers, bounding addresses alone is insufficient: integer values also need a finite abstraction. The paper's machine-derived method identifies these approximation choices instead of hiding them in an implementation.

## Concepts and terms

**[1] Abstract machine.** A step-by-step operational model of program evaluation. Its environment maps variables to locations, its store maps locations to runtime objects, and its continuation records remaining work.

**[2] Store-allocated continuation.** A continuation frame whose successor is an address rather than a recursively embedded continuation. This makes the potentially unbounded chain pass through the store.

**[3] Bounded address abstraction.** Mapping arbitrarily many concrete allocation events to finitely many abstract addresses. The allocator controls how much context the analysis distinguishes.

**[4] Join.** Combining possible contents at a shared abstract address. A lookup nondeterministically considers each member, preserving all represented concrete behaviors.


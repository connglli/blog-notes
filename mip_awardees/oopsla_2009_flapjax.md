# Flapjax: A Programming Language for Ajax Applications

**Summary by:** GPT 6 Astra

**Author:** Leo A. Meyerovich, Arjun Guha, Jacob Baskin, Gregory H. Cooper, Michael Greenberg, Aleks Bromfield, Shriram Krishnamurthi

**Source:** OOPSLA 2009; SIGPLAN Most Influential OOPSLA Paper Award, 2019

**Link:** https://dl.acm.org/citation.cfm?id=1640091

**Documentation:** [Flapjax](https://www.flapjax-lang.org/)

## Key insight

Describe dependencies between changing values directly, instead of distributing the same update logic across many event callbacks.

## Basic idea

Flapjax represents discrete occurrences as event streams [1] and values that vary over time as behaviors [2]. Combinators build a dataflow graph [3] whose updates propagate to dependent computations and user-interface elements. Topological scheduling avoids glitches [4] within the supported reactive graph. Browser callbacks still exist underneath the library; the abstraction organizes their effects rather than eliminating external events.

## Illustrative example

**Inputs.** A shop page has a quantity selector initially set to two and an "add item" button. Represent button clicks as an event stream. Folding those clicks with addition produces a quantity behavior; a reset event could instead set its next value explicitly. Let the unit price be five.

**Dependencies.** Define subtotal as five times quantity, discount as one when quantity is at least three and zero otherwise, and total as subtotal minus discount. Bind total to the displayed text. Initially the three derived values are ten, zero, and ten.

**Update.** One click changes quantity to three. Both subtotal and discount depend on that change, giving fifteen and one. Total should become fourteen. If total runs after the new subtotal but before the new discount, it momentarily becomes fifteen, an inconsistent mixture of old and new data.

**Scheduling.** Process the source change, then its direct dependents, then total, respecting the graph's dependency order. The display receives fourteen without that intermediate inconsistent result. A cycle in immediate dependencies would not admit such an order; feedback needs a delay that separates updates in time. Independent network replies are separate external events, so local glitch freedom does not automatically impose a transaction across the browser and server or resolve out-of-order replies.

## Concepts and terms

**[1] Event stream.** A sequence of discrete occurrences carrying values, such as clicks or received messages.

**[2] Behavior.** A reactive value with a current value at every relevant time, including an initial value before events occur.

**[3] Dataflow graph.** Nodes compute reactive values; edges indicate that one node's result depends on another.

**[4] Glitch.** A transient inconsistent result produced by combining updates from different stages of one logical change.

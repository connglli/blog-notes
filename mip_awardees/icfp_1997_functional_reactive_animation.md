# Functional reactive animation

**Summary by:** GPT 6 Astra

**Author:** Conal Elliott and Paul Hudak

**Source:** ICFP 1997; SIGPLAN Most Influential ICFP Paper Award 2007.

**Link:** https://doi.org/10.1145/258948.258973

**Code:** [Original Fran implementations](https://github.com/conal/Fran)

## Key insight

An animation can be described by values that vary over continuous time, with explicit events that change how those values are defined. This separates the animation's meaning from the schedule used to draw frames.

## Basic idea

Fran provides behaviors [1] for time-varying values and events [2] for discrete occurrences carrying values. Ordinary functions are lifted [3] to combine behaviors pointwise, while switching [4] changes the governing behavior when an event occurs. The paper gives these abstractions a denotational semantics and uses partial information about event times to guide event detection. A renderer samples this description for display, but the display's frame rate is not the definition of the behavior.

## Illustrative example

**Motion.** A marker starts at horizontal position zero and moves two units per second. Define its position behavior mathematically by `position(t) = 2*t` for nonnegative time. Its vertical position is a constant zero behavior.

Lifting the pair constructor combines the coordinates into one position behavior. Lifting a drawing function over that position and a constant marker image produces a time-varying image. At times 0, 1.5, and 2.5 seconds, the marker's horizontal positions are 0, 3, and 5.

**Event and switch.** Define an event for the first time the position reaches 6, carrying the replacement behavior that remains constantly at 6. Switching the original position at this event gives `2*t` before time 3 and 6 thereafter.

The time of the event is part of the meaning. A display that draws only at 2.8 and 3.2 seconds shows positions 5.6 and 6; it need not pretend that the stop happened at the later frame.

**Detection.** For this linear behavior, an interval estimate over times `[2, 2.5]` bounds the position by `[4, 5]`, so the threshold cannot be reached there. Over `[2.5, 3.5]`, the position range `[5, 7]` requires refinement to locate the occurrence. Here algebra determines the exact time 3; more general behaviors require the detection machinery's approximation discipline.

A practical renderer still has numerical and scheduling limits. A continuous-time denotation does not claim that a finite computer draws infinitely many frames or computes every real-valued event time exactly.

## Concepts and terms

**[1] Behavior.** A value whose meaning varies with time, conceptually a function from time to values. A constant is a behavior with the same value at every time.

**[2] Event.** A discrete occurrence with an occurrence time and associated information. The paper's semantic treatment includes partial information about when an event may occur.

**[3] Lifting.** Applying an ordinary function to the values of its input behaviors at each time. It supports composition without manually coordinating separate update loops.

**[4] Switching.** Following one behavior until an event supplies another behavior to use. This combines continuously varying quantities with discrete reactive changes.


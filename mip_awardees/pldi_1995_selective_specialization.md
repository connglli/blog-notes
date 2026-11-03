# Selective Specialization for Object-Oriented Languages

**Summary by:** GPT 6 Astra

**Author:** Jeffrey Dean, Craig Chambers, David Grove

**Source:** PLDI 1995; SIGPLAN Most Influential PLDI Paper Award, 2005

**Link:** https://doi.org/10.1145/207110.207119

## Key insight

Specialize methods where better argument-class information removes expensive dispatches, rather than generating a separate method for every possible class combination.

## Basic idea

The compiler uses profiles to select profitable specializations [1] that turn dynamic dispatch [2] into known calls. A specialization constrains a set of possible classes for each argument, including arguments other than the receiver. Several classes can share a version when class-hierarchy analysis [3] shows the required call target is unchanged. A general version handles remaining cases, and runtime selection must respect each version's assumptions.

## Illustrative example

**Hot call.** A method `render(items, painter)` loops over many items and invokes `painter.paint(item)`. The `painter` argument is not the receiver of `render`. Profiles show that this loop usually receives either `BluePainter` or `DarkBluePainter`, both inheriting the same `paint` method, while occasional calls use a different `PatternPainter` implementation.

**Goal-directed choice.** The costly operation is the repeated call to `paint`. Work backward from that call: knowing that `painter` belongs to the first two classes uniquely selects their shared implementation. Compile one `render` version with the class-set constraint `{BluePainter, DarkBluePainter}`, rather than separate versions for both classes.

**Generated behavior.** Select this specialized version once at the outer call. Its loop can call the known `paint` implementation directly and may inline it. Route `PatternPainter` to the general version, which still performs dynamic lookup. If the loop processes 100 items, this illustrative transformation can replace 100 method lookups with one version-selection decision, subject to the actual generated code and inlining choices.

**Safety and cost.** The profile motivates paying for an extra version; it does not prove that other classes cannot occur. A class that overrides `paint` must not enter the specialized version under an overly broad test. An infrequently used specialization may add code and compilation cost without worthwhile runtime benefit, which is why exhaustive cloning is avoided.

## Concepts and terms

**[1] Specialization.** A method version optimized under stronger facts about its arguments, with those facts required at entry.

**[2] Dynamic dispatch.** Selecting a method implementation from runtime argument classes rather than a statically fixed target.

**[3] Class-hierarchy analysis.** Reasoning from classes and method definitions to determine which implementations can be selected; inherited methods can let several classes share one target.

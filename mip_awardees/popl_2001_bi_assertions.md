# BI as an assertion language for mutable data structures

**Summary by:** GPT 6 Astra

**Author:** Samin Ishtiaq and Peter W. O'Hearn

**Source:** POPL 2001; SIGPLAN Most Influential POPL Paper Award 2011.

**Link:** https://doi.org/10.1145/360204.375719

## Key insight

A heap assertion can state that two properties hold of disjoint pieces of memory. This makes the memory a command does not touch available as a reusable frame, rather than an additional proof obligation for each operation.

## Basic idea

The paper interprets the logic of bunched implications, BI [1], over mutable heaps. Its separating conjunction [2] combines descriptions of disjoint memory, unlike ordinary conjunction, which speaks about the same state. A frame rule [3] extends a command's local specification to unrelated heap contents, subject to a variable-modification condition. The classical heap model describes exact allocated memory and supports both allocation and disposal; separating implication [4] also expresses obligations about extending a heap.

## Illustrative example

**Setup.** Let `a` and `b` point to distinct two-field cells. The assertion `a -> (4, nil) * b -> (9, nil)` means that the heap splits into one cell at `a` containing `(4, nil)` and one at `b` containing `(9, nil)`.

The command updates the first field of `a` to 6. Its small specification is: starting from `a -> (4, nil)`, executing `a.1 := 6` ends with `a -> (6, nil)`.

**Framing.** Take `R = b -> (9, nil)`. The command changes no variable mentioned by `R` and its heap access is confined to the cell described by its precondition. The frame rule therefore yields the larger postcondition `a -> (6, nil) * b -> (9, nil)`.

If `a` and `b` alias, the initial separating conjunction is false. Replacing it with ordinary conjunction would not establish disjointness and would not justify preserving `b`'s old contents.

**Disposal and extension.** Disposing of `a` consumes that cell, leaving exactly `b -> (9, nil)`. The stack variable `a` may still hold the old address, but dereferencing it is unsafe because no allocated cell at that address is owned.

A separating implication such as `(a -> (6, nil)) -* Q` holds of a heap when adding any disjoint cell satisfying its left side produces a heap satisfying `Q`. For example, with `Q = a -> (6, nil) * b -> (9, nil)`, the remaining `b` cell satisfies this implication. It describes what an appropriate disjoint extension would establish, without asserting that the extension already exists.

## Concepts and terms

**[1] BI.** A logic combining ordinary connectives with resource-sensitive ones. In this paper the resource is allocated heap memory; assertions also depend on a stack mapping variables to values.

**[2] Separating conjunction.** `P * Q` holds when the current heap splits into disjoint subheaps satisfying `P` and `Q`. A points-to assertion describes an allocated cell and its contents.

**[3] Frame rule.** From a safe specification `{P} C {Q}`, infer `{P * R} C {Q * R}` when `C` does not modify free variables of `R`. The command preserves the separately owned heap.

**[4] Separating implication.** `P -* Q` universally quantifies over disjoint heap extensions satisfying `P` and requires their combination with the current heap to satisfy `Q`.


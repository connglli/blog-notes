# On the criteria to be used in decomposing systems into modules

**Summary by:** GPT 6 Astra

**Author:** David L. Parnas

**Source:** Communications of the ACM 15(12), 1972; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/361598.361623

## Key insight

Choose module boundaries around design decisions likely to change, not merely around successive processing steps. A useful interface hides the decision so that changing it need not change its clients.

## Basic idea

Parnas compares a processing-step decomposition [1] with an information-hiding decomposition [2] for a small indexing program. Both can compute the same result, but they expose different dependencies between modules. In the information-hiding design, each module owns a representation or algorithmic decision and offers an abstract interface [3] for the operations others need. This improves independent development and change isolation only when those interfaces avoid revealing the supposedly hidden decisions.

## Illustrative example

**Task.** Index the two titles `quiet river` and `bright moon` by listing each cyclic rotation of its words, then sorting those rotations. The four outputs in order are `bright moon`, `moon bright`, `quiet river`, and `river quiet`.

**Processing-step design.** An input module packs characters into an array, a rotation module builds arrays of offsets into it, a sorting module rearranges those offsets, and an output module follows them. The modules correspond neatly to execution stages. However, all understand the packed-character and offset representations. Changing the storage format can require changing every stage even though the desired index is unchanged.

**Hide decisions.** A line-storage module exposes operations to obtain a line's word count and a particular word, while keeping character layout private. A rotation module exposes the number of rotations and the word at position `j` of rotation `r`. It may store complete rotated strings or represent a rotation by a pair `(line, starting-word)`; clients cannot distinguish these choices through the interface.

An ordering module exposes the rotation identifier at sorted position `k`. It can sort eagerly, maintain an ordered structure as lines arrive, or compute enough ordering on demand. Output asks this module for rotation identifiers and the rotation module for words. Its job does not require inspecting the ordering representation.

**Change one decision.** Replace materialized rotated strings with `(line, starting-word)` descriptors. For a line of `n` words, the rotation module obtains word `j` through `(starting-word + j) mod n`. If its observable interface is preserved, sorting and printing do not change. Changing whether capital letters precede lowercase letters belongs to the ordering decision, not to character storage.

The decomposition is not a requirement to incur an expensive procedure call for every word access. Representation of modules during development and the final executable organization can differ. Nor does one fixed decomposition isolate every conceivable change: choosing which decisions to hide requires understanding likely variation.

## Concepts and terms

**[1] Processing-step decomposition.** Dividing a program according to the phases of its execution. It can leave multiple modules dependent on the same intermediate-data representation.

**[2] Information hiding.** Assigning a design decision to one module and preventing other modules from depending on its internal details. The hidden information is a changeable decision, not simply confidential data.

**[3] Abstract interface.** A set of operations whose externally specified behavior gives clients what they need without exposing the module's storage layout or implementation strategy. Preserving this behavior is the condition for independent replacement.

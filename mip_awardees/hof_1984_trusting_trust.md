# Reflections on Trusting Trust

**Summary by:** GPT 6 Astra

**Author:** Ken Thompson

**Source:** Communications of the ACM 27(8), 1984; SIGOPS Hall of Fame Award 2011

**Link:** https://doi.org/10.1145/358198.358210

## Key insight

Clean source does not imply a clean executable when the program translating that source is untrusted. A malicious self-hosting compiler can preserve its own hidden behavior across rebuilds even after the visible source is repaired.

## Basic idea

Thompson combines self-reproduction [1] with compiler bootstrapping [2] to construct a persistent source-to-binary mismatch. A modified compiler recognizes a target program and inserts unwanted behavior into its executable. It also recognizes the compiler's own source and inserts both recognition rules into the rebuilt compiler. After the attacker removes those rules from the distributed source, rebuilding with the compromised compiler still reproduces them. The trust boundary [3] therefore includes the tools that produce executable code, not only the source being reviewed.

## Illustrative example

**Define harmless source.** A small program `seal` prints `ACCEPT` only when an input record passes its stated checks. A compiler `forge` is written in its own input language and can compile its own source. Assume an ordinary, correctly functioning compiler initially exists for this language.

**Introduce two transformations.** A deliberately modified compiler source contains one rule that recognizes `seal` and adds an extra acceptance case, and another rule that recognizes `forge` and emits a compiler containing both rules. The second rule needs a representation of the inserted code as data, including the code that reproduces that representation. This is the self-reproduction step, not magic stored outside the executable.

**Bootstrap once.** Compile this modified source using the ordinary compiler. The result, `forge_bad`, contains the two transformations. The modified source can then be replaced by the clean compiler source. Compiling that clean source with `forge_bad` produces another compiler with the hidden rules because the second transformation triggers.

**Observe the mismatch.** A reviewer reads clean `seal` source and clean `forge` source. Rebuilding `forge` with the installed compiler preserves the hidden transformations, and using the rebuilt compiler on `seal` inserts the unwanted acceptance behavior again. Repeated self-compilation does not provide independent evidence of cleanliness: every generation descends through the same compromised translation step.

The example is a conceptual construction, not an exploit against a named modern compiler. Its pattern recognition must actually match the relevant source, and the generated code must remain valid. Source refactoring may defeat a particular simplistic trigger without disproving the general attack.

## Concepts and terms

**[1] Self-reproduction.** Producing a representation of one's own program as output, usually by arranging that code contains data describing the portion to be reproduced. Additional behavior can be carried along with the reproducing component.

**[2] Compiler bootstrapping.** Building a compiler with an existing compiler, including a compiler written in its own language. The resulting executable can retain behavior introduced by its predecessor rather than behavior visible in the nominal source alone.

**[3] Trust boundary.** The components whose correct behavior an assurance argument assumes. Here that includes the executable compiler and potentially assemblers, loaders, and lower execution machinery. The paper's construction shows a limit of source-only scrutiny, not that every independent checking technique is impossible.

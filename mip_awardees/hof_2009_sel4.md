# seL4: Formal Verification of an OS Kernel

**Summary by:** GPT 6 Astra

**Author:** Gerwin Klein, Kevin Elphinstone, Gernot Heiser, June Andronick, David Cock, Philip Derrin, Dhammika Elkaduwe, Kai Engelhardt, Rafal Kolanski, Michael Norrish, Thomas Sewell, Harvey Tuch, and Simon Winwood

**Source:** SOSP 2009; SIGOPS Hall of Fame Award 2019

**Link:** https://doi.org/10.1145/1629575.1629596

**Code:** [seL4 kernel](https://github.com/seL4/seL4) and [seL4 specifications and proofs](https://github.com/seL4/l4v)

## Key insight

A practical operating-system kernel can be verified by relating its C implementation to an abstract specification through an executable intermediate model. Designing the kernel and its proof together makes the necessary invariants manageable.

## Basic idea

seL4 is a capability-based microkernel [1] whose C implementation is proved to refine an abstract kernel specification [2]. An executable specification [3] connects abstract behavior to concrete data structures, while invariants [4] express the representation conditions required by low-level operations. Isabelle/HOL [5] checks the proofs of those relationships. The result establishes functional correctness of the covered C code relative to the specification, under explicit assumptions about compilation, assembly, boot code, caches, and hardware.

## Illustrative example

**Specify.** Consider a simplified kernel operation that copies a capability for endpoint `mailbox` into an empty destination slot, possibly reducing its rights. At the abstract level, success requires a valid source capability, adequate authority over the destination, and a destination satisfying the operation's constraints. The result grants no rights beyond the source. Invalid requests must follow the specified error behavior.

This example illustrates the proof structure rather than reproducing an entire seL4 system-call specification. An actual proof must include all capability types, derivation rules, error cases, and relevant kernel-state effects.

**Refine the representation.** In an executable model, slots and capabilities have detailed structure. In C, the same objects occupy memory and use concrete encodings and links. A representation relation maps those concrete objects to the abstract capability state. Invariants include valid object references, correctly formed capability structures, and consistency of the kernel's bookkeeping.

**Prove the step.** Starting from related states that satisfy the invariants, execute the C operation. Show that its result and updated memory correspond to an allowed abstract transition, and that the invariants remain true. This includes branches that reject a request; proving only the successful path would not establish the interface contract. Connecting these step proofs across the refinement layers covers arbitrary sequences of modeled kernel operations, rather than a finite collection of tests.

**Interpret the guarantee.** If the abstract operation cannot grant write permission from a read-only source, a corresponding implementation execution cannot do so either. This does not prove that every system using seL4 has the right initial permissions or that the abstract policy captures every desired security property. The 2009 paper explicitly distinguishes its functional-correctness result from a separate high-level access-control proof not connected to this refinement result.

## Concepts and terms

**[1] Capability-based microkernel.** A small privileged kernel exposes objects through protected references carrying authority. Possessing a capability permits specified operations; ordinary user code cannot fabricate a valid capability by choosing its bit pattern.

**[2] Refinement.** A relation showing that the lower-level system's observable behaviors are allowed by the higher-level specification. It transfers appropriate properties of the specification to the implementation, not the truth of an unstated requirement.

**[3] Executable specification.** A precise model detailed enough to run and to bridge abstract behavior with implementation choices. seL4's model derives from a Haskell prototype, but the proof concerns the translated definitions and C code.

**[4] Invariant.** A property established initially and preserved by all relevant transitions, allowing later operations to rely on it.

**[5] Isabelle/HOL.** An interactive theorem prover for higher-order logic. Human-guided proofs are checked by a small logical kernel; external execution components remain outside that proof unless separately justified.

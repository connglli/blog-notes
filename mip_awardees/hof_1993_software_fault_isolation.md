# Efficient Software-Based Fault Isolation

**Summary by:** GPT 6 Astra

**Author:** Robert Wahbe, Steven Lucco, Thomas E. Anderson, and Susan L. Graham

**Source:** SOSP 1993; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/168619.168635

## Key insight

Rewriting unsafe machine instructions can confine an untrusted module's stores and control transfers within one address space. This replaces expensive address-space crossings with local enforcement around the operations that could escape.

## Basic idea

Software fault isolation assigns a module a fault domain [1] with separate code and data segments. Statically safe instructions remain unchanged; unsafe stores and indirect control transfers are checked or sandboxed [2]. Reserved registers and code verification [3] prevent untrusted control flow from bypassing the enforcement sequence. Controlled cross-domain calls [4] permit communication with other modules while preserving protection. The basic isolation policy constrains writes and execution targets, not every possible read or resource-consuming behavior.

## Illustrative example

**Layout.** Give an extension a power-of-two-aligned 64 KiB data segment beginning at `0x40000` and a distinct code segment. For this simplified example, unsafe stores use a register address with no immediate displacement. Only the data segment is writable by the extension, so it cannot modify its instrumented code.

**Constrain a store.** A candidate address `p` is converted to `(p & 0xffff) | 0x40000` in a reserved address register, and the store uses that register. Every resulting address lies between `0x40000` and `0x4ffff`. If the extension supplies `0x91234`, the store targets `0x41234` inside its own segment. Sandboxing confines the damage; it does not preserve the intended meaning of an invalid pointer or necessarily report the offending instruction.

**Preserve the invariant.** Rewriting only the arithmetic sequence is insufficient if the extension can set the reserved register directly or reach an unchecked store. A verifier checks the instruction stream and register usage. The dedicated-register discipline makes the actual store depend on a confined address even when a branch reaches part of the sequence. Indirect jumps receive corresponding treatment using the code-segment bounds. Direct branch targets can be checked statically.

Real instruction sets also permit addressing modes such as register-plus-displacement. The paper uses guard regions and architecture-specific treatment to cover those cases; the simple mask above is not a complete verifier for arbitrary machine code.

**Call out.** An approved call stub transfers to a trusted service, preserving and restoring the state needed for isolation. The service must validate arguments before performing actions outside the extension's domain. Allowing an arbitrary target under the label "service call" would defeat confinement.

This policy does not prevent an infinite loop, guarantee confidentiality of readable memory, or establish the extension's functional correctness. It prevents the particular memory and control-flow violations covered by the verified transformation and runtime interface.

## Concepts and terms

**[1] Fault domain.** Logically separate code and data regions within an address space. Their aligned segment boundaries permit efficient range enforcement through high address bits.

**[2] Address sandboxing.** Forcing a computed address into an allowed segment by masking and setting bits. Unlike a check that traps on an invalid address, it can redirect a faulty operation within the module's own region.

**[3] Code verification.** Checking that every relevant instruction obeys the transformation's invariants, including protected registers and control-transfer restrictions. The security argument depends on the whole reachable instruction stream, not isolated snippets.

**[4] Cross-domain call.** A transfer through a controlled interface that intentionally crosses the ordinary confinement boundary. Its stub and destination form part of the trusted enforcement mechanism.

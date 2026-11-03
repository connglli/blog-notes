# Safe Kernel Extensions Without Run-Time Checking

**Summary by:** GPT 6 Astra

**Author:** George C. Necula and Peter Lee

**Source:** OSDI 1996; SIGOPS Hall of Fame Award 2006

**Link:** https://www.usenix.org/conference/osdi-96/safe-kernel-extensions-without-run-time-checking

## Key insight

An extension can carry a checkable proof about its actual machine code instead of asking the kernel to trust its author or compiler. Once that proof establishes the kernel's policy, the covered safety checks need not be repeated during execution.

## Basic idea

Proof-carrying code [1] combines native instructions with evidence that they satisfy a published safety policy [2]. A verification-condition generator [3] derives a safety predicate from the instructions and their calling precondition. The producer constructs a proof; the consumer independently derives the predicate from the received code and checks the proof using a small proof checker [4]. The accepted code can then execute directly under the checked assumptions. Soundness depends on the policy, instruction semantics, generator, and checker, not on the untrusted producer's willingness to supply a convincing-looking certificate.

## Illustrative example

**Specify access.** A kernel passes a packet-filter extension a buffer base p and length n. The precondition grants read access to each byte at `p + i` for `0 <= i < n`, with the relevant addresses representable. It grants no write permission. The extension must return an accept/reject decision and preserve the kernel's protected memory.

**Write a filter.** The extension rejects when `n < 8`. Otherwise it reads byte `p + 7` and accepts only if that byte equals a chosen tag. This is our simplified straight-line filter, not a copy of the paper's Alpha assembly examples.

**Generate obligations.** The control-flow branch establishes `n >= 8` on the only path reaching the load. The load obligation is that `p + 7` is readable. The proof combines `0 <= 7`, `7 < n`, and the buffer precondition to discharge it. Return-path obligations establish the permitted result and exit behavior. A store to `p + 7` would need a write-permission fact that the stated precondition does not provide.

**Check the submitted binary.** The kernel decodes the native instructions it actually received, reconstructs the safety predicate, and checks the supplied proof against that predicate. It cannot merely accept a valid proof about a producer-supplied formula: that formula might describe different code. If the branch is removed, a short packet can reach the load and the original proof no longer establishes the resulting obligation.

**Execute under the contract.** The checked byte load does not need an additional dynamic bounds test beyond the program's own control flow that established its safety. This does not mean the extension has no branches or that every possible security property was proved. The caller must satisfy the precondition, the executable code must remain the validated code, and hardware must implement the modeled instructions. The chosen example terminates, but arbitrary loops require additional proof obligations or restrictions.

## Concepts and terms

**[1] Proof-carrying code.** Executable code distributed with a formal certificate checked before use. It proves a property of behavior rather than identifying the author cryptographically.

**[2] Safety policy.** The consumer's permitted behavior, expressed through instruction rules, logical axioms, and a calling precondition. A proof is only as relevant as this policy.

**[3] Verification-condition generator.** A trusted procedure translating the received code and control flow into logical obligations sufficient for the desired safety property.

**[4] Proof checker.** A program validating an explicit derivation under the chosen logic. The paper encodes predicates and proofs in the Edinburgh Logical Framework, where checking the proof's type establishes the corresponding proposition.

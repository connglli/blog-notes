# Proof-Carrying Code

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:** George C. Necula (Carnegie Mellon University)

**Source:** POPL 1997

**Link:** https://doi.org/10.1145/263699.263712

## Key insight

Rather than trust the producer or inspect the code itself, the host defines a safety policy and requires every untrusted binary to arrive with a machine-checkable proof that the code obeys it; checking the proof is much easier than producing it, so the trusted part of the system shrinks to a small proof checker.

## Basic idea

A host that executes foreign code, whether a kernel loading a packet filter or an ML runtime calling a C function, must decide whether the code respects its invariants, and the traditional options all fail somewhere: signatures only delegate trust to a person or compiler, and sandboxing, interpretation, or a safe language subset costs run-time performance or expressiveness [1]. Proof-carrying code moves the work to load time: the consumer publishes a safety policy, which consists of a verification-condition generator, a set of proof rules, and a precondition and postcondition for each imported function [2], and the producer sends native code together with a proof that the code's safety predicate follows from the policy [3]. The proof is encoded in the Edinburgh Logical Framework, so validation is type checking, and the consumer's checker is a small program whose correctness, together with the soundness of the policy itself, is all the consumer must trust [4]. Certification is expensive but happens once on the producer's side, on any machine and in any style; validation is cheap, happens at load time, and if either the code or the proof is tampered with, checking either fails or the modified code is still safe [5]. In the reported experiments, hand-tuned DEC Alpha packet filters carry proofs that validate at load time, run faster than interpreted Berkeley Packet Filters, and amortize their validation cost after a few hundred packets [6].

## Illustrative example: a conditional write in a record

**The service and the policy.** A kernel lets a user routine update one word of a two-word record. The record at address `cell` holds a flag in word 0 and a value in word 1, and the kernel calls the routine with the address of the record in register `r8`. The policy states that the routine may read both words, and may write the value word only if the flag is not zero:

```text
Pre = cell : addr and cell + 8 : addr and (sel(mem, cell) != 0 implies cell + 8 : addr)
```

`cell : addr` means that `cell` is a valid aligned address, and `sel(mem, cell)` is the contents of memory at `cell`. The routine is supposed to increment the value but only when the flag permits it.

**The untrusted program.** The producer writes the routine in assembly, with two invariant annotations that the kernel's policy format allows:

```text
    INV Pre
    LD  r9, 0(r8)        ; load the flag
    BEQ r9, done         ; skip the write when the flag is 0
    INV cell + 8 : addr  ; claim: from here, the value word is writable
    LD  r10, 8(r8)       ; load the value
    ADD r10, 1, r10      ; increment it
    ST  r10, 8(r8)       ; store it back
done: RET
```

**The verification condition.** The policy's VC generator walks the program backwards, one rule per instruction [3]. A load `LD ra, n(rb)` contributes "`rb + n` is an address and the rest holds with the value `sel(mem, rb + n)` substituted for `ra`"; a store contributes "`rb + n` is an address and the rest holds in the updated memory"; a branch contributes both paths; the annotations contribute their predicates at their program points. For this routine the obligations reduce to two facts: the flag load is inside the readable region (true by `Pre`), and the store is safe. At the store, the generator requires `cell + 8 : addr`, which is not given unconditionally, so the invariant supplies it as an obligation: assuming the branch fell through, `r9 != 0`.

**The proof and the check.** The producer must derive the safety predicate, which conjoins `Pre implies VC(0)` with the invariant obligations, and ships the derivation. The only interesting steps connect the branch condition to the permission in the precondition:

```text
from LD rule:       r9 = sel(mem, cell)
congruence:         sel(mem, cell) != 0        (from r9 != 0 and the equation)
implication elim:   cell + 8 : addr            (from Pre's third conjunct and the above)
```

The whole derivation is encoded as an LF term; the consumer's checker type-checks that term against the LF signature encoding the policy [4]. It never re-runs a solver and never looks at the producer's toolchain, and running the routine afterwards needs no checks. If someone changes the store to target a different offset, the existing proof no longer type-checks; if someone modifies both the code and the proof consistently so that validation still succeeds, the new code is still safe, because validation accepts only a proof of the safety predicate of the code as shipped.

## Concepts and terms

**[1] The problem and the alternatives.** Examples of the problem include installing application code into an OS kernel, executing mobile or web code, and linking foreign functions into a language runtime such as ML, where the foreign code must not break heap or representation invariants. Signature-based trust fails because trusted people and compilers make mistakes; interpretation and run-time checks (as in the BSD Packet Filter) cost speed; software fault isolation and safe language subsets (for example Modula-3 with its safe pointer casts) restrict the implementation and still charge overhead. PCC's claim is that the producer can keep hand-optimized native code, and the consumer still gets certainty.

**[2] The safety policy.** Defined by the code consumer and consisting of three parts. A Floyd-style verification-condition generator, derived from an abstract machine that describes the instruction set. A set of axioms and inference rules, an extension of first-order predicate logic with application-specific predicates such as `addr`, `ro_addr`, and `sel`, used to prove the condition. A precondition, the calling convention describing what the code may assume when invoked, and a postcondition describing what it must establish before returning. Different services can have different policies; the paper notes one could even require a semaphore to be acquired and released.

**[3] The abstract machine and the safety predicate.** The abstract machine models a subset of DEC Alpha assembly: a state is the register values, the memory (a total map on aligned addresses), and the program counter; programs are checked without function calls in the basic presentation. Invariant annotations `INV P` mark program points and carry predicates; the only restriction is that every backward branch must target an invariant, which lets the whole verification condition be computed in one backward pass. The safety predicate conjoins, for every instruction, the machine-safety conditions of reaching it with the reasoning of the instructions after it. Proving it means no executed path blocks and the postcondition holds on return. Loops make invariants essential; the paper's later case studies include loops.

**[4] Proofs in LF and the checker.** Derivations in the logic are represented as objects in the Edinburgh Logical Framework, whose support for binding, hypothetical judgments, and variable renaming keeps the encodings compact, and a compact binary encoding carries them over the wire. Checking a proof is then LF type checking; the checker accepts a signature, which encodes the policy's logic, so new logics need no new checker, only a new signature. The paper defines LFo, a fragment with trusted signatures, second-order constants, first-order abstractions, and canonical objects only, whose type checking is simple enough that a naive implementation stays small. The consumer must trust the checker's implementation and the soundness of the policy itself, including its verification-condition rules, but not the producer, its compiler, or its proof generator.

**[5] Certification versus validation.** Certification is the producer-side search for a proof: goal-directed search, interactive theorem proving, or heuristics, with all its cost and complexity. Validation is the consumer-side check, cheap enough to sit in performance-critical paths. The separation is the paper's main principle: proof checking is much easier than proof generation. Certification happens once per code version regardless of how many times the code runs, and loading a filter requires only its validation time. Any modification to a binary either breaks validation or preserves safety, and the host performs no run-time checks afterwards.

**[6] Case studies and measured cost.** The main experiment implements four network packet filters in hand-tuned DEC Alpha assembly with a prototype assembler that emits PCC binaries: 8 to 47 instructions, binary sizes (code plus proof) of 315 to 835 bytes, validation times of 358, 546, 1327, and 850 microseconds, and up to about 15 KB of validation workspace; filters run about ten times faster than BPF filters, at the price of a startup cost that is amortized after 860 packets against BPF and 8300 packets against a Modula-3 filter. A second study certifies foreign functions for the TIL Standard ML runtime under a policy that preserves the heap representation and data-type invariants, limited to functions without calls or allocation; a third certifies an internet checksum routine, with a 1.3 ms validation latency amortized after about 150 KB of data, and the paper's examples validate in 1 to 3 milliseconds overall. The remaining practical difficulties are establishing a policy general enough to certify realistic code and automating proof generation for loops and complex invariants, which the report's discussion leaves open.

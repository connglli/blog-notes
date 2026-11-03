# Proof-carrying code

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:** George C. Necula

**Source:** POPL 1997; SIGPLAN Most Influential POPL Paper Award 2007.

**Link:** https://doi.org/10.1145/263699.263712

## Key insight

An untrusted code producer can supply a machine-checkable proof that its binary obeys the consumer's safety policy. The consumer checks the proof against a condition generated from the received binary, without trusting the producer or its compiler.

## Basic idea

The consumer defines a safety policy [1] describing permitted memory operations and required entry conditions. A verification-condition generator [2] symbolically processes native instructions and produces a formula sufficient for safety, using annotations at control-flow boundaries when necessary. The producer supplies a proof of that formula in a formal logic [3]. The consumer independently generates the condition and checks the proof before execution; acceptance establishes the stated policy, not arbitrary functional correctness.

## Illustrative example

**Policy.** Suppose an extension receives an array base `base`, an element count `count`, and an index `index`. The entry contract grants read permission exactly for the array's `count` elements, with a valid nonnegative count. For this example, use mathematical addresses and assume the array allocation and address arithmetic cannot overflow.

The extension returns zero if the index is outside the array. Otherwise it reads that element. Its two branches correspond to this simple C routine:

```c
int select_or_zero(const int *base, int count, int index) {
    if (index < 0 || index >= count)
        return 0;
    return base[index];
}
```

The certificate concerns the actual compiled instructions, not this explanatory source code.

**Condition generation.** At the load instruction, the generator requires read permission for `base + index * sizeof(int)`. The path reaching that instruction supplies `0 <= index < count`. Combined with the entry contract, these facts imply the required permission. On the zero-return path there is no array access to justify.

For a real machine, the policy and arithmetic reasoning must also account for finite-width addresses and the concrete load width. Removing that obligation from the model would weaken the result.

**Checking.** The producer constructs a derivation of the load-permission implication. The consumer reconstructs the same obligation from the received binary and validates the derivation. If a malicious producer removes the bounds branch but reuses the old proof, the resulting unconditional load obligation is different and is not established by that proof.

The trusted implementation includes the policy's interpretation, the instruction model, condition generation, and proof checking. A proof checker disconnected from the code being executed would not provide this guarantee.

## Concepts and terms

**[1] Safety policy.** The consumer's formal rules for acceptable execution, including assumptions about inputs and allowed operations. Memory safety is one possible policy; a proof does not imply properties absent from the policy.

**[2] Verification condition.** A logical formula whose validity is sufficient for a program to satisfy the policy. Symbolic instruction processing propagates register and memory facts and emits obligations at potentially unsafe operations.

**[3] Formal proof.** A derivation assembled from specified inference rules. Constructing a proof may be difficult, but checking each inference can be straightforward. The consumer need not trust the search procedure that found the proof.


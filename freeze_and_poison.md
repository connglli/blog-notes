# Taming Undefined Behavior in LLVM

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:** Juneyoung Lee, Yoonseung Kim, Youngju Song, Chung-Kil Hur (Seoul National University); Sanjoy Das (Azul Systems), David Majnemer (Google), John Regehr (University of Utah), Nuno P. Lopes (Microsoft Research)

**Source:** PLDI 2017

**Link:** https://doi.org/10.1145/3062341.3062343

**Code:** [LLVM fork](https://github.com/snu-sf/llvm-freeze/tree/pldi) and [Clang fork](https://github.com/snu-sf/clang-freeze/tree/pldi)

## Key insight

LLVM's two representations of deferred undefined behavior, `undef` and `poison`, have inconsistent semantics that leave textbook optimizations such as global value numbering and loop unswitching mutually contradictory. Replacing `undef` with `poison`, making branching on poison immediate undefined behavior, and adding a `freeze` instruction removes the conflicts while keeping existing optimizations and generated-code quality.

## Basic idea

C/C++ programs are full of undefined behavior [1], and LLVM's IR models it in two classes: immediate UB [2], for operations such as division by zero or invalid dereferences, and deferred UB [2], for operations that are safe to execute speculatively but yield an unreliable value, such as signed overflow or a shift past the bit width. Deferred UB is represented by `undef` and `poison` [3]. The two forms interact badly: `undef` may take a different value at each use, so duplicating an operand (`mul x, 2` into `add x, x`) or hoisting a division past a guard that may be undef is unsound, and different passes disagree about whether branching on poison is UB, which makes GVN [7] and loop unswitching [8] mutually inconsistent. The paper removes `undef`, keeps only `poison`, adds a `freeze` instruction [5] that turns a poisoned value into an arbitrary but fixed one, makes every operation except `phi`, `select`, and `freeze` [6] propagate poison, and makes branching on poison immediate UB. GVN then becomes sound, and loop unswitching becomes correct once it freezes the condition it hoists. A prototype on LLVM 4.0 changed 578 lines and added few `freeze` instructions, with compile time, memory, code size, and runtime close to the baseline.

## Illustrative example: `a + b > a` becomes `b > 0`

In C, `a + b > a` can be replaced by `b > 0` because signed overflow is UB [1]: the executions where the addition overflows are undefined, and the two expressions agree on every execution where it does not.

**The IR.** The addition carries the `nsw` attribute [4], which means it yields `poison` [3] on signed overflow:

```
%sum = add nsw i32 %a, %b
%cmp = icmp sgt i32 %sum, %a
```

Without `nsw`, `add` wraps on overflow and the replacement would be wrong on any execution that overflows. With `nsw`, the comparison is poison whenever the addition overflows, and under the paper's semantics branching on poison is immediate UB [2].

**Why `undef` is not enough.** Suppose overflow produced `undef` [3] instead. Take `a = INT_MAX` and `b = 1`. The original comparison is `undef > INT_MAX`, which is false for every integer, while the replacement `b > 0` gives `1 > 0`, which is true. Both executions are defined, so the replacement would change the behavior of a defined execution and would be unsound; `undef` cannot justify this optimization.

**Why `poison` is enough.** Poison is not a value of the type: it taints the comparison, so whenever the comparison becomes a branch condition, the original program executes UB [1] on the overflow input. A transformation may give any behavior to an execution in which the original has UB [9], so replacing the comparison with `b > 0` is allowed. On executions without overflow, the two expressions agree.

**Freezing a value.** Using `%sum` in further arithmetic propagates poison; using a poison comparison as a branch condition triggers immediate UB. The `freeze` instruction [5] turns poison into an arbitrary but fixed value and leaves defined values unchanged:

```
%sum = add nsw i32 %a, %b
%f = freeze i32 %sum
```

All uses of `%f` see the same value, while two different freeze instructions may choose different values. Freeze is the tool the paper uses to repair transformations that move values across poison boundaries, such as loop unswitching [8].

## Concepts and terms

**[1] Undefined behavior (UB).** Behavior that the C/C++ standards or the IR leave unconstrained. Optimizers use UB by assuming it does not happen; for example, signed overflow is UB in C, so `a + b > a` may be replaced by `b > 0`. UB is untrapped, so its effects can appear far from the operation that caused it.

**[2] Immediate and deferred UB.** LLVM's two classes of undefined behavior. Immediate UB leaves the whole execution unconstrained, without requiring a trap, and cannot safely be introduced on a previously defined path by speculation; division by zero and invalid pointer dereferences are examples. Deferred UB is safe to execute speculatively but yields an unreliable value; signed overflow and shifts past the bit width are examples. Under the paper's proposal, branching on poison is immediate UB.

**[3] undef and poison.** The two IR values that represent deferred UB [2]. `undef` is a value of the given type that may differ at each use. `poison` is not a value of the type: most operations return poison if any operand is poison, and under the proposal branching on it is immediate UB [2]. The paper removes `undef` and keeps `poison`, with `phi` and `select` [6] propagating poison only from the value they choose.

**[4] nsw and nuw.** Attributes on LLVM arithmetic instructions meaning "no signed wrap" and "no unsigned wrap": if the operation overflows, the result is poison [3] instead of a wrapped value. They let the compiler assume that overflow does not happen without paying for a trap.

**[5] freeze.** An instruction that returns its operand unchanged when it is a defined value, and an arbitrary value of the type when the operand is poison [3]. All uses of the result of one dynamic execution agree. Duplicating that execution can introduce independent choices; in particular, sinking a freeze into a loop can let its result change between iterations (Section 5.5).

**[6] SSA, phi, and select.** Static single assignment (SSA) form gives every register a single definition. A `phi` instruction selects the value associated with the predecessor block that executed. A `select` chooses one of two values using a Boolean condition: poison in the unchosen value does not propagate, but a poison condition produces poison (Figure 5).

**[7] GVN (global value numbering).** An optimization that replaces equal expressions with a shared representative. For example, a branch on `x == y` can justify substituting `y` for `x` on its true path. Making a poison branch condition immediate UB excludes executions where that equality test would otherwise allow substitution of a poison value for a defined one.

**[8] Loop unswitching.** An optimization that hoists a loop-invariant conditional out of a loop and duplicates the loop body for each outcome. The hoisted branch may execute even when the original loop never ran, so if the condition may be poison [3] the transformation has to freeze it [5]; otherwise it introduces UB on an execution that was defined.

**[9] Correctness of a UB-aware transformation.** Every behavior of the transformed program must be permitted by the original. A transformation may remove nondeterministic choices and make poison more defined; it must preserve concrete results on defined inputs and must not introduce immediate UB on an input where the original excludes it.

**[10] Poison-aware static analysis.** An analysis fact may hold only when the value is not poison: `shl 1, y` is a power of two whenever its result is defined. Such a fact does not prove that the value is safe as a divisor. Hoisting `1 / a` out of a loop that may execute zero times can introduce immediate UB if `a` is poison. The client must establish non-poisonness when its use of an analysis fact requires it (Section 5.6).

# Taming Undefined Behavior in LLVM

**Author:**
- Juneyoung Lee, Yoonseung Kim, Youngju Song, Chung-Kil Hur (Seoul National University)
- Sanjoy Das (Azul Systems), David Majnemer (Google), John Regehr (University of Utah), Nuno P. Lopes (Microsoft Research)<br/>

**Source:** PLDI 2017

**Link:** https://doi.org/10.1145/3062341.3062343<br/>

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

**Freezing a value.** If the program uses `%sum` directly, its poison would trigger UB. The `freeze` instruction [5] turns poison into an arbitrary but fixed value and leaves defined values unchanged:

```
%sum = add nsw i32 %a, %b
%f = freeze i32 %sum
```

All uses of `%f` see the same value, while two different freeze instructions may choose different values. Freeze is the tool the paper uses to repair transformations that move values across poison boundaries, such as loop unswitching [8].

## Concepts and terms

**[1] Undefined behavior (UB).** Behavior that the C/C++ standards or the IR leave unconstrained. Optimizers use UB by assuming it does not happen; for example, signed overflow is UB in C, so `a + b > a` may be replaced by `b > 0`. UB is untrapped, so its effects can appear far from the operation that caused it.

**[2] Immediate and deferred UB.** LLVM's two classes of undefined behavior. Immediate UB has immediate effects, such as a processor trap or memory corruption, and cannot be executed speculatively; division by zero and invalid pointer dereferences are examples. Deferred UB is safe to execute speculatively but yields an unreliable value; signed overflow and shifts past the bit width are examples. Under the paper's proposal, branching on poison is immediate UB.

**[3] undef and poison.** The two IR values that represent deferred UB [2]. `undef` is a value of the given type that may differ at each use. `poison` is not a value of the type: most operations return poison if any operand is poison, and under the proposal branching on it is immediate UB [2]. The paper removes `undef` and keeps `poison`, with `phi` and `select` [6] propagating poison only from the value they choose.

**[4] nsw and nuw.** Attributes on LLVM arithmetic instructions meaning "no signed wrap" and "no unsigned wrap": if the operation overflows, the result is poison [3] instead of a wrapped value. They let the compiler assume that overflow does not happen without paying for a trap.

**[5] freeze.** An instruction that returns its operand unchanged when it is a defined value, and an arbitrary but fixed value of the type when the operand is poison [3]. All uses of one freeze see the same value, but two freeze instructions over the same poison may choose differently, so duplicating or sinking a freeze is not allowed. Freeze is how a program removes poison without triggering UB.

**[6] SSA, phi, and select.** Static single assignment (SSA) form gives every register a single definition, so a control-flow join needs a `phi` instruction that takes the value from the branch that was taken. `select` is the value-level conditional. In the proposal, `phi` and `select` return poison only when the chosen value is poison, unlike arithmetic operations, which return poison when any operand is poison.

**[7] GVN (global value numbering).** An optimization that finds expressions computing the same value and replaces redundant uses with a representative, for example replacing `w = x + 1` with `y` inside a block guarded by `t == y`. This substitution is only sound if a poison value cannot leak into a place where a defined value was expected, which the branch-on-poison rule provides.

**[8] Loop unswitching.** An optimization that hoists a loop-invariant conditional out of a loop and duplicates the loop body for each outcome. The hoisted branch may execute even when the original loop never ran, so if the condition may be poison [3] the transformation has to freeze it [5]; otherwise it introduces UB on an execution that was defined.

**[9] Correctness of a UB-aware transformation.** A transformation is correct when it preserves every execution in which the original program has defined behavior; executions in which the original triggers UB may be given any behavior. This is why replacing a comparison that becomes poison with a constant is allowed: the executions where the poison reaches a branch are already UB.

**[10] Poison-aware static analysis.** LLVM analyses typically report facts that hold only when the analyzed values are not poison [3]; for example, `shl 1, y` is known to be a power of two, but if `y` is poison the result may be any value. This is safe for rewriting expressions, because the rewritten expression is poison exactly when the original is, but unsafe for moving operations past control flow: hoisting `1 / a` because `a` is known to be a power of two is unsound if `a` may be poison and the loop may never run. The paper discusses returning "up to poison" results and letting the client check non-poisonness.

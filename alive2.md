# Alive2: Bounded Translation Validation for LLVM

**Summary by:** GPT 6 Astra

**Author:** Nuno P. Lopes, Juneyoung Lee, Chung-Kil Hur, Zhengyang Liu, John Regehr

**Source:** PLDI 2021, pages 65-79

**Link:** https://doi.org/10.1145/3453483.3454030

**Code and demo:** [Alive2](https://github.com/AliveToolkit/alive2), [online validator](https://alive2.llvm.org/)

## Key insight

Check the actual LLVM IR before and after an optimization, including LLVM's undefined and nondeterministic values, without trusting the optimization's implementation. Restrict loop execution to a finite bound so that automatic refinement checking remains practical.

## Basic idea

Alive2 performs translation validation [1] on pairs of LLVM functions. Symbolic execution [2] builds expressions for return values, memory, and undefined behavior, combining control-flow paths instead of enumerating concrete inputs. The checker asks whether the optimized function refines [3] the original: every target behavior must be allowed by the source, including when the target makes an undefined value more defined. Bounded loop unrolling [4] turns loops into acyclic code and excludes executions that reach either function's unrolling limit, so a successful check is not a proof for arbitrary loop lengths.

## Illustrative example

**The candidate transformation.** This function freezes an input once and adds that same chosen byte repeatedly. `freeze` [5] turns an undefined or poison input into an ordinary, fixed value:

```llvm
define i8 @sum_repeated(i8 %input, i8 %count) {
entry:
  %chosen = freeze i8 %input
  br label %loop

loop:
  %index = phi i8 [ 0, %entry ], [ %next, %body ]
  %total = phi i8 [ 0, %entry ], [ %updated, %body ]
  %more = icmp ult i8 %index, %count
  br i1 %more, label %body, label %exit

body:
  %updated = add i8 %total, %chosen
  %next = add i8 %index, 1
  br label %loop

exit:
  ret i8 %total
}
```

Suppose an optimizer moves `%chosen = freeze i8 %input` from `entry` to the start of `body`. Both functions remain valid SSA: each use has an available definition. But the target executes the freeze once per iteration, allowing independent choices.

**Unrolling and symbolic execution.** Unroll enough to include two body executions and the final exit test. For the concrete input `count = 2`, the source returns `(s + s) mod 256`, where `s` is its freeze result. If `input` is poison, the target returns `(t0 + t1) mod 256`, where `t0` and `t1` are independent freeze results. The `phi` instructions select the initial zeroes on entry and the updated index and accumulator on each backedge.

**Refinement query.** A counterexample must give a target output that no source choice can produce [6]. Choose `t0 = 0` and `t1 = 1`: the target returns 1, while `(s + s) mod 256` is even for every byte `s`. Neither function executes undefined behavior on this input because freeze absorbs the poison before arithmetic. The move is therefore incorrect, even though both programs agree for every ordinary, fixed value of `input`.

**What the bound means.** Paths needing more iterations than the chosen unrolling allows are redirected to a sink and excluded from the query. Reaching that sink is not treated as a program bug. If the bound cannot include the two-iteration execution above, this particular counterexample is missed; increasing the bound exposes it. Unsupported constructs and solver failures must also be distinguished from a successful check [7].

## Concepts and terms

**[1] Translation validation.** Verify a particular transformation result rather than prove the compiler correct for all programs. LLVM IR is a typed intermediate representation between source-language processing and machine-code generation. Alive2 can compare two IR files or run between compiler passes. Its contract is intraprocedural: function signatures and their interfaces supply the context for checking each function. Unknown calls are modeled through their arguments, memory effects, and applicable attributes rather than by executing their implementations.

**[2] Symbolic execution and path merging.** A symbolic register stores a value expression and a poison flag; a program state also contains memory and an immediate-UB flag. Integers use fixed-width bit-vectors, while supported floating-point operations use SMT's floating-point theory. SSA, static single assignment, gives each register one definition. A block's reachability condition guards its effects. `phi` selects an incoming value according to the predecessor, and return sites are merged with conditional expressions. This yields one combined expression for a register instead of separately exploring every control-flow path.

**[3] Refinement of final states.** If the source executes immediate UB, the target is unconstrained. Otherwise the target must not introduce UB, must preserve return versus no-return behavior in the checked domain, and must refine the return value and observable memory. A defined source value must be preserved; source poison can become any value, and a source set of possible values can become a subset. Memory comparison accounts for different local allocation identities rather than demanding equal raw block identifiers. The companion [memory-model summary](smt_llvm_memory_model.md) covers that encoding in detail.

**[4] Bounded loop unrolling.** Duplicate loop bodies, redirect branches, and repair SSA operands and `phi` nodes. A backedge leaving the final copy goes to a sink. Add the condition that neither source nor target reaches its sink, since an optimization may change how many iterations each side needs. This avoids reporting a mismatch caused only by unequal truncation. Nested loops are processed inside-out. The method misses bugs outside the admitted executions and does not prove general termination or infinite-loop equivalence.

**[5] Undef, poison, and freeze.** `undef` can supply a different permitted value on each use; poison propagates through most operations and causes immediate UB in uses such as branch conditions. A dynamic execution of `freeze` chooses one ordinary value from an undef operand's permitted values, or any value of the type for poison. Every use of that execution's result agrees. Alive2 implements this distinction by refreshing undef variables at uses but retaining the variables that encode a freeze result.

**[6] Quantified SMT checking.** An SMT (satisfiability modulo theories) solver searches for assignments satisfying logical formulas over domains such as bit-vectors and arrays. Under valid input assumptions, every target choice must be explainable by some source choice. For equal fixed inputs, a value-mismatch search therefore has the shape `exists target_choices; forall source_choices: outputs differ`, not simply two unrelated executions with different outputs. Alive2 checks separate obligations for UB, return behavior, poison, undef, concrete values, and memory. An unsatisfiable negated obligation establishes that property; a satisfying model explains a failure; unknown or timeout is inconclusive.

**[7] Scope and trust.** Bounds and approximations can hide bugs. For example, the paper's input encoding considers fully undef or fully defined arguments, not every partially undef input. Unsupported features may be conservatively approximated or cause a function to be skipped; a counterexample depending on an approximation is not reported as a definite compiler bug. The implementation, its semantic model, Z3, and LLVM's IR parser are trusted. The paper describes a goal of avoiding false alarms, not a machine-checked proof that the checker itself is infallible.

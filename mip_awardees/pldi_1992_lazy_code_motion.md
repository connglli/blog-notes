# Lazy Code Motion

**Summary by:** GPT 6 Astra

**Author:** Jens Knoop, Oliver Rüthing, Bernhard Steffen

**Source:** PLDI 1992; SIGPLAN Most Influential PLDI Paper Award, 2002

**Link:** https://doi.org/10.1145/143095.143136

## Key insight

Remove redundant evaluations without computing their saved values earlier than necessary, because early placement can needlessly lengthen temporary lifetimes.

## Basic idea

Lazy code motion performs partial redundancy elimination [1] through successive data-flow analyses [2]. It identifies safe earliest placements, delays them while preserving computational optimality, and removes isolated placements that provide no reuse. Inserted temporaries [3] replace redundant evaluations where their operands have not changed. Its optimality concerns the paper's safe code-motion model, not globally optimal register allocation or arbitrary effectful expressions.

## Illustrative example

**Control flow.** An entry branch chooses `Left` or `Right`, both reaching `Join`. `Left` computes `u = a+b` and uses it. `Right` performs unrelated work. `Join` computes `v = a+b` and uses it. Assume `a+b` is pure, cannot trap, and neither operand changes along these paths.

**Redundancy.** Along `Left -> Join`, the second addition repeats the first. Along `Right -> Join`, it does not. Deleting the join computation outright would leave the right path without a value.

**Safe placement.** A temporary could be initialized before the branch and reused throughout both arms. That removes the repeated evaluation, but holds the temporary across all unrelated work in `Right`.

**Delay.** Keep `t = a+b` immediately before its first use in `Left`. Insert another `t = a+b` at the end of `Right`, just before the join. Replace the addition at `Join` by `t`. Each path executes one addition, and the right path does not keep the temporary live across its unrelated work. If `Right` also has an exit bypassing `Join`, insert on the edge entering `Join`, not before that exit decision.

**Isolation.** An added temporary used only at its own insertion point provides no sharing benefit; retain the direct expression there instead. Operand assignments kill availability, so adding `a = a+1` before the join would require recomputation on that path rather than reuse of the old sum.

## Concepts and terms

**[1] Partial redundancy.** An expression has already been evaluated on some, but not all, incoming paths without intervening operand changes.

**[2] Data-flow analysis.** Compute program-point facts by propagating and merging information through the control-flow graph until stable.

**[3] Temporary lifetime.** The interval during which a saved result must remain available; overlapping live temporaries can increase register pressure.

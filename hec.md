# HEC: Equivalence Verification Checking for Code Transformation via Equality Saturation

**Author:**
- Jiaqi Yin, Zhan Song, Cunxi Yu (University of Maryland, College Park)
- Nicolas Bohm Agostini, Antonino Tumeo (Pacific Northwest National Laboratory)<br/>

**Source:** USENIX ATC 2025 (pages 1181-1196)

**Link:** https://www.usenix.org/conference/atc25/presentation/yin<br/>

## Key insight

Equivalence checking becomes a membership test in an e-graph: insert the original and the transformed programs into one e-graph, apply rewriting rules until saturation, and conclude equivalence when the two root e-nodes merge into the same equivalence class; control-flow transformations are covered by rules generated at runtime, each validated by an SMT check of its conditions.

## Basic idea

Compilers perform source-to-source transformations (loop unrolling, tiling, fusion, algebraic simplification) whose correctness is usually checked only by testing, and existing checkers cover either affine control flow or datapath rewrites, not both. HEC translates two MLIR programs into a graph representation [2] (operations as nodes; each loop split into a loopvalue node for start, stop, step, and the loop variable, and an ordered block node for its body; stores get pseudo outputs; variables are renamed by global order of appearance) and inserts both into one e-graph [1]. Datapath transformations are handled by static rules [3] that are proved identities of Boolean and arithmetic algebra; control-flow transformations are handled by dynamic rules [4] generated for the given input from patterns such as unrolling, tiling, fusion, and coalescing, whose conditions (iteration counts, replication structure, absence of memory hazards) are checked with Z3 at generation time. The verification runner alternates saturation with rule injection: if the two roots are not yet in one e-class, it scans the graph for candidate loops, creates a combine node binding them, and adds the matching dynamic rules, until the roots merge or no new rule can be generated, in which case HEC reports the programs as nonequivalent. HEC never declares inequivalent programs equivalent (static rules come from proven identities and dynamic conditions are checked), but the converse report can be a false negative, since a missing rule or a stopped saturation hides a real equivalence. On PolyBenchC and a CNN-Forward benchmark, HEC verified loop unrolling, tiling (factors 2 to 64), and fusion, handled a datapath experiment of 108,012 lines of MLIR in 2,305 seconds, and found two mlir-opt bugs: an unrolling that executes iterations the original skips when a loop's start exceeds its end, and a fusion that violates a read-after-write dependency on an array.

## Illustrative example: an unrolled mask loop

**The programs.** The source loop computes `c[i] = ~(a[i] & b[i])` over 1-bit vectors, written as MLIR affine code:

```text
affine.for %i = 0 to %n {
  %1 = affine.load %a[%i] : memref<?xi1>
  %2 = affine.load %b[%i] : memref<?xi1>
  %3 = arith.andi %1, %2 : i1
  %4 = arith.xori %3, %true : i1
  affine.store %4, %c[%i] : memref<?xi1>
}
```

**Graph representation.** Every operation becomes a node carrying its name, inputs, data type, and dimensions, connected by edges. The loop becomes a `loopvalue` node holding (0, %n, step 1, %i), which both loads consume, plus a `block` node holding the ordered body; the store has no value output, so it gets a pseudo output that keeps it tracked; the result that no other operation consumes (%4) is the block's only isolated output; and %i is renamed by global order of appearance if the name repeats in another scope. Moving `%true` from outside the loop into the body, or the reverse, does not change the graph, so loop hoisting needs no rewrite rule [2].

**Datapath variant, static rules.** The first transformed program computes the same function with De Morgan's law:

```text
affine.for %i = 0 to %n {
  %1 = affine.load %a[%i] : memref<?xi1>
  %2 = affine.load %b[%i] : memref<?xi1>
  %4 = arith.xori %1, %true : i1
  %5 = arith.xori %2, %true : i1
  %6 = arith.ori %4, %5 : i1
  affine.store %6, %c[%i] : memref<?xi1>
}
```

Static rules such as `~x ⇔ x ⊕ true` and `~(a & b) ⇔ (~a) | (~b)` [3] merge the two bodies node by node, so the two program roots end in one e-class and the programs are equivalent.

**Control-flow variant, dynamic rule.** The second transformed program unrolls the loop by 2 into a main loop and a remainder loop:

```text
affine.for %i = 0 to %m step 2 { body(%i); body(%i + 1) }   // %m = 2 * (%n floordiv 2)
affine.for %i = %m to %n { body(%i) }
```

where `body(x)` is the original body with %i replaced by x. The runner cannot merge the roots using static rules alone, so the rule generator recognizes the two loops as an unrolling candidate and asks Z3 whether the pattern condition holds for every %n (the two iteration counts add up to the original count, and the bodies follow the replication pattern); the check succeeds and HEC builds a dynamic rule whose right-hand side is a fresh `combine` node binding the two loops [4]. Saturation merges `combine(loop1, loop2)` with the original loop's e-class, both roots unite, and the unrolled program is equivalent. If the split does not in fact cover the original iterations for every %n, Z3 refutes the condition, no dynamic rule is generated, and the roots stay apart, which is how HEC reports a transformation it cannot justify.

## Concepts and terms

**[1] E-graph and equality saturation.** An e-graph stores expressions and the equalities between them: e-nodes (an operator applied to child e-classes) live in e-classes, and the structure stays closed under congruence, so equal children imply equal parents. Equality saturation applies rewrite rules to the e-graph until no rule adds a new equality; because e-classes share subterms, exponentially many equivalent expressions fit in linear space. HEC uses the egg library.

**[2] MLIR and the graph representation.** MLIR is a compiler IR framework in which each operation belongs to a dialect (arith, affine, func); HEC uses it as the frontend, and C code can be raised to it with Polygeist. HEC's converter maps each operation to a node with its name, inputs, data type, and dimensions; loops become a `loopvalue` node (start, stop, step, and the variable name, so otherwise identical loops stay distinct) plus a `block` node whose body keeps the original operation order, exposes isolated results (values consumed nowhere else in the block), and gives pseudo outputs to operations with no value result such as stores. The same block mechanism captures if and func nesting, and variables are renamed by their global order of appearance so names reused in different scopes do not collide. A converter called the inverter turns the e-graph back into this graph form between verification iterations.

**[3] Static rewriting rules.** A precompiled suite of 62 bitwidth-dependent datapath identities from Boolean and arithmetic algebra, applied by the e-graph runner. Examples from the paper's table include `a ≪ b ⇔ a × 2^b`, associativity and distributivity laws, `a ⊕ 0 ⇔ a`, `¬a ⇔ a ⊕ true`, and De Morgan's law. They are bidirectional and sound by construction, since each is a proven algebraic identity.

**[4] Dynamic rewriting rules and transformation patterns.** Rules generated at runtime for the input at hand, because control-flow transformations create fresh variables, loop bounds, and factors (such as the tiling factor) that a static pattern cannot know in advance. HEC's pattern library covers unrolling, tiling, fusion, and coalescing; each pattern carries a condition, for example that the iteration counts of the split loops add up to the original loop's count and that the bodies are replications, or that fusion introduces no read-after-write hazard. Conditions are checked with Z3 when the rule is generated (this takes well under a second), and Z3 is used for nothing else, so saturation stays scalable. A `combine` pseudo-node binds the several loops that participate in one transformation so that the dynamic rule has a single left-hand side to match.

**[5] Verification runner.** The driver loop: build the initial e-graph from both programs with the static rules; saturate; if the two roots share an e-class, report equivalence. Otherwise run the rule generator over the current graph, inject the dynamic rules it produces, convert the e-graph back to the graph representation, and repeat. Stop when the roots merge (equivalent) or when no new rule can be generated (nonequivalent). E-graph saturation dominates the runtime, over 90% of it in the nested-unrolling experiments.

**[6] Soundness and incompleteness.** HEC is sound: it never reports two inequivalent programs as equivalent, because static rules are proven identities and dynamic rule conditions are validated by Z3. It is incomplete for arbitrary transformations: an unmodeled rule, a rule whose condition the solver cannot discharge, or a saturation run stopped by time or memory limits leaves the roots unmerged, and the tool reports the programs as nonequivalent, which is a false negative when they are in fact equivalent.

**[7] Comparison to prior checkers.** PolyCheck and ISA verify affine/control-flow transformations of C programs; Coward et al. verify datapath rewrites in RTL; CompCert and Alive/Alive2 work at other levels of the compilation stack. MLIR-TV is the only other checker at the MLIR level, but according to the authors' testing it does not support the affine dialect, which makes a direct comparison impractical.

**[8] Evaluation and found bugs.** The evaluation covers twelve PolyBenchC kernels plus CNN-Forward, with transformations applied through mlir-opt (LLVM 18.0.0). Tiling results are stable across factors 2 to 64; unrolling scales superlinearly because the code and e-graph grow (nested unrolling by 16 on both loops makes some kernels hit the time limit, though most finish within 20 minutes); datapath experiments of over 150 generated benchmarks show e-node count and runtime growing linearly with the lines of MLIR, up to 108,012 lines in 2,305 seconds. Two bugs in mlir-opt surfaced: unrolling preserves semantics only when the loop end is guaranteed to exceed the start, and the split can add an iteration the original skips (seen on the Jacobi_1d and Seidel_2d benchmarks); and fusing two loops can violate a read-after-write dependency on an array, changing the memory state.

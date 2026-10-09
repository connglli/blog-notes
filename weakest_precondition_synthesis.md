# Weakest Precondition Synthesis for Compiler Optimizations

**Author:**
- Nuno P. Lopes, José Monteiro (INESC-ID, IST Universidade de Lisboa)<br/>

**Source:** VMCAI 2014

**Link:** https://doi.org/10.1007/978-3-642-54013-4_12<br/>

**Code:** [PSyCO prototype and benchmarks](http://web.ist.utl.pt/nuno.lopes/psyco/)

## Key insight

An optimization is a rewrite rule expressed as two patterns with holes, and the paper synthesizes the weakest precondition over that rule rather than for a single concrete program: a verifier returns two paths that disagree for some instantiation of the holes, an SMT solver enumerates all models that rule the pair out, and their disjunction is the weakest condition for that counterexample. The generated preconditions are correct by construction, and for software pipelining the synthesized condition is strictly weaker than the hand-written precondition verified with PEC.

## Basic idea

Compiler optimizations are rewrite rules, written as patterns: a transformation function `τ: Src => Tgt` over template programs whose holes (`S1`, `B`, ...) stand for arbitrary code [1], plus a precondition [2] that guarantees the rewrite is semantics-preserving at every instantiation. A precondition that is too strong silently loses optimization opportunities, so the paper synthesizes the weakest precondition over the rule itself, in a language of constraints over the read and write sets [3] of the template statements and expressions, and guarantees that the result is the weakest condition expressible there [5]. The algorithm is counterexample-guided [6]: a black-box verifier either proves the rule correct under the current precondition or returns a pair of paths, one from the source pattern and one from the target pattern, that start from the same state and end in different states. Each path pair is encoded into logic by treating a template statement as a conditional write to every variable and each template expression as a fresh value [7], with Ackermann-style constraints [8] that force two occurrences of the same template to agree whenever their inputs agree; the read/write-set memberships are the existential variables, and every model is a sufficient condition that rules out the counterexample. Negating models and re-solving enumerates them all, and their disjunction is the weakest precondition for that counterexample, which is conjoined into the running precondition; model generalization with unsat cores keeps the enumeration small [9]. PSyCO implements the algorithm in about 1,400 lines of Python over Z3; on 18 mostly loop-oriented optimizations it produces conditions with a handful of counterexamples, usually in seconds, with one reported case taking about 163 s in total, and for software pipelining the synthesized condition is weaker than the hand-written one verified with PEC [11].

## Illustrative example: loop unswitching

**The transformation rule.** This is the loop-unswitching rule: `B`, `S1`, and `S2` are holes standing for an arbitrary side-effect-free condition, the then-branch, and the else-branch, while `I` and `N` are program variables. The two listings are therefore one rewrite rule over all instantiations, not a concrete program pair:

```text
while I < N do
  if B then S1 else S2
  I := I + 1
=>
if B then
  while I < N do
    S1
    I := I + 1
else
  while I < N do
    S2
    I := I + 1
```

Instantiating the holes, for example `B = flag`, `S1 = (x := x + 1)`, and `S2 = (x := x + 2)`, yields a concrete source loop and the concrete unswitched loop that the optimizer produces from it. The rule is safe to apply when the branch condition `B` is loop invariant.

**A counterexample.** PSyCO starts with the precondition `true` and asks the verifier. A path pair that disagrees is the source path `I<N; B; S1; I:=I+1; I<N; ¬B; S2; I:=I+1; I≥N` against the target path `B; I<N; S1; I:=I+1; I<N; S1; I:=I+1; I≥N`: the source executes `S1` then `S2`, while the target executes `S1` twice. Since the templates are unconstrained, an instantiation where `S1` and `S2` change `I` and `B` reads `I` (for example `B = (I < 1)`, `S1 = (I := I + 1)`, `S2 = (I := I + 10)`, with initial `I = 0` and `N = 4`) makes the loops exit with different values of `I`, so the paths are a genuine counterexample. In this instantiation `I ∈ R(B)`, `I ∈ W(S1)`, and `I ∈ W(S2)`, so the precondition below rejects it.

**Encoding and models.** The two paths are encoded into logic [7]: each template statement becomes a conditional write to every variable (a fresh Boolean records whether the statement writes the variable), each template expression becomes a fresh variable, and two occurrences of the same template are forced to produce equal fresh values whenever the values of the variables in their read sets agree [8]. The read/write-set memberships are the existential variables. Every model is a sufficient condition that discharges the counterexample; for instance, `R(B) = ∅` (B is constant) would work, but it is not the weakest. PSyCO negates each model, solves again, and repeats until no models remain; the disjunction of all models is the weakest precondition for this counterexample [9].

**Result.** After processing every counterexample and conjoining the results, PSyCO outputs

```
I ∉ R(B) ∧ W(S1) ∩ R(B) = ∅ ∧ W(S2) ∩ R(B) = ∅
```

which is exactly loop invariance of `B`: the condition must not read the loop counter, and the two bodies must not write any variable the condition reads. The formula is the precondition, and `B`, `S1`, and `S2` belong to the program template, not to the precondition; `R(B)` is the set of variables the instantiated condition may read, and `W(S1)` and `W(S2)` are the sets of variables the instantiated bodies may write, so the precondition only constrains those sets [3]. The evaluation reports the same style of weakest conditions for code hoisting, partial redundancy elimination, loop unrolling, strength reduction, and software pipelining.

## Concepts and terms

**[1] Transformation function and template programs.** A compiler optimization is specified as a transformation function `τ: Src => Tgt` over template programs. Template statements (`S_i`) and template expressions (`E_i`, `B_i`) are placeholders that are instantiated with concrete statements and expressions when the optimization is applied; template expressions are side-effect free and never trap, so error behavior must be modeled explicitly in the control flow. The transformation takes an instantiated source program and returns the instantiated target program.

**[2] Precondition, semantics preservation, and profitability.** A precondition `ψ` is a sufficient condition under which the transformation preserves the semantics: for every instantiation that satisfies `ψ`, the source and target programs behave identically. The optimization also has a profitability heuristic that decides when applying the transformation is worthwhile; it is ignored here because it does not affect correctness.

**[3] Read and write sets.** The precondition language consists of constraints over which variables each template statement or expression may read and write, written `R(t)` and `W(s)`; expressions have empty write sets. Examples are `W(S) ∩ R(E) = ∅` (S may not write anything E reads) and `v ∉ W(S)`. Constraints between two read sets, such as `R(t1) ∩ R(t2) = ∅`, are excluded because the authors know of no optimization that requires them.

**[4] Context variables.** A transformation template does not name all variables that may be in scope at the instantiation site, so each template statement `S_i` is assigned a fresh context variable `c_i` that stands for the variables in scope at the instantiation site that the transformation function does not name, with `c_i ∈ W(S_i)` always. Synthesis runs with at least one more context variable than template statements, which is enough to express every combination of `R ∩ W` and `W ∩ W` emptiness constraints and their negations. Context variables let a precondition say that a statement writes only variables that are otherwise unmentioned.

**[5] Weakest (liberal) precondition.** The algorithm returns the weakest precondition expressible in the read/write-set language, assuming the condition can be expressed there: no weaker constraint over read/write sets accepts more instantiations. Because the prototype's verifier checks partial correctness only, the generated conditions are weakest liberal preconditions: they guarantee that if the source terminates then the target terminates with the same result, but not relative termination. A true weakest precondition would also need counterexamples for termination mismatches.

**[6] Counterexample-guided synthesis.** PSyCO maintains a running precondition `ψ`, initially `true`, and repeatedly calls a black-box verifier. The verifier either proves the transformation correct under `ψ` or returns a counterexample: a source path and a target path that start from the same state and end in different states. The weakest precondition for that counterexample is conjoined into `ψ`, so the same counterexample never appears twice; the precondition language is finite, so the loop terminates. In the prototype the verifier is a simple bounded model checker, chosen over the authors' CORK verifier because it produces counterexamples much faster.

**[7] Path encoding.** A path is a straight-line sequence of statements and Boolean expressions (loops are unrolled by the verifier). Each template statement `s` is encoded as a conditional assignment to every variable `v`: the new value is a fresh variable `f_v` if a fresh Boolean `w(s,v)` is true, and the old value otherwise, where `w(s,v)` means that `s` writes `v`. Each template expression is replaced by a fresh variable. The source and target paths use disjoint variable names, and read/write-set membership is represented by Boolean variables.

**[8] Ackermann-style consistency.** Even though a template's body is unknown, two occurrences of the same template must produce the same result when their inputs agree. For every pair of occurrences of a template `t`, the encoding adds: if every variable in `R(t)` has equal values at the two occurrences, then the fresh output variables are equal. This is the standard Ackermann reduction of uninterpreted functions to first-order logic.

**[9] Model enumeration and generalization.** The encoding is universally quantified over initial values and fresh variables, and existentially quantified over the read/write-set memberships. Each model is a sufficient condition that discharges the counterexample, and the weakest condition is the disjunction of all models; PSyCO collects them by conjoining the negation of each model and re-solving until the formula is unsatisfiable. `GeneralizeWP` drops unnecessary literals using an unsat core, and a set of preferred literals biases solutions toward compact intersection constraints such as `W(S1) ∩ R(B) = ∅`, which also reduces the number of models.

**[10] Loop unswitching.** A loop transformation that hoists a loop-invariant branch out of the loop and duplicates the loop body. It is safe to apply when the branch condition is loop invariant, which the synthesized precondition `I ∉ R(B) ∧ W(S1) ∩ R(B) = ∅ ∧ W(S2) ∩ R(B) = ∅` states for the example.

**[11] PEC comparison.** PEC is an earlier compiler optimization verifier that requires a hand-written precondition as input. Its published precondition for software pipelining requires `V1, V2 ∉ W(S1)`; the condition synthesized by PSyCO does not, so PSyCO's result is strictly weaker and accepts more instantiations. This is the paper's evidence that automatic synthesis can find conditions that experts miss.

**[12] Scope and limitations.** The template language has no heap locations, arrays, or arithmetic preconditions, so the algorithm does not synthesize conditions such as "the loop trip count is even". Templates may still be instantiated with memory operations as long as the read/write-set precondition holds; for example, a template expression may be instantiated with a load whose dependencies are covered by the precondition.

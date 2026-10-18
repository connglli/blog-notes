# TensorRight: Automated Verification of Tensor Graph Rewrites

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:** Jai Arora, Devansh Jain, Tianfan Xu, Charith Mendis (University of Illinois Urbana-Champaign); Sirui Lu (University of Washington); Farzin Houshmand, Praveen Narayanan, Karthik Srinivasa Murthy, Amit Sabne (Google); Phitchaya Mangpo Phothilimthana, Rastislav Bodik (Google DeepMind); Mohsen Lesani (University of California, Santa Cruz)

**Source:** POPL 2025 (distinguished paper)

**Link:** https://doi.org/10.1145/3704865

**Code:** [TensorRight](https://github.com/ADAPT-uiuc/TensorRight); artifact at https://doi.org/10.5281/zenodo.14159871

## Key insight

A rule that must hold for tensors of every rank can be verified by checking finitely many rank instances: for each rank class there is a computable sufficient rank, and a counterexample at any higher rank lowers to one at that rank, so "bounded verification of all instances implies the correctness of the rewrite rule in the unbounded setting".

## Basic idea

Tensor compilers rewrite tensor graphs expecting the rewrites to preserve semantics for tensors of arbitrary rank and size (the rules are rank- and size-polymorphic [1]), but prior automatic checkers verify only fixed ranks and sizes, and prior unbounded proofs are manual Coq developments. TensorRight expresses rules in a DSL [2] whose tensors are built from aggregated axes [3], groups of axes that play the same role and can instantiate to any positive number of named axes, with equal-rank requirements recorded by rank classes [4]. The DSL's denotational semantics [5] define operators as maps from accesses to values, and a bound inference algorithm [6] computes a sufficient rank for each rank class from the number of non-trivial conditions and distinct tensor accesses in the rule. Each rank class is then instantiated at every rank up to its bound, the two sides are symbolically executed under a general access with tensors as uninterpreted functions over symbolic indices and unbounded sizes, and the resulting proof obligations (shape equality, access validity, value equality) are discharged by an SMT solver [7]. Ranks above the bound follow by induction [8]: a counterexample at rank r+1 can be projected onto r axes while preserving the conditions and the access being compared, so it yields a counterexample at rank r. TensorRight represented 121 of the 175 rewrites of XLA's algebraic simplifier and verified 115 of them in the unbounded setting, against 14 represented rules (6 proved) for TASO and 18 (16 proved) for PET; it also proved a generalized version of XLA's rule that folds input padding into a convolution, with the precondition removed.

## Illustrative example: folding two low pads

**The rule.** The source expression pads the low end of every axis twice; the target merges the padding: `pad_low(pad_low(X, 0, p), 0, q)` rewrites to `pad_low(X, 0, p + q)`, with precondition `p ≥ 0 ∧ q ≥ 0`. X has one aggregated axis c, so its shape is the map `{c ↦ s}` where s holds one size per instantiated axis, and p and q are maps of the same form. `pad_low(X, v, m)` [5] returns a tensor whose sizes are those of X plus m, mapping an access A to `X[A − m]` when `A_i ≥ m_i` on every axis and to the padding value v otherwise.

**Rank instantiation.** c belongs to rank class C [4]. Instantiating C at rank 2 turns c into two axes {u, v}: X has shape `{u ↦ 3, v ↦ 4}`, p is `{u ↦ 1, v ↦ 2}`, q is `{u ↦ 2, v ↦ 1}`, and both sides get shape `{u ↦ 6, v ↦ 7}`.

**Symbolic check.** Symbolic execution at a general access A [7] turns the rule into the equality

```text
(if ∀i. A_i ≥ q_i then (if ∀i. A_i − q_i ≥ p_i then X[A − p − q] else 0) else 0)
= (if ∀i. A_i ≥ p_i + q_i then X[A − p − q] else 0)
```

over symbolic indices and sizes, with X an uninterpreted function; the SMT solver discharges it for the rank-1 and rank-2 instances. At the concrete access (4, 6) both sides read X[(1, 3)]; at (1, 0) both produce 0.

**Bound inference.** There are 2 distinct conditions: `∀i. A_i ≥ q_i` and `∀i. A_i ≥ p_i + q_i`. The test `A_i - q_i ≥ p_i` is the second condition in another form. There is 1 distinct access to X, so the sufficient rank is `max(1, 0 + 2) = 2` [6]: only ranks 1 and 2 need checking. The bound is sufficient, not minimal; it treats the conditions as independent.

**Why two ranks cover all ranks.** Each condition is a conjunction with one clause per axis, and the scalar function compares the same access on both sides. Suppose a counterexample existed at rank r+1 with r ≥ 2. A condition that is true stays true on any subset of the axes; a condition that is false stays false if we keep one axis whose clause is false. So each condition pins at most one axis; keeping r axes that include the pinned ones, and restricting the tensor, the sizes, and the padding maps to them, reproduces the mismatch at rank r [8]. Repeating the step lowers any counterexample to rank 2, which has been checked.

**Reductions.** Rules whose expressions contain reduce, dot, or conv use the same scheme after each reduction is represented as an uninterpreted sum, with a user-supplied bijection between the two sides' reduction indices [9].

## Concepts and terms

**[1] Rank and size polymorphism.** A tensor graph rewrite replaces a subgraph with an equivalent one when a precondition holds, written LHS rewrites to RHS under a precondition. A rule is rank- and size-polymorphic when it must preserve semantics for input tensors of every rank (number of axes) and every axis size. Tensors are named-axis objects: an axis has a name, a shape is a map from axis names to sizes, an access is a map from axis names to indices, and the axes are unordered because the supported operators do not depend on physical layout.

**[2] TensorRight DSL.** The specification language for rules, with operators that mirror XLA-HLO: const, iota, expand, binary, pad, slice, dy-slice, dyup-slice, reduce, relabel, concat, dot, conv-base, conv, clamp, select, reverse. Operator attributes (start indices, strides, padding widths, shapes) are maps over the same axes; preconditions are predicates built from per-axis atoms, for example `stride = 1` on every axis. Layout-sensitive operators, notably reshape and bitcast, cannot be expressed.

**[3] Aggregated axis.** A nonempty set of named axes that share one role and are treated uniformly by every operator. A tensor has a finite number of aggregated axes, and the rank of an aggregated axis is the number of named axes it is instantiated to, so one expression stands for all ranks. Shapes, indices, and attributes become aggregated maps: nested maps from an aggregated axis to a map from the named axes in it to integers. Maps are combined element-wise (pointwise over the named axes), and each operator states validity conditions on them. In the example, the padding maps p and q live over the aggregated axis c and are combined axis by axis.

**[4] Rank class (RClass).** A property that ties together aggregated axes which must always be instantiated to the same rank; each axis belongs to exactly one class. An instantiation assigns one concrete rank to each class, and the class also fixes a canonical bijection between the named axes of two axes in the class, which is what lets relabel (the renaming operator that replaces transpose) re-match axes between the sides of a rule.

**[5] Denotational semantics.** The model supports Boolean, mathematical integer, and real-valued elements; it does not establish equivalence under general IEEE floating-point rounding. Every operator is defined as a computable tensor object: given input tensors, its semantics fixes the output shape and the output element at each valid access, plus the side conditions under which the expression is valid; a tensor is the map from valid accesses to elements. Two expressions are equal when they agree at every general access, and validation starts by checking that the sides have the same shape.

**[6] Sufficient rank.** For each rank class c, `InferBound` returns `max(1, Σ n_t² + m_c)`, summing over the tensors with an axis of class c that the rule accesses more than once, where n_t is that tensor's number of distinct accesses and m_c is the number of non-trivial conditions involving c (a fold that is true on every axis is dropped). A tensor accessed once contributes nothing, and a second access is what creates a constraint. The value is a sufficient rank, not the minimum. With several rank classes, every combination of ranks up to the respective bounds must be checked, so the number of bounded instances is the product of the bounds.

**[7] Bounded verification.** After instantiation, ranks are concrete but sizes stay unbounded: each tensor is an uninterpreted function from accesses to values, indices and sizes are symbolic integers, and symbolic execution under a general access yields assertions that the two sides have the same shape (axis names are checked by the engine, axis sizes by the solver), that valid accesses of one side are valid accesses of the other, and that the values are equal. The obligations are conditional: whenever the rule's precondition holds and the left-hand side is valid, the right-hand side must be valid and equal. These assertions go to an SMT solver.

**[8] Counterexample lowering and rank induction.** With k the sufficient rank of a class, the key lemma is that for every r ≥ k, validity at rank r implies validity at rank r+1, proved by contrapositive: from a counterexample at rank r+1, choose a subset of r named axes to keep, restrict the tensor, the sizes, and the attributes to that subset, and set the tensor value at the needed access, which reproduces a counterexample at rank r. Each condition forces at most one axis to be kept, namely the clause that is uniquely false, and each pair of distinct accesses to one tensor forces at most one axis to stay distinct from another, which is where the n² term of [6] comes from. Verifying ranks 1 through k (the basis) and applying the lemma (the induction) proves the rule for every rank; validity at one rank alone says nothing about others, and a rule can hold at rank 1 and fail at rank 2.

**[9] Reduction elements and hints.** reduce, dot, and conv sum over axes whose sizes are unbounded, so their results are kept as uninterpreted reduction elements `Red_⊕(f)` rather than expanded. Two reduction elements are proved equal by exhibiting a bijection between their reduction-index sets (a relation supplied by the user) and proving the paired values equal; the solver checks bijectivity. Of the 17 reduction rules discussed in this verification scheme, 13 can be proved with these hints. For 1, SMT quantifier reasoning blocks the bijection proof; for 3, the index sets have different cardinalities. The paper leaves those remaining set-equivalence arguments to the user, so its reported verified-rule count should not be read as fully automatic end-to-end proof of every reduction rule.

**[10] Implementation and results.** TensorRight is written in Haskell with the Grisette symbolic evaluation engine; queries go to Z3, except one advanced element-wise rule proved with cvc5, with a 10-second timeout per query. Of the 115 verified rules, 110 need a single bounded instance; total verification time ranges from 0.023 s to 23.33 s, and 108 rules finish under a second. Of the 121 represented rules, 118 are implemented and 115 verified; the remaining 6 are 3 timeouts (div and rem) and 3 that need reduction-element rules the system does not have. The artifact is on Zenodo.

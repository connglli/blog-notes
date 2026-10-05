# Refinement E-Graphs

**Author:**
- Philip Zucker<br/>

**Source:** blog "Hey There Buddo!" 2026-10-04

**Link:** https://www.philipzucker.com/refinement_egraph/<br/>

**Code and demo:** prototype [refinement-microegg](https://github.com/philzook58/refinement-microegg), based on Max Willsey's [microegg](https://github.com/mwillsey/microegg); WASM demo at https://www.philipzucker.com/refinement-microegg

## Key insight

A refinement e-graph adds an inequality (`<=`) relation beside the native equality (`=`) of an e-graph, where `t <= s` means that `t` refines `s`; a compiler rewrite that only makes a program more concrete (specification to implementation) can then be stated as a one-way refinement instead of an equality.

## Basic idea

An ordinary e-graph [1] is a union-find plus a hash cons. Its central invariant is congruence [2]: `a = b => f(a) = f(b)` for every function symbol. The blog observes that many compiler rewrites are instead one-way refinements [3], from an abstract specification to a more determined implementation. A refinement e-graph adds `<=` beside `=`, where `t <= s` means that every behavior of `t` is a behavior of `s`, so `t` is the more refined term; a refinement rewrite replaces a term by a refinement of it, and a cycle `a <= b <= a` collapses to equality. The central difference from `=` is that general `<=` is not a congruence: it passes through a function only where the function is monotone in that argument, so each function symbol carries a variance signature [5] (`+`, `-`, or unknown). Where the variance is `+`, `<=` satisfies the analogue of congruence: `a <= b => f(a) <= f(b)`; a preorder compatible with every operation is called a precongruence, and this system has that compatibility only for the monotone declarations. The implementation is an inequality union-find [4] plus a hash cons, with refinement closure [6], refinement e-matching [7], and refinement extraction [9], all keyed by modes [8]; the blog gives a Python toy and a Rust prototype [12].

## Illustrative example: constant folding through an unspecified value

A language can leave a value unspecified, so an implementation may choose any permitted value. A don't-care condition [10] in a circuit is one source of this freedom: an input pattern that never occurs makes the output on that pattern arbitrary. An optimizer uses the freedom to pick the value that makes the program smaller.

Consider the expression `3 + ?`, where `?` stands for an unspecified integer. A term denotes the set of values it may produce:

| Term | Denotation |
| --- | --- |
| integer literal `n` | the singleton set `{n}` |
| `?` | the set of all integers |
| `a + b` | every sum `i + j` over all choices `i` from `[[a]]` and `j` from `[[b]]` |
| `t <= s` | `[[t]]` is a subset of `[[s]]` [3] |

**Initial e-graph.** The e-graph holds the term `3 + ?`, the refinement fact `0 <= ?` (zero is one of the values `?` may take), the ground equality `3 + 0 = 3`, and the declaration that `+` is monotone in its second argument [5].

**Saturation.** Refinement closure [6] applies the declaration to the fact and derives `3 + 0 <= 3 + ?`; the equality merges `3 + 0` with `3`. Together they give `3 <= 3 + ?`.

**Extraction.** Extraction [9] looks for the simplest term below `3 + ?` and returns `3`. The optimizer chose `0` for the unspecified value and folded the addition away; returning `3` is sound because `3` was already a possible result of `3 + ?`.

**Refinement versus equality.** Equating `?` with `0` would force every occurrence of `?` to be `0`. The inequality keeps all integers available, and closure creates one enode per choice of refinement, so each occurrence can choose independently.

## Concepts and terms

**[1] E-graph.** A data structure that represents many terms and the equalities between them at once. It combines a union-find, which maps each eclass id to a canonical representative, with a hash cons, which maps each function application (an enode such as `f(e1, e2)`) to the eclass it belongs to. When two classes merge, every enode whose children changed must be re-canonicalized and possibly merged; this rebuilding restores congruence closure.

**[2] Congruence.** A relation `R` is compatible with a set of function symbols when `a R b` implies `f(..., a, ...) R f(..., b, ...)` for every symbol and argument position. A congruence is an equivalence relation with this property, and a precongruence is a preorder with it. Equality is a congruence for every function: applying a function to equal inputs gives equal outputs. Refinement `<=` is not a congruence in general. It is preserved only by functions monotone in the argument, reversed by anti-monotone functions, and undetermined for unknown ones; the variance signature records which case holds, and `<=` is a precongruence only for the symbols and arguments declared monotone. For example, set difference `A \ B` is monotone in `A` and anti-monotone in `B`. Under a semantics that lifts every constructor pointwise over sets of behaviors, every constructor is monotone, but the e-graph does not know the intended semantics, so the variance is declared.

**[3] Refinement.** A preorder `<=` on terms, read `t <= s` as "t refines s". The blog's semantics is behavior containment: a term denotes a set of possible behaviors, and `t <= s` holds when every behavior of `t` is also a behavior of `s`. Refinement removes possible behaviors, so the more refined term is the more defined and more deterministic one. The relation is reflexive and transitive, and it is antisymmetric on classes: if `a <= b` and `b <= a` then `a` and `b` are equal. This containment order has the same shape as the refinement relation used to justify compiler transformations, where the transformed program may have fewer behaviors than the source. The blog's model is total: it has no undefined-behavior element and no separate `undef` or `poison` value.

**[4] Inequality union-find.** The extension of a union-find that tracks `<=` beside `=`. The blog's interface:

```python
def add_le(a, b): ...   # record a <= b
def is_le(a, b): ...    # test a <= b
def all_le(a): ...      # all classes x with a <= x
def all_ge(a): ...      # all classes x with x <= a
```

Equality still uses `union`, `find`, and `is_eq`. Each class stores an upper set and a lower set of class ids; the sets stay sparse and their transitive closure is computed on demand by graph search.

**[5] Variance (monotonicity) signature.** A property of a function symbol that says how it interacts with `<=` in each argument. An argument is monotone or covariant (`+`) when `a <= b` implies `f(..., a, ...) <= f(..., b, ...)`, anti-monotone or contravariant (`-`) when `a <= b` implies `f(..., a, ...) >= f(..., b, ...)`, and unknown or invariant when neither inference holds. Functions always respect equality, whatever their variance.

**[6] Refinement closure.** The analogue of congruence closure for `<=`. Congruence closure applies `a = b and c = d implies diff(a, c) = diff(b, d)`; refinement closure applies `a <= b and c >= d implies diff(a, c) <= diff(b, d)`, with the direction of each argument chosen by its variance. The materializing version adds enodes for the newly related terms; the weak version only connects enodes that already exist. The blog notes that the materializing version is not obviously terminating, and that full ground refinement closure may be undecidable, which puts it in the same category as rewrite rules.

**[7] Refinement e-matching.** Matching a pattern against the e-graph while allowing `<=` steps. The problem is a constraint such as `?p <= t` or `t <= ?p`. Each argument of a function application inherits a constraint whose direction follows the argument's variance, so an anti-monotone argument flips the direction. The matcher may walk `<=` edges between classes while searching, and it can flatten a pattern into a chain in which every argument position is linked by an explicit `<=` with the direction set by variance.

**[8] Mode.** A tag that records the relation currently being solved: equality (`EQ`), below (`LE`), or above (`GE`). Matching and extraction both use modes. Descending into a function argument transforms the mode: a monotone argument keeps it, an anti-monotone argument flips it, and an unknown argument forces equality.

**[9] Refinement extraction.** Choosing a concrete term for a goal class, as in ordinary extraction, but the goal may be `?extract <= t` or `?extract >= t` instead of `?extract = t`. The extractor walks the classes related to the goal in the given mode, extracts each argument in the mode induced by the argument's variance, and keeps the best term according to a cost. The blog suggests preferring the most refined term and breaking ties by size; its toy implementation scores candidates by term size.

**[10] Don't care.** A condition whose output value does not matter because the input pattern cannot occur. Logic minimization, for example with Karnaugh maps, assigns don't-care outputs 0 or 1 to shrink the circuit. The unspecified `?` in the example is the same kind of freedom: the optimizer may choose any permitted value, here `0`.

**[11] Refinement rules.** The prototype asserts facts with `(ge a b)` and `(le a b)`, and states quantified refinements with `rewrite-le` and `rewrite-ge`: `(rewrite-le lhs rhs)` means `forall ?a, lhs(?a) <= rhs(?a)`. Because the rule is an inequality, the matcher does not need the left-hand side to occur as an equal subterm: from any term `?t` with `?t <= subst(lhs)` the rule yields `?t <= subst(rhs)`.

**[12] Prototype.** The blog's Python toy implements the inequality union-find, `le_cong_step` and `le_cong_step_weak` for refinement closure, and mode-keyed `ematch_rec` and `extract`. The Rust prototype refinement-microegg is built on microegg. The author lists possible extensions: special-case common orders (total, tree-like), proof-relevant orders such as an offset union-find for integers, and combining refinement with lambda/lifting e-graphs.

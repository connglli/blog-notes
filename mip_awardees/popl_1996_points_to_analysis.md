# Points-to analysis in almost linear time

**Summary by:** GPT 6 Astra

**Author:** Bjarne Steensgaard

**Source:** POPL 1996; SIGPLAN Most Influential POPL Paper Award 2006.

**Link:** https://doi.org/10.1145/237721.237727

## Key insight

Represent possible pointer targets with shared equivalence classes instead of independently growing sets. Merging classes loses precision but makes an interprocedural analysis almost linear in program size.

## Basic idea

A points-to analysis [1] approximates which locations a pointer may reference. This analysis is flow-insensitive [2] and describes storage using recursive types whose components stand for possible data and function targets. Constraints from assignments, address-taking, loads, stores, and calls are solved by unification [3] with a union-find structure [4]. Conditional joins [5] avoid merging components merely because a nonpointer value flows between variables.

## Illustrative example

**Setup.** Consider these C statements, with distinct integer objects:

```c
int left = 0, right = 0;
int *p = &left;
int *q = &right;
p = q;
```

A flow-sensitive analysis could say that immediately before the last assignment `p` points only to `left`, and immediately afterward only to `right`. Here we instead seek one approximation valid throughout the program.

**Constraints.** Start with separate abstract locations for `left` and `right`. The two address-taking expressions establish target components for `p` and `q`. The assignment `p = q` requires compatible pointer-content descriptions. Since `q` has a pointer-valued component, the solver joins the relevant components.

The merged target class contains both `left` and `right`. Queries for either `p` or `q` can consequently report both objects. The additional target reported for `q` is an intentional approximation: this implementation does not retain an asymmetric subset relation that would let `q` stay more precise than `p`.

**Solver mechanics.** Each component has an equivalence-class representative, a type descriptor, and pending joins. Joining two representatives also unifies any structured descriptors they already contain. If a source component is still bottom, meaning that it contributes no pointer information yet, a conditional join is postponed. When pointer information reaches that component, its pending joins are activated. Thus an ordinary integer copy need not immediately collapse unrelated pointer classes.

A rough implementation must merge recursively referenced components as well as their outer representatives. Union-find alone, without these type constraints and deferred joins, is not the complete algorithm.

## Concepts and terms

**[1] Points-to analysis.** A static approximation of possible pointer targets. Soundness requires retaining every target that an execution may use; an extra target is a false positive, not an omitted behavior.

**[2] Flow-insensitive analysis.** All statements constrain a single result, independent of execution order. The paper also shares information across calls rather than distinguishing every calling context.

**[3] Unification.** Making type descriptions equal by merging their variables and corresponding components. Recursive descriptions allow cycles in the inferred storage graph.

**[4] Union-find.** A data structure maintaining disjoint equivalence classes with efficient representative lookup and merging. The bounded graph representation and near-constant amortized operations support the paper's complexity bound.

**[5] Conditional join.** A deferred equality obligation activated when the source component becomes non-bottom. It distinguishes absence of pointer information from an already established pointer relationship.


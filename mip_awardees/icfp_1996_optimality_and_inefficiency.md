# Optimality and inefficiency: What isn't a cost model of the lambda calculus?

**Summary by:** GPT 6 Astra

**Author:** Julia L. Lawall and Harry G. Mairson

**Source:** ICFP 1996; SIGPLAN Most Influential ICFP Paper Award 2006.

**Link:** https://doi.org/10.1145/232627.232639

## Key insight

Avoiding duplicated reductions does not imply efficient execution. Sharing graphs also perform bookkeeping, and a complexity measure that ignores that work or intermediate representation size can misrepresent the real cost.

## Basic idea

Optimal reduction [1] groups related beta-reductions [2] so their work can be shared. Implementations use sharing graphs [3] with fan nodes and bookkeeping that tracks which copies belong together. The paper constructs families for which this bookkeeping is exponentially larger than the counted useful interactions, and separately critiques a cost model that neglects intermediate term size. Its conclusion concerns these cost models and implementations, not a theorem that all sharing or all functional evaluation is inefficient.

## Illustrative example

**A size-sensitive calculation.** Let `duplicate = lambda x. branch x x`, where `branch` and `leaf` are free symbols with no reduction rules. Apply `duplicate` three times to `leaf`, reducing the innermost application first.

The successive arguments are `leaf`, `branch leaf leaf`, and `branch (branch leaf leaf) (branch leaf leaf)`. The final result has eight leaf occurrences. For `n` nested applications there are only `n` chosen beta-contractions in this inside-out sequence, but the fully expanded result contains `2^n` leaves.

**Representation matters.** A tree implementation physically copies a growing argument at every substitution. A graph implementation can instead create a new branch node whose two outgoing edges point to the same existing graph. Its compact representation of this particular result grows only linearly. Printing the complete unshared tree still requires work proportional to its output size.

This is an original illustration of the intermediate-size issue, not the paper's stronger exponential-bookkeeping construction.

**Accounting for sharing.** When shared function bodies are applied to different arguments, an optimal graph evaluator must also preserve which occurrence of a bound variable belongs to which application. Fan interactions and scope-related bookkeeping maintain that information. Counting only beta-like interactions misses these additional steps.

For an experimental implementation, record separate counters for beta interactions, fan interactions, bookkeeping rewrites, graph size, and output expansion. Two evaluators can have the same first counter and very different total running times. A justified cost model must relate the charged operations and representation sizes to an implementable machine model.

## Concepts and terms

**[1] Optimal reduction.** A technical notion based on sharing families of related reductions. It optimizes that notion of duplicated work, not elapsed time over all possible implementations.

**[2] Beta-reduction.** Replacing an application `(lambda x. body) argument` with the body after capture-avoiding substitution of the argument for `x`. Its abstract step count need not equal the cost of physically performing substitution.

**[3] Sharing graph.** A graph representation in which multiple uses can refer to common structure. Fans represent controlled sharing or duplication; bookkeeping distinguishes compatible sharing histories and binding contexts. Reading the graph back as an ordinary term can itself expand its size.


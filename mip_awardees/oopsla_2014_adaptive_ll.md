# Adaptive LL(*) Parsing: The Power of Dynamic Analysis

**Summary by:** GPT 6 Astra

**Author:** Terence Parr, Sam Harwell, Kathleen Fisher

**Source:** OOPSLA 2014; SIGPLAN Most Influential OOPSLA Paper Award, 2024

**Link:** https://doi.org/10.1145/2660193.2660202

**Code:** [ANTLR 4](https://github.com/antlr/antlr4)

## Key insight

Resolve grammar decisions using the actual remaining input, and cache those decisions, instead of trying to precompute sufficient lookahead for every possible input.

## Basic idea

ALL(*) equips a recursive-descent parser [1] with adaptive prediction. When a choice is unknown, it simulates alternative paths through an augmented transition network [2], eliminating alternatives inconsistent with lookahead. A deterministic automaton [3] caches reusable prediction work; context-sensitive conflicts can require full calling context [4]. Prediction does not execute ordinary side-effecting parser actions, and the core algorithm's grammar guarantee excludes left recursion unless it has been rewritten.

## Illustrative example

**Grammar.** A statement is either a parenthesized expression followed by `:` and a name, or a parenthesized expression followed by `;`. Expressions can contain arbitrarily nested parentheses. Thus no fixed small number of tokens always reaches the punctuation distinguishing the alternatives.

**First encounter.** On input `((item)):label`, start prediction at the statement choice. Both alternatives remain viable through the nested expression. The colon eliminates the semicolon alternative. Resume ordinary parsing with the first alternative; only that actual parse performs its associated semantic actions.

**Cache.** Record transitions for the encountered token sequence in the decision automaton. A later compatible lookahead sequence can reuse those transitions instead of rebuilding every simulated configuration. An unfamiliar nesting pattern extends the cache as needed; the cache is not a finite precomputation of every possible nested expression.

**Context and ambiguity.** A local prediction that merges alternatives can retry with the enclosing parser call context, because what may legally follow a rule depends on its caller. If alternatives genuinely remain ambiguous, the strategy resolves according to grammar ordering rather than silently promising an unambiguous grammar. Direct-left-recursive expression syntax is supported by ANTLR through rewriting; that does not mean arbitrary indirect left recursion is handled by the core predictor. The paper's practical near-linear measurements are not a worst-case linear-time theorem.

## Concepts and terms

**[1] Recursive-descent parser.** A top-down parser whose routines correspond to grammar rules.

**[2] Augmented transition network.** A graph representation of grammar alternatives and rule calls that supports simulated lookahead paths.

**[3] Deterministic automaton.** A state machine with at most one transition per token from a state, used here to reuse prediction results.

**[4] Calling context.** The active sequence of enclosing rule invocations, which constrains where a rule can return.

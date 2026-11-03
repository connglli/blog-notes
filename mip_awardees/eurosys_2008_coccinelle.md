# Documenting and Automating Collateral Evolutions in Linux Device Drivers

**Summary by:** GPT 6 Astra

**Author:** Yoann Padioleau, Julia L. Lawall, René Rydhof Hansen, Gilles Muller

**Source:** EuroSys 2008; EuroSys Test-of-Time Award 2018

**Link:** https://doi.org/10.1145/1352592.1352618

**Code:** [Coccinelle](https://github.com/coccinelle/coccinelle)

**Documentation:** [Semantic patch documentation](https://coccinelle.gitlabpages.inria.fr/website/documentation.html)

## Key insight

An API migration is a transformation pattern, not a collection of textual substitutions. Describe its required code and control-flow context once, then match that pattern across clients with different names, formatting, and branch structure.

## Basic idea

Coccinelle expresses collateral evolution [1] through semantic patches written in SmPL [2]. Metavariables bind program fragments, while control-flow matching [3] recognizes related operations even when intervening statements or branches differ. Isomorphisms [4] cover selected equivalent spellings. The engine translates patch conditions into temporal-logic queries, matches them against the program, and edits the associated source locations; it applies a supplied migration rule rather than proving the new API's correctness.

## Illustrative example

**Define the API change.** In a hypothetical driver API, `acquire_item(key)` returns an item whose reference must later be released. Its replacement, `borrow_item(key)`, has the same lookup result but returns a reference kept alive by the caller's enclosing framework operation. The migration replaces acquisition with borrowing and removes matching releases, assuming no reference escapes that enclosing operation.

**Describe one pattern.** A driver assigns the lookup result to `entry`, checks for failure, then takes one of two branches. Each successful branch calls `release_item(entry)` before returning. The semantic patch binds the result variable and key expression, matches the lookup and its control-flow context, and specifies removal of the corresponding releases.

**Match paths, not line ranges.** A patch need not list both branch bodies separately. A control-flow pattern can relate the lookup to the release on each path while permitting intervening statements. It must reject cases violating its conditions, such as reassignment of the bound variable or an unmatched lifetime path. Another driver can use the name `record` and a different number of branches while satisfying the same rule.

**Handle surface variation.** An applicable isomorphism can recognize a null test written as `entry == NULL` or `!entry`. The tool retains the original source presentation outside edited fragments. Partial matches expose cases needing examination instead of establishing that every driver has been migrated correctly.

## Concepts and terms

**[1] Collateral evolution.** An interface changes, requiring corresponding changes in code that uses it. The library edit and the client edit are separate responsibilities. A reusable semantic patch records the intended client-side migration, including the context needed to decide whether it applies.

**[2] SmPL and metavariables.** SmPL uses patch-like removal and insertion notation with declarations for placeholders such as identifiers, expressions, and types. Repeated occurrences of a bound metavariable must refer to the same matched fragment. The author specifies the migration; the tool does not infer arbitrary replacement semantics from the new library.

**[3] Control-flow matching.** A control-flow graph represents possible transfers between statements. Coccinelle translates semantic-patch patterns into computational tree logic conditions and uses model checking to find matching paths and bindings. Ellipses describe intervening control flow, subject to pattern restrictions, rather than unrestricted textual gaps. Matching is an approximation of execution behavior, not a general alias or functional-correctness proof.

**[4] Isomorphism.** An explicitly supported relation between alternative code forms that should match the same pattern. It avoids requiring a separate patch for every equivalent spelling. Only the declared equivalences and supported analyses are available; semantic similarity alone does not guarantee a match.

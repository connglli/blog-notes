# Verifying Peephole Rewriting in SSA Compiler IRs

**Summary by:** GPT 6 Astra

**Author:** Siddharth Bhat, Alex Keizer, Chris Hughes, Andrés Goens, Tobias Grosser

**Source:** ITP 2024, LIPIcs 309, article 9

**Link:** https://doi.org/10.4230/LIPIcs.ITP.2024.9

**Code and demo:** [Lean-MLIR, paper version](https://github.com/opencompl/lean-mlir/tree/ITP24), [playground](https://lean-mlir.grosser.es/)

## Key insight

Separate proving a local rewrite from proving that matching and applying it inside an SSA program is correct. Lean-MLIR supplies a verified, dialect-independent rewriting framework, leaving the user to define the dialect's semantics and prove the local mathematical identity.

## Basic idea

Domain-specific compiler IRs need proofs at their own abstraction level, not only proofs about lowered machine arithmetic. Lean-MLIR represents SSA dialects [1] with intrinsically well-typed syntax [2] and user-supplied denotational semantics [3], including nested regions for structured control flow. A peephole rewrite packages two fragments and a proof relating their meanings; tactics simplify the SSA machinery into an ordinary mathematical goal [4]. A verified rewriter [5] matches along definition-use dependencies and substitutes the replacement inside a larger program, even when unrelated operations intervene.

## Illustrative example

**Define a dialect.** Use a tiny pure dialect with mathematical integers and two operations: `add : Int × Int -> Int` and `mul : Int × Int -> Int`. Their meanings are ordinary integer addition and multiplication. The following executable Python is a rough rendering of an SSA block, with one assignment per variable:

```python
def fragment(u: int, v: int, w: int) -> int:
    left = u * v
    keep = left + u
    right = u * w
    total = left + right
    answer = total + keep
    return answer
```

The input context contains three integer variables. Each assignment extends it with another integer. An operation argument refers to an existing context entry of the required type, so an integer addition cannot accidentally receive a Boolean or an out-of-scope name.

**Prove the local rule.** The pattern is `a*b + a*c`; the replacement is `a*(b+c)`. Both take three integers and return one integer. After unfolding the dialect's operation meanings and simplifying variable lookups, the local proof obligation is simply `forall a b c : Int, a*b + a*c = a*(b+c)`. Integer distributivity proves it. This is a mathematical-integer example, not a floating-point rewrite.

**Match the dependencies.** At `total`, the matcher follows its two operands back to `left` and `right`. It finds the two multiplications despite the intervening assignment to `keep`, and binds the pattern variables as `a -> u`, `b -> v`, and `c -> w`. No assumption that the matched instructions are consecutive is needed.

**Insert and redirect.** Split the block after the definition of `total`. Keep the prefix, insert `new_sum = v + w` and `new_total = u * new_sum`, and change the suffix to use `new_total` wherever it used `total`. For `u = 2`, `v = 3`, and `w = 4`, both blocks return 22. The local identity and the rewriter's theorem establish the same result for every integer input, not just this test.

**Clean up without deleting shared work.** Dead-code elimination [6] can remove the unused original `total` and `right`. It must retain `left`, because `keep` still uses it. The rewrite theorem does not justify deleting every instruction that participated in the match.

**Use the rule inside a region.** The same block can be the body of a conditional region: its block arguments receive `u`, `v`, and `w`, and it returns `answer` to the enclosing conditional. The rewriter can descend into that region while leaving the other branch unchanged. This is rewriting a known region body, not matching an arbitrary region as a pattern variable [7].

## Concepts and terms

**[1] Dialect and SSA.** An intermediate representation (IR) describes a program between compilation stages. A dialect supplies its own types and operations. In static single assignment (SSA), each value has one definition, and uses identify that definition directly. Lean-MLIR is parameterized by the dialect rather than fixing one instruction set or numerical domain.

**[2] Intrinsic well-typing.** A context is a list of available variable types. A variable reference includes an index and evidence that the indexed entry has the required type. Operation signatures constrain their operands and result. `Expr Γ t` represents a single operation in context `Γ` returning type `t`; `Com Γ t` represents a sequence of bindings ending in a return. A binding extends the context for the remaining commands. Ill-typed programs cannot inhabit these types, though raw parsed MLIR may fail conversion into them.

**[3] Denotation and regions.** A valuation assigns values to a context's variables. The user maps each IR type to a Lean type and each operation to a function on values of those types. The framework extends those definitions to whole blocks by evaluating each binding and extending the valuation. A region is a nested block with its own typed inputs and return; its denotation is supplied as a function to the enclosing operation. A conditional chooses a region function, while a bounded loop repeatedly applies one. The pure semantics uses terminating Lean functions, not arbitrary nonterminating control-flow graphs.

**[4] Local rewrite proof and automation.** A rewrite stores a left-hand fragment, a right-hand fragment with the same input context and return type, and a proof that their denotations agree for every input valuation. `simp_peephole` unfolds the framework's evaluation and context operations, replaces lookups with named Lean variables, and leaves a domain-level goal. Arithmetic tactics or an explicit proof finish that goal. Tactics produce proofs checked by Lean; simplifying away SSA does not itself prove the remaining identity.

**[5] Verified matching and replacement.** The rewriter uses a zipper: a prefix of already-bound variables and a suffix to continue executing. It matches the pattern backward from a selected result, obtains a type-correct substitution for the pattern's free variables, inserts the substituted replacement, and redirects uses in the suffix to the replacement's result. The framework proves that splitting, inserting, substituting, and reconnecting preserve the intended denotation. A traversal bound limits rewriting attempts; it is not a bound on the runtime inputs covered by a rewrite proof.

**[6] Dead-code elimination.** Remove a binding only when its result is unused and deleting its computation is permitted. For pure operations this reduces to tracking uses and updating the typed context. Lean-MLIR supplies a separately verified implementation, so removing obsolete matched instructions does not require extending each local rewrite proof.

**[7] Scope and trust.** The theorem applies to the formalized dialect and its semantics, not automatically to an external MLIR implementation. The effectful extension permits rewrites of operations declared pure inside an effectful context; it does not justify arbitrary effect reordering. Regions are compared structurally during pattern matching, although the rewriter can recurse into their bodies; free region variables are unsupported. The paper's LLVM case study supports proofs over arbitrary bitwidths, but omits `nsw` and `nuw` and collapses poison and immediate UB into one optional-value representation. Rewrites involving division or remainder therefore require an additional manual check that target UB is not introduced. This is not a complete formalization of LLVM semantics.

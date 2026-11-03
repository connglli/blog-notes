# The Spoofax Language Workbench: Rules for Declarative Specification of Languages and IDEs

**Summary by:** GPT 6 Astra

**Author:** Lennart C. L. Kats, Eelco Visser

**Source:** OOPSLA 2010; SIGPLAN Most Influential OOPSLA Paper Award, 2020

**Link:** https://doi.org/10.1145/1932682.1869497

**Code:** [Spoofax](https://github.com/metaborg/spoofax)

## Key insight

A compiler and an editor should reuse the same language analyses, so navigation, error checking, and code generation agree about what a program means.

## Basic idea

Spoofax combines declarative syntax definitions [1], rewrite rules [2], and configurable editor services. Name analysis [3] records declaration relationships that type checking, reference navigation, and completion can share. Language-independent editor components connect these specifications to the development environment. The paper's implementation uses SDF and Stratego; defining syntax alone does not automatically supply a language's semantic rules.

## Illustrative example

**Language.** Define a small configuration language with integer declarations and additions: `let width = 3; let area = width + 2;`. A grammar maps declarations, identifiers, literals, and addition into corresponding syntax-tree constructors. The example notation is illustrative, not copied Spoofax syntax.

**Analysis.** On the declaration of `width`, create a binding from that name in its scope to its declaration node. Resolve the occurrence inside `area` through that binding. Infer integer types for the literal and reference, then require both addition operands to have integer type. If the reference is instead spelled `widht`, emit an unresolved-name error associated with that occurrence.

**Reuse.** A "go to definition" service follows the same binding from the occurrence of `width` to its declaration. A completion service at `wi` proposes visible names, including `width`, while using the syntax context to avoid proposing an entire declaration where an expression is needed. Code generation uses the resolved tree rather than performing a separate incompatible name lookup.

**Editing.** An unfinished expression such as `width +` needs a recoverable syntax representation so services remain useful during typing. Source-origin information connects tree nodes and diagnostics to the original text. If a nested scope shadows `width`, the binding analysis distinguishes the two declarations, and every consumer of that analysis sees the same distinction. None of these services should infer bindings from textual name equality alone.

## Concepts and terms

**[1] Declarative syntax definition.** A grammar specifying source forms and their abstract structure, used to generate parsing support.

**[2] Rewrite rule.** A pattern-directed transformation or query on syntax trees; Stratego supplies strategies controlling application and scoped dynamic rules for contextual information.

**[3] Name analysis.** Determining which declaration each identifier occurrence denotes under the language's scope rules.

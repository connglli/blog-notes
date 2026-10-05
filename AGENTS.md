# AGENTS.md

## What this project is

This directory holds short, self-contained summaries of papers and blog posts. One markdown file per work, named after the work.

## Before writing

Think critically and carefully before writing anything down. Completeness is not the goal: leaving out a less important, trivial, or simple part is fine. Soundness is the goal: do not write anything wrong. Check every claim against the source instead of relying on memory, and prefer the source's own definitions and its running example.

## Structure of a summary

Every summary contains, in order:

- The title as a level-1 heading, followed by the author, the link to the work, and links to its code or demos when the work names them.
- `## Key insight`: one or two sentences with the central idea. A short quote from the work works well here.
- `## Basic idea`: the core idea in plain language, including the minimum background needed to follow it.
- `## Illustrative example`: one concrete example, written from scratch rather than copied from the work. Rebuild the work's running example smaller and more self-contained when possible, with our own names and only the details the basic idea needs. Every concept that the basic idea introduces and that a reader may not already know must show up in the example, so that a reader can follow the example without reading the work.
- `## Concepts and terms`: a complete explanation, formal or informal, of every non-obvious concept and term used anywhere in the summary. A concept that the basic idea introduces but does not fully explain is explained here and appears in the example.

Rules for the summary:

- It must be self-contained. A reader who has not read the work should understand it.
- It does not need to cover everything; skip details that do not help a quick understanding.
- The reader should be able to do a rough implementation from the summary alone. State semantics and mechanics, not only motivation.
- Do not paste the work's examples, code, or tables. Rewrite and simplify them: the example is ours, uses our names, and contains only what the basic idea needs.
- Number the entries in `## Concepts and terms` as `[1]`, `[2]`, and so on. Cite a concept as `[n]` at its first occurrence in `## Basic idea` or `## Illustrative example`, as in `congruence [2]`.
- When the work has distinct algorithm phases, separate them inside `## Illustrative example` with small titles in the form `**Title.**`, for example `**Saturation.**` and `**Extraction.**`, not with `###` headings.

## Writing rules

Write plain English in plain words. Specialized domain terms are allowed and often necessary, but explain them in `## Concepts and terms`.

- Write for a reader who has not read the source.
- Prefer plain English to metaphor.
- State the contract: what holds, under which conditions, and what happens when it does not.
- One idea per paragraph.
- Numbers carry their provenance; a percentage states its denominator.
- Keep prose concise. Do not append clauses everywhere.
- Avoid puffery ("a testament to", "a pivotal moment"), dangling commentary ("highlighting", "reflecting", "showcasing"), promotional verbs ("boasts", "features", "leverages", "ensures"), copula inflation ("serves as" where "is" is meant), negative parallelism ("not only X but also Y"), three adjectives chosen for rhythm, false ranges ("from X to Y" that spans nothing), elegant variation (repeat the name instead of finding a synonym), weasel attribution ("it is generally accepted"), and closing paragraphs that speculate about future work.
- Avoid temporal narration ("previously", "now", "no longer") and status annotations ("implemented", "planned", "future work"). State what holds.
- Do not state the same fact in two places. One fact, one home.
- Do not narrate the reasoning that led to a claim; state the claim.
- Do not keep a hand-maintained inventory that the source already carries; name where it lives.

## Formatting

- One physical line per paragraph; use editor soft-wrap.
- Sentence case headings. Plain `*` bullets. No emoji. Straight quotes and apostrophes.
- Em and en dashes disallowed; commas and parentheses do the same work.
- Code blocks carry real code from the work or from a rough implementation, and have to be true.
- Emphasis marks the clause that matters. Bold and caps everywhere mean nothing stands out.

## The slop checklist

Read the summary for temporal words, a distinctive phrase from a rule stated twice, doubled emphasis, numbers without provenance, paragraph walls, a list of one, and a table of two rows. Then read once more for a paragraph with two subjects and for a passage that explains how you got there instead of what holds.

## Length and quality

When updating a document, prioritize rewriting and refining existing content rather than appending new text. Add material only when necessary, and maintain the summary's concision, clarity, and overall quality.

Section limits:

- Key insight: one or two sentences.
- Basic idea: one paragraph, at most six sentences. State the problem, the mechanism, and the names of the main parts; leave details to the example and the concepts section.
- Illustrative example: one example, worked once.
- Concepts and terms: one entry per concept, each as short as a complete explanation allows. Do not restate the basic idea.

Before finishing, delete any sentence that repeats another section or that does not help a reader understand the work or do a rough implementation.
# Automating string processing in spreadsheets using input-output examples

**Summary by:** GPT 6 Astra

**Author:** Sumit Gulwani

**Source:** POPL 2011; SIGPLAN Most Influential POPL Paper Award 2021.

**Link:** https://doi.org/10.1145/1926385.1926423

**Demo:** [Flash Fill demos, the Excel implementation](https://www.microsoft.com/en-us/research/project/flash-fill-excel-feature-office-2013/)

## Key insight

A few examples usually admit many string transformations, so retain a compact set of consistent programs instead of committing immediately. Intersecting these sets across examples removes incompatible interpretations.

## Basic idea

The paper defines a string-expression language [1] using constants, substring extraction, concatenation, and restricted conditionals and loops. Substring boundaries can be described by token-based positions [2], allowing a program to generalize beyond fixed character offsets. A directed acyclic graph [3] compactly represents alternative decompositions of an example's output and the expressions that produce them. Synthesis intersects these representations across examples, then ranks surviving programs [4] and can request examples that distinguish ambiguous results.

## Illustrative example

**Examples.** A user supplies `"Elm-52" -> "52/Elm"` and `"Birch-9" -> "9/Birch"`. The intended transformation swaps the two hyphen-separated fields and inserts a slash.

From the first example alone, many candidates fit: extract the final two characters, extract the first digit sequence, or output the constant `"52"`. For the word, either a fixed three-character slice or extraction before the hyphen also fits.

**Compact representation.** Create output-position nodes for `"52/Elm"`. An edge from one position to a later position carries all supported expressions that produce that output segment. A path spelling the full output can select a number-extraction edge, a constant-slash edge, and a word-extraction edge. Sharing nodes and expression sets avoids enumerating every combination as a separate program.

**Intersection.** The second example rejects the constant `"52"` and the fixed three-character word slice. A token-relative program remains: take the text after the hyphen, concatenate `"/"`, then take the text before the hyphen. Its structure is shared across the two examples even though the actual substring indices differ.

Applying that program to `"Cedar-804"` produces `"804/Cedar"`. This new row is an illustration of the selected rule, not evidence that the rule is uniquely determined by the two examples.

If the data can contain several hyphens, taking the first or last matching delimiter may remain ambiguous. Ranking expresses preferences among consistent candidates; asking for a discriminating example supplies information that ranking alone does not have.

## Concepts and terms

**[1] String-expression language.** A restricted language defining the candidate programs the synthesizer can represent. Failure to find a program may reflect either inconsistent examples or limits of that language.

**[2] Token-based position.** A string boundary described by matching token patterns on its left and right and selecting an occurrence. Tokens include classes such as letters, digits, and punctuation.

**[3] Directed acyclic graph.** A graph whose paths cannot cycle. Here a source-to-target path represents a concatenation, while labels represent sets of expressions for its segments. Intersection retains expressions consistent with multiple examples.

**[4] Program ranking.** A preference ordering used to choose among programs that agree with the examples. Agreement establishes consistency with the given rows, not correctness on every unseen row.


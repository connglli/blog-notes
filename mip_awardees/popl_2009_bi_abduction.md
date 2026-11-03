# Compositional shape analysis by means of bi-abduction

**Summary by:** GPT 6 Astra

**Author:** Cristiano Calcagno, Dino Distefano, Peter W. O'Hearn, and Hongseok Yang

**Source:** POPL 2009; SIGPLAN Most Influential POPL Paper Award 2019.

**Link:** https://doi.org/10.1145/1480881.1480917

**Code:** [Infer, the successor project](https://github.com/facebook/infer)

**Documentation:** [Infer's separation logic and bi-abduction](https://fbinfer.com/docs/separation-logic-and-bi-abduction/)

## Key insight

To apply a procedure's specification, infer both what memory is missing and what memory is irrelevant. This lets an analysis discover a procedure's required inputs without knowing all its callers.

## Basic idea

The analysis describes pointer structures with separation-logic assertions [1] and summarizes procedures by preconditions and postconditions [2]. At a call, bi-abduction [3] solves `A * M entails P * F`, where `A` is the caller's known state and `P` is the callee's required state. The missing part `M` becomes an additional requirement, while the frame `F` is preserved across the call. Summaries compose bottom-up, and candidate preconditions are checked rather than treating every abduced hypothesis as automatically valid.

## Illustrative example

**Setup.** A procedure `increment(p)` requires an allocated cell `p -> n` and returns with `p -> n+1`. A caller has established only `q -> 8`, for a cell it intends to preserve, and calls `increment(p)`.

There is insufficient information to justify dereferencing `p`. The analysis does not assume that every address is allocated.

**Bi-abduction.** Let `A = q -> 8` and `P = p -> n`. One consistent solution is `M = p -> n` and `F = q -> 8`, with the cells disjoint. Then `A * M` entails `P * F`, just by rearranging the two separated cells.

Applying the callee summary replaces `P` by its postcondition and preserves `F`. The resulting symbolic state is `p -> n+1 * q -> 8`.

**Procedure summary.** If no earlier caller operation conflicts with the added assumption, the caller can be summarized with precondition `p -> n * q -> 8` and the computed postcondition. A subsequent caller can satisfy this requirement from its own state, or infer another missing part.

This is one sufficient specification, not a claim that `p` and `q` must be distinct in every safe use of `increment`. An aliasing case needs its own consistent specification. Nor can the analysis repair a definite error by inventing impossible ownership: if earlier code freed `p`, adding `p -> n` at the call does not by itself justify the execution. Rechecking candidates against their proposed initial assumptions is essential.

## Concepts and terms

**[1] Separation-logic assertion.** A symbolic description of allocated memory and its relationships. `p -> v` describes a cell; `A * B` requires disjoint heap portions satisfying its operands. List predicates can summarize arbitrarily long linked structures.

**[2] Procedure summary.** A precondition and postcondition describing safe executions. It can be reused without reanalyzing the procedure body for each calling context.

**[3] Bi-abduction.** Simultaneously inferring an anti-frame, the missing assumption, and a frame, the untouched remainder, that make a separating entailment valid. Solutions must satisfy consistency and the restrictions of the analysis's assertion language.


# Value Locality and Load Value Prediction

**Summary by:** GPT 6 Astra

**Author:** Mikko H. Lipasti, Christopher B. Wilkerson, John Paul Shen

**Source:** ASPLOS 1996; ASPLOS Influential Paper Award 2021

**Link:** https://doi.org/10.1145/248209.237173

## Key insight

A load instruction often returns a value it has returned before, even when ordinary address locality is insufficient to avoid waiting. Predicting that value can start dependent work early, provided the prediction is verified before incorrect work becomes visible.

## Basic idea

The paper identifies value locality [1] and proposes a load-value prediction table [2] indexed by the load instruction. A classification table [3] decides when predictions are sufficiently promising to use. Ordinary predictions are checked against actual memory results, while a constant verification unit [4] can validate specially tracked constant loads without another ordinary data access. Incorrect predictions require recovery; predictability is not permission to ignore stores.

## Illustrative example

**Observe a load.** A loop repeatedly executes the same load instruction to obtain a configuration field. Its recent results are `7, 7, 7`. A last-value predictor therefore proposes 7 for the next instance, and the classifier's history allows dependent arithmetic to begin speculatively.

**Verify a correct guess.** The real load returns 7. The dependent computation can be accepted. Prediction did not make the memory access disappear in this ordinary path; it overlapped the wait with useful speculative work.

**Recover from a change.** The configuration is updated and the next real load returns 9. The prediction of 7 is wrong. Computation that depended on 7 must be discarded or re-executed with 9, and the classification history is updated to reflect the mistake. A speculative result must not have irreversibly committed an external action.

**Track a stable location.** For a load classified as constant, the verification unit records both the data address and the relevant prediction-table index. A store to that address invalidates the tracked entry. A later load can bypass ordinary verification only while the matching coherent entry remains valid; otherwise it returns to the ordinary predict-and-check path.

## Concepts and terms

**[1] Value locality.** Repetition in the values produced by an instruction. It differs from temporal address locality: the prediction is associated with the load's instruction address, and repeating results need not imply that all instances access the same data address.

**[2] Prediction table.** Store recent values associated with load instructions. The paper's simple design uses the last value and a direct-mapped, untagged table, so unrelated instructions can interfere. Some larger-history experiments assume an ideal value selector to explore limits; that assumption is not an implemented predictor.

**[3] Load classification.** Saturating counters updated by prediction success divide loads into unpredictable, predictable, and highly predictable classes. The classifier reduces wasted speculation but does not establish correctness. Misprediction costs can offset successful latency hiding.

**[4] Constant verification.** A separate associative structure binds a predicted value's table entry to a data address and invalidates it on relevant stores. A valid match establishes coherence under the modeled mechanism. The table must account for memory changes; repetition alone cannot make a mutable location a semantic constant.

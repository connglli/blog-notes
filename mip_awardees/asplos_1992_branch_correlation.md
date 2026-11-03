# Improving the Accuracy of Dynamic Branch Prediction Using Branch Correlation

**Summary by:** GPT 6 Astra

**Author:** Shien-Tai Pan, Kimming So, Joseph T. Rahmeh

**Source:** ASPLOS 1992; ASPLOS Influential Paper Award 2021

**Link:** https://doi.org/10.1145/143371.143490

## Key insight

A branch's outcomes can look irregular when different incoming paths are mixed together. Use recent branch outcomes to select a separate prediction history for each path pattern, making otherwise hidden correlations usable.

## Basic idea

The predictor splits each branch's history into subhistories [1] selected by a register of recent branch outcomes [2]. Each selected subhistory has its own saturating counter [3], which predicts taken or not taken and learns from the actual result. An `(M, N)` predictor uses the last `M` outcomes to select an `N`-bit counter. Table organization [4] trades the number of branch-address entries against the number of histories retained per entry.

## Illustrative example

**Expose correlation.** Two conditional branches, `first` and `second`, execute consecutively with no intervening branch. Suppose `second` always has the same outcome as `first`, while that outcome varies between executions. A predictor considering only `second`'s undivided past can mix together its taken and not-taken cases.

**Separate the histories.** Use the toy `(1, 2)` configuration. Just before predicting `second`, the one-bit history register contains `first`'s outcome. It selects one of two counters belonging to `second`: one for previous outcome 0 and one for previous outcome 1.

**Predict and learn.** Counters range from 0 to 3, with 0 and 1 predicting not taken and 2 and 3 predicting taken. After suitable training, suppose the two counters are 0 and 3. If `first` is not taken, the selected counter predicts that `second` is not taken. If `first` is taken, the other counter predicts taken. On resolution, increment the selected counter for a taken result or decrement it otherwise, saturating at the endpoints. Then shift the actual outcome into the recent-history register.

**Account for storage.** This toy branch uses two counters instead of one. At a fixed total table budget, allocating more counters per branch-address entry leaves fewer distinct address entries and can increase collisions. Correlation is therefore useful structure to exploit, not a guarantee that adding history always improves prediction.

## Concepts and terms

**[1] Branch subhistory.** The outcomes of one static branch restricted to executions preceded by a particular recent-outcome pattern. Mixing several predictable subhistories can produce a less predictable aggregate history. The paper's method learns the separate cases dynamically rather than requiring the compiler to identify the source-level relationship.

**[2] Recent-outcome register.** An `M`-bit shift register encodes the outcomes of the most recently executed branches, including unconditional branches, selecting among `2^M` cases. This includes information from other branches, not merely the last `M` executions of the branch being predicted.

**[3] Saturating counter.** An `N`-bit state moves toward taken or not-taken confidence without wrapping around. A threshold converts the state into a prediction. For the conventional two-bit case, a single contrary outcome need not immediately reverse a strongly established prediction.

**[4] Prediction table and limits.** Branch-address bits identify a logical entry; history bits select a counter within it. Different branch addresses can share an entry and interfere. Warmup, history length, counter width, and total storage affect accuracy. The paper evaluates trace-based direction prediction, not a universal speedup or a complete implementation of every speculative-pipeline recovery detail.

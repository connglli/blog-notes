# Green: A Framework for Supporting Energy-Conscious Programming using Controlled Approximation

**Summary by:** GPT 6 Astra

**Author:** Woongki Baek, Trishul M. Chilimbi

**Source:** PLDI 2010; SIGPLAN Most Influential PLDI Paper Award, 2020

**Link:** https://doi.org/10.1145/1806596.1806620

## Key insight

Approximation needs an explicit output-quality contract and feedback, not just a faster implementation that seems acceptable on a few inputs.

## Basic idea

Green lets programmers supply approximate functions or permit early termination of loops, together with a quality-of-service measure [1]. Calibration [2] estimates the quality loss and cost of approximation choices. During operation, the runtime selects choices satisfying the requested statistical quality constraint and uses adaptation [3] to reassess them. The contract concerns measured quality statistically, not exact equivalence or a worst-case guarantee on every input.

## Illustrative example

**Setup.** A search service can score either all candidate documents or a prefix of a ranked candidate list. Define quality as the fraction of the exact method's ten highest-scoring documents retained in the approximate top ten. This metric and the numbers below are illustrative, not measurements from the paper.

**Calibration.** On representative saved queries, run the exact function and variants scoring 100 or 300 candidates. Suppose the 100-candidate variant has mean quality 0.91 and the 300-candidate variant 0.98, with measured costs 2 and 5 milliseconds. The exact method costs 12 milliseconds. A quality requirement of at least 0.97 excludes the smaller candidate set under this simple illustrative decision rule.

**Operation.** Use the 300-candidate variant on ordinary queries. Periodically also compute exact results on sampled queries and compare the same metric. These measurements cost time and energy, so they are part of the approximation system's overhead, not free observations.

**Adaptation.** If a changed query mix reduces observed quality to 0.94, the old calibration does not justify continued use. Update the model and choose a less aggressive approximation, or use the exact method when no approximate choice meets the requirement. Returning a result on every query does not imply meeting the quality target on every individual query. A production implementation also needs the paper's statistical treatment rather than treating these illustrative sample means as certainty.

## Concepts and terms

**[1] Quality-of-service measure.** An application-specific numeric evaluation of the output; approximation loss compares it with an exact reference execution on the same input.

**[2] Calibration.** Training executions that associate approximation settings with estimated cost and quality loss.

**[3] Adaptation.** Runtime sampling and model adjustment to respond when actual behavior differs from calibration.

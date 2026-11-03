# Statistically Rigorous Java Performance Evaluation

**Summary by:** GPT 6 Astra

**Author:** Andy Georges, Dries Buytaert, Lieven Eeckhout

**Source:** OOPSLA 2007; SIGPLAN Most Influential OOPSLA Paper Award, 2017

**Link:** https://doi.org/10.1145/1297027.1297033

## Key insight

One unusually fast execution is not a reliable estimate of typical performance, especially when compilation and runtime decisions differ between virtual-machine launches.

## Basic idea

The paper distinguishes startup performance from steady-state performance [1] and treats repeated virtual-machine invocations [2] as essential experimental units. For steady state, collect stable iterations within each invocation, compute one mean per invocation, and estimate uncertainty across those means. Confidence intervals [3] communicate measurement uncertainty and support comparisons. Repeating iterations inside one process cannot substitute for independently restarting a runtime whose optimization choices vary between runs.

## Illustrative example

**Design.** Compare two runtime configurations on one fixed benchmark, input, heap size, and machine. The question is steady-state performance, so launch each runtime several times and run repeated benchmark iterations in each launch. Declare a stability rule in advance; the paper uses a recent-window coefficient of variation [4] threshold as a practical heuristic.

**Measurements.** Suppose configuration A produces stable invocation means of 9, 10, and 11 milliseconds. B produces 9.5, 9.6, and 9.7 milliseconds. The smallest observation favors A, but the means are 10 and 9.6. These invented three-sample datasets demonstrate the distinction, not an adequately powered benchmark study.

**Uncertainty.** For A, the sample standard deviation is 1 millisecond and the standard error of the mean is `1/sqrt(3)`. Under the assumptions for a Student-t interval, the two-sided 95% critical value with two degrees of freedom is about 4.303, yielding approximately `10 +/- 2.48` milliseconds. That uncertainty is much larger than the observed difference between configurations.

**Conclusion.** Gather more independent invocations before making a strong comparative claim, and use an appropriate comparison of means or their difference. Overlapping individual confidence intervals alone are not a universal significance test. If startup is the question instead, measure a fresh launch and its first iteration rather than discarding the behavior of interest as warm-up.

## Concepts and terms

**[1] Steady-state performance.** Behavior after startup effects have settled sufficiently for the specified experiment; a short stable window is a heuristic, not a proof of permanent stationarity.

**[2] Virtual-machine invocation.** A fresh runtime process, distinct from another benchmark iteration in the same process.

**[3] Confidence interval.** An interval-producing procedure with a stated long-run coverage rate under its assumptions.

**[4] Coefficient of variation.** Standard deviation divided by mean, measuring relative variability within a sample window.

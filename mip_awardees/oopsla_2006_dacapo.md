# The DaCapo Benchmarks: Java Benchmarking Development and Analysis

**Summary by:** GPT 6 Astra

**Author:** Stephen M. Blackburn, Robin Garner, Chris Hoffmann, Asjad M. Khan, Kathryn S. McKinley, Rotem Bentzur, Amer Diwan, Daniel Feinberg, Daniel Frampton, Samuel Z. Guyer, Martin Hirzel, Antony Hosking, Maria Jump, Han Lee, J. Eliot B. Moss, Aashish Phansalkar, Darko Stefanović, Thomas VanDrunen, Daniel von Dincklage, Ben Wiedermann

**Source:** OOPSLA 2006; SIGPLAN Most Influential OOPSLA Paper Award, 2016

**Link:** https://doi.org/10.1145/1167473.1167488

**Code:** [DaCapo benchmarks](https://github.com/dacapobench/dacapobench)

## Key insight

A runtime optimization must be evaluated on realistic, varied programs and configurations; a benchmark choice or heap size can reverse an apparent performance advantage.

## Basic idea

DaCapo packages open-source Java applications, inputs, and a benchmark harness [1] with result validation. The paper characterizes workload behavior [2] rather than relying only on elapsed time. Its methodology varies runtime, hardware, heap size, and startup versus repeated execution [3] to expose tradeoffs. The suite is evidence for a specified workload population, not a universal model of every Java application.

## Illustrative example

**Workload.** Compare two garbage collectors using a document-indexing application. Fix the application version, document corpus, and required output. The harness times the selected execution interval and checks the resulting outputs against expected checksums. A fast run that skips documents fails validation and is not a valid speedup.

**Heap experiment.** Suppose collector A takes twelve seconds with a tight heap and eight seconds with a larger heap, while B takes ten and nine seconds respectively. These invented numbers show that reporting only the larger-heap run would favor A, whereas the tight-heap result favors B. State actual heap sizes and their relation to the workload's memory requirements.

**Runtime experiment.** Record the first iteration separately from repetitions within the same process. Class loading and compilation can make the first iteration fundamentally different. If using the harness's stability heuristic, examine a recent window's standard deviation relative to its mean, stop when the configured threshold is met, and report failure to stabilize after the configured limit rather than silently selecting a favorable iteration.

**Interpretation.** Add workload measurements such as allocation volume, live-data size, and executed methods. They help explain why one collector behaves differently, but do not replace timing. Repeat across other applications and machines before generalizing. A claim should identify the exact suite release and inputs, because a suite name alone does not define a reproducible experiment.

## Concepts and terms

**[1] Benchmark harness.** Code controlling workload invocation, inputs, timing boundaries, repetitions, and correctness checks.

**[2] Workload behavior.** Properties of actual execution, such as allocated bytes and object lifetimes, that exercise runtime mechanisms differently.

**[3] Startup versus repeated execution.** First-use costs and later execution in a warmed runtime answer different performance questions and must not be conflated.

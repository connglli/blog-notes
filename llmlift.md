# Verified Code Transpilation with LLMs

**Author:**
- Sahil Bhatia, Jie Qiu, Niranjan Hasabnis, Sanjit A. Seshia, Alvin Cheung (UC Berkeley; Hasabnis at Code Metal, work done while at Intel Labs)<br/>

**Source:** NeurIPS 2024 (pages 41394-41424)

**Link:** https://openreview.net/forum?id=spwE9sLrfg (arXiv: https://arxiv.org/abs/2406.03003)<br/>

**Benchmarks:** https://github.com/metalift/metalift/tree/llmlift/llmlift/benchmarks

## Key insight

The LLM proposes and the verifier disposes: the model writes the target DSL program as a single Python expression over the DSL operators and guesses the loop invariants, and an SMT solver proves functional equivalence to the source for all inputs before the program is rewritten into the DSL's concrete syntax. The paper presents this as "the first to leverage LLMs to generate both code and proof annotations together": the annotations are the model's guesses, and the correctness guarantee comes entirely from the solver.

## Basic idea

Verified lifting compiles a program into a DSL by searching for a target program and proving it equivalent to the source, but the symbolic search needs a per-DSL search space and hand-written heuristics that cost thousands of lines of expert code [1]. LLMLift replaces the search with prompting: the prompt defines the DSL operators by their semantics written as Python functions, Python serves as the intermediate representation (IR), and the model (GPT-4) is asked for a program summary, a composition of those operators [2]. Loops need invariants, so a second, one-shot prompt generates an invariant in the template `f(i) ∧ e(Tlang)`, a range condition on the loop index plus an equality relating the accumulator or output to the summary applied to a prefix of the input [3]. A parser rejects candidates that leave the operator set, rewrite rules translate the summary and invariant into SMT, and cvc5 or z3 discharges the Floyd-Hoare verification conditions (the invariant holds initially, is preserved by the loop body, and at exit implies the summary equals the return value) for all inputs; only a verified summary passes to the code generator that emits the DSL's concrete syntax [4]. Failures feed back as Boolean information: the set of already-tried summaries goes into the next prompt with an instruction not to regenerate them, under a budget of 50 summary queries and 10 invariant queries per summary [5]. The authors build compilers this way for Spark MapReduce, the Domino packet-processing atoms, TACO, and the TensIR tensor IR, with prompts of about 70 to 320 lines instead of the baselines' thousand-odd lines of heuristics, and solve 44 of 45, 10 of 10, 60 of 60, and 23 of 23 benchmarks [6].

## Illustrative example: summing positive readings

**The source and the DSL semantics.** The function to lift sums the positive values of an integer list:

```c
int positiveTotal(int[] xs) {
  int acc = 0;
  for (int i = 0; i < xs.length; i++)
    if (xs[i] > 0) acc += xs[i];
  return acc;
}
```

The target is a small list DSL, named Breeze here, whose operators are presented to the model as Python functions, which is the IR [2]:

```python
def keep(xs, f):    # map, keeps the list shape
    return [] if not xs else [f(xs[0])] + keep(xs[1:], f)
def total(xs):      # reduce with +
    return 0 if not xs else xs[0] + total(xs[1:])
def choose(c, a, b):
    return a if c else b
```

Asking the model directly for Breeze code invites invented operators; defining them in Python works because the model has seen plenty of Python and the semantics are explicit [2].

**Generating the summary and the invariant.** Zero-shot, the model produces the program summary

```python
total(keep(xs, lambda v: choose(v > 0, v, 0)))
```

One-shot, with the source plus the assertion that the return value equals the summary, it then produces the invariant [3]:

```python
def inv(xs, i, acc):
    return 0 <= i <= len(xs) and acc == total(keep(xs[:i], lambda v: choose(v > 0, v, 0)))
```

The first conjunct is the `f(i)` part, the second the `e(Tlang)` part: the accumulator equals the summary evaluated on the processed prefix.

**Filtering and verification.** A candidate such as `total([v for v in xs if v > 0])` dies in the parser, because a list comprehension is outside the operator set [4]. For the candidates that parse, the three verification conditions are encoded in SMT: initially `inv(xs, 0, 0)`; preservation, `inv(xs, i, acc) and i < len(xs)` implies `inv(xs, i+1, acc + (xs[i] > 0 ? xs[i] : 0))`; and at exit, `inv(xs, len(xs), acc)` implies `acc == total(keep(xs, ...))`. Suppose the model first guesses `choose(v > 0, v, 1)` instead of returning 0 for non-positive values: for `xs = [-1]` the candidate invariant claims `acc = 1` after one iteration while the loop leaves `acc = 0`, so the solver refutes preservation and the summary is retired [4]. The next summary prompt lists it with the instruction not to regenerate it, and the corrected summary above is checked and accepted within the budget; the paper's name for this propose-check-feedback loop is oracle-guided inductive synthesis [3].

**Emitting the DSL code.** Pattern-matching rewrite rules turn the verified summary into the DSL's concrete syntax, here a chain [4]:

```python
xs.keep(lambda v: v if v > 0 else 0).total()
```

The summary and its proof are unchanged when the same program is emitted for another backend; only the operator-by-operator code generation rules change.

## Concepts and terms

[1] Verified lifting and the VL problem.
Lifting compiles a general-purpose program into a DSL. Verified lifting pairs the search for the target with a proof that the target is functionally equivalent to the source; its three phases are search, verification, and code generation. The target is expressed as a program summary (`PS`), a composition of DSL operators drawn from a program space `G`, and as a certificate of correctness, typically loop invariants `Inv` from a certificate space `G_I`; the problem is to find `PS` and `Inv` such that `∀σ. S(σ) = PS(σ)`, which traditional tools attack with enumerative, deductive, or constraint-based (SyGuS-style) search. Those solvers depend on the grammar and on hand-written domain heuristics, so each new DSL needs a new solver effort; the paper's baselines are MetaLift (Spark and Domino, using Rosette), C2TACO, and Tenspiler. The guarantee applies to the programs being compiled, not to a compiler verified once for all inputs.

[2] Python as the IR.
The prompt defines every DSL operator by its semantics as a Python function and includes the source program as the specification; the model must answer with one return expression built only from those functions, without loops and with expressions inlined. Python is the IR because it is heavily represented in LLM training data, so models write it reliably, and because its simple structure makes the later translations mechanical: pattern-matching rules map the IR to the verifier's input syntax and to the DSL's concrete syntax. Prompting for the DSL directly fails, both because DSLs are underrepresented in training data (asked for MLX, Apple's tensor DSL, GPT-4o hallucinated a nonexistent MLCompute header) and because theorem provers cannot consume DSL code; the IR is the common language for the model and the prover.

[3] Two-phase generation and the invariant template.
The summary is generated first, zero-shot; the invariant is generated second, one-shot, from a prompt containing the source plus an assertion equating the return variable with the summary. VL invariants have the templated form `Inv ≜ f(i) ∧ e(Tlang)`: `f(i)` constrains loop indices (range conditions) and `e(Tlang)` is an inductive expression over DSL operators (typically an equality for the accumulator or output). The prompt requires only the defined functions, no loops, a single return, inlined expressions, and one invariant per loop. The paper frames the loop as oracle-guided inductive synthesis (OGIS), a generalization of counterexample-guided inductive synthesis in which LLM oracles propose summaries and invariants and the verifier answers with Boolean feedback. The split is empirical: generating summary and invariant in one step solves 20 of the 23 tensor benchmarks, the two-phase form all 23, since the invariant prompt can build on the chosen summary; with GPT-4o and Claude 3.5 Sonnet, zero-shot invariants suffice for all 23, while GPT-4 with a zero-shot invariant prompt solves 11.

[4] Verification conditions, the parser, and the contract.
Correctness is established in Floyd-Hoare logic. For a source loop with a candidate invariant the verifier checks: initial, the invariant holds before the loop; preservation, the invariant at iteration i implies it after one body execution; and termination, at loop exit the invariant implies that the return value equals the summary. Rewrite rules translate the summary and the Boolean invariant into SMT, and cvc5 and z3 check the conditions for all inputs, not for tests. A rule-based parser runs before verification and rejects candidates that use anything outside the operator set or constructs the SMT encoding cannot represent (for loops, list comprehensions, nested list literals); model errors are thus classified as syntactic (caught by the parser) or semantic (caught by the solver). The contract is functional equivalence of the emitted code to the source, for side-effect-free functions; the supported subset of C/C++ and Python excludes pointers and objects.

[5] The search loop and its budgets.
The algorithm runs for a fixed number of rounds, requests n summaries per round, skips ones seen before, parses them, requests n invariants for each parseable summary, parses those, and verifies each summary-invariant pair; the first success is returned, otherwise the result is `None`. Every attempted summary is recorded and included in later prompts with "These generated programs are incorrect. Do not generate the same. Please generate another program.", so a summary whose invariants all fail is retired. The budgets are 50 summary queries and 10 invariant queries per summary, at temperature 0.7, with GPT-4 through its API; the parser and API plumbing are about 700 lines of Python. Feedback is Boolean only: a candidate is reported as wrong, but the solver's counterexample is not shown (the paper lists counterexample and compiler-error feedback as improvements).

[6] Evaluation.
Four DSLs, each against the symbolic VL tool for its domain. Spark: 45 Java-to-MapReduce benchmarks, all with loops; MetaLift solves 40 with a one-hour timeout, LLMLift 44, under a minute per benchmark against MetaLift's 3, with a prompt of about 100 lines against MetaLift's 1000-plus lines of search-space description. Domino: 10 loop-free packet-processing benchmarks (no invariants required), both solve all 10, 2 seconds against 6, about 70 lines of prompt against 1100-plus lines. TACO: 60 benchmarks, C2TACO solves 57, LLMLift all 60 (C2TACO's failures need expression depth beyond 4 and time out even with a day), 2 seconds against 41 on average, about 100 lines of prompt against 1000-plus lines of heuristics. TensIR: 23 tensor benchmarks, both tools solve all; Tenspiler depends on three expert-written optimizations (about 1200 lines) and solves 5 of 23 without them, LLMLift uses about 320 lines of prompt and averages 95.89 seconds against 115.14. The paper's summary is 7 more benchmarks than the baselines, about 1000x less code to write (prompts instead of search-space descriptions), and 6x faster on average. Runtime speedups of the translated code are those the original tools reported (2.1x for NumPy and 167.71x for PyTorch against sequential C++, 15.6x for Spark against sequential Java, 24x for TACO), since the search has no cost function and the outputs were manually checked to match the baselines'.

[7] Additional model and scalability studies.
Prompts transfer across models without tuning: on the 23 tensor benchmarks, GPT-4o and Claude 3.5 Sonnet solve all, Gemini 1.5 Pro 21 (two summaries wrong); Llama 3 8B and Mistral Nemo 12.2B solve none, their candidates failing the parser, which the paper attributes to weaker instruction following and long-context handling. With zero-shot invariant prompts, GPT-4 solves 11 of 23, GPT-4o and Claude 3.5 Sonnet all 23, Gemini 20. On 10 synthetic TACO benchmarks whose target expressions have length 5 to 10, C2TACO times out on all of them at 90 minutes while LLMLift solves all in under 2 seconds, and a variant with exponent 20 is also solved.

[8] Limitations and scope.
The supported source is a side-effect-free subset of C/C++ and Python without pointers or objects, and the proof equates the source to the summary under the operator semantics written in the prompt, not to the DSL's implementation. Feedback is Boolean, so the model learns only that a candidate is wrong, not why; the paper proposes counterexample or compiler-error feedback and semantic pre-filtering with tests as improvements. The search has no cost function: it finds an equivalent program, not the fastest one, and the reported speedups of generated code are inherited from the baseline tools' outputs, which LLMLift's outputs were manually checked to match.

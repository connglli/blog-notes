# Taming the Hydra: Targeted Control-Flow Transformations for Dynamic Symbolic Execution

**Summary by:** DeepSeek V4.1 Flash, GPT 6 Astra

**Author:** Charitha Saumya, Muhammad Hassan, Rohan Gangaraju, Milind Kulkarni, Kirshanthan Sundararajah

**Source:** OOPSLA1 2026, Proceedings of the ACM on Programming Languages 10, article 94, 38 pages

**Link:** https://doi.org/10.1145/3798202

**Code:** [CFMSE-OOPSLA26-Artifact](https://github.com/hassanaleem/CFMSE-OOPSLA26-Artifact)

**Artifact:** [Zenodo artifact](https://doi.org/10.5281/zenodo.19120042)

## Key insight

Remove selected symbolic branches before symbolic execution by completing and merging their instruction sequences. The paper argues that the transformation preserves failures, although unconditional memory accesses can introduce additional failures that must be checked against the original program.

## Basic idea

Dynamic symbolic execution (DSE) [1] can explore exponentially many paths when input-dependent branches occur repeatedly. cfm-se uses symbolic-variable analysis [2] to select such branches, then aligns their instructions and inserts extra operations to make the sequences match [3]. It merges the sequences using `select` operations [4] that encode conditional values without forking at the removed branch. The paper gives a failure-preservation argument [5] for its supported transformations and a driver that replays failing inputs on the original program, disabling a transformation location when it causes a false positive. Branches involving symbolic memory addresses are excluded because those accesses are expensive for the symbolic executor.

## Illustrative example

**Setup.** A KLEE driver makes the contents of an allocated three-element unsigned array symbolic and passes it to this function. The array address and loop indices are concrete; only the element values vary symbolically. The assertion intentionally exposes a bug in the function's claimed result.

```c
#include <assert.h>

void bump_small(unsigned values[3]) {
  for (unsigned i = 0; i < 3; ++i) {
    if (values[i] < 10u) {
      values[i] = values[i] + 1u;
    }
  }
  assert(values[0] != 10u);
}
```

**Branch selection.** The symbolic-variable analysis propagates the driver's symbolic array contents into `bump_small`. It marks the test `values[i] < 10u` as symbolic, while the loop bound remains concrete. The three update decisions can produce eight combinations before the final assertion. Dynamic state merging [6] could combine states after each update, but the executor would first encounter each branch and determine feasible outcomes.

**Completing the alignment.** The update's true side loads an element, adds one, and stores the result; its false side does nothing. cfm-se adds matching operations to the false side: a load, a harmless addition, and a store of the value loaded immediately before that store. A matching redundant load is added on the true side. With valid ordinary memory, the added store leaves the false side's element unchanged.

**Merging.** Let `condition` be the original comparison. At the level of compiler instructions, the merged block loads the element into `before`, computes `changed = before + select(condition, 1, 0)`, reloads the element into `saved`, and stores `select(condition, changed, saved)`. Both accesses use the same concrete element address. For input `[9, 20, 8]`, the updates produce `[10, 20, 9]`. The symbolic executor represents the choices as conditional expressions instead of splitting states at the three update branches; the assertion still requires checking.

**Replaying the failure.** The transformed program fails the assertion for that input. Replaying it on the original produces the same failure, so the driver reports a real bug. All inserted accesses in this example are within the allocated array. If a transformation instead introduces a failing access on an input that succeeds in the original, the driver records that transformation location, rebuilds with the location excluded, and restarts the search.

## Concepts and terms

**[1] DSE, path conditions, and KLEE.** Symbolic values represent many possible concrete inputs. An execution state records program values and a path condition, the constraints accumulated along that path. A satisfiability-modulo-theories (SMT) solver checks whether those constraints have a solution and can produce a corresponding test input. KLEE performs this analysis on LLVM's intermediate representation, the compiler's typed instruction form. Repeated independent symbolic decisions cause path explosion, the growth in combinations the executor must handle.

**[2] Symbolic-variable analysis.** The analysis starts from inputs marked symbolic, propagates dependence through computations and control flow, and reprocesses callees when their parameters receive symbolic inputs. It combines information from different callers rather than analyzing each calling context separately. A value may be symbolic while the address holding it remains concrete, as with the array elements in the example.

**[3] Alignment and extra instructions.** Alignment pairs compatible instructions from the two sides by operation, allowing operands to differ. Missing partners are supplied by extra arithmetic, logical, comparison, conversion, or memory instructions. Original instructions must not consume results of extras. Extra arithmetic receives safe operands; an extra store writes back the value read immediately before it. Arbitrary calls cannot be inserted this way because their effects need not be harmless.

**[4] Select and memory handling.** `select(c, a, b)` chooses an already-computed value: `a` when `c` is true and `b` otherwise. In symbolic execution it becomes an if-then-else expression inside a constraint. Matching accesses to the same concrete address can merge. Accesses to different concrete addresses are kept as separate unconditional operations, avoiding a symbolic choice of address; this can expose invalid accesses that a branch guarded. If an aligned access has a symbolic address, cfm-se skips the branch. More selects can make solver queries harder even when fewer branches remain.

**[5] Failure preservation and replay.** Under the paper's instruction and memory assumptions, a failing input for the original must also fail after transformation. The argument relies on keeping original value flows intact and preventing extra stores from changing valid memory. It does not promise identical behavior on inputs where extra accesses fail, or that a resource-limited search will discover every bug. Replaying inputs distinguishes original failures from added ones; excluding the responsible locations removes the corresponding false positives in subsequent runs.

**[6] Dynamic state merging.** A symbolic executor can combine compatible states at a common program location by representing differing values with conditional expressions. This reduces separate states but retains the earlier feasibility checks and depends on states reaching a suitable merge point. cfm-se performs the corresponding branch removal during compilation, before KLEE explores those paths.

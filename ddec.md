# Data-Driven Equivalence Checking

**Author:**
- Rahul Sharma, Eric Schkufza, Berkeley Churchill, Alex Aiken (Stanford University)<br/>

**Source:** OOPSLA 2013 (pages 391-406)

**Link:** https://doi.org/10.1145/2509136.2509509<br/>

## Key insight

The simulation relation that a loop-equivalence proof needs can be guessed from test runs and then checked: run the two loops on the same inputs, read the equalities between their live state elements off the observed values, pair up their loop-free code paths from the instruction traces, and let an SMT solver prove the guessed relation; insufficient test data makes the proof fail but can never make it succeed wrongly.

## Basic idea

Equivalence checking of loops at the assembly level has no practical sound techniques, and inferring the required simulation relation [1] statically would need a sound and precise x86 analysis that does not exist. DDEC guesses the relation from data instead: it decomposes the two x86 loops at cutpoints, runs both on a set of test cases, matches the two instruction traces to obtain corresponding loop-free code paths [2], and learns equalities between the live registers, stack slots, and heap locations at each cutpoint from the observed values [3]. The guess is then checked: proof obligations are relational Hoare triples [4] discharged by Z3 in quantifier-free bitvector logic, covering the entry, each pair of corresponding paths between cutpoints, and the exit, plus obligations that no corresponding path was missed. A failed check returns a counterexample, which is added to the observed data and the equality learning is repeated, so DDEC is sound (it reports equivalence only from a complete proof) but incomplete: sparse tests or a needed inequality make it fail [5]. The technique extends to multiple and nested loops, function calls, and polynomial equalities by adding monomial features; on x86-64 it proves GCC -O2 binaries equivalent to CompCert output for the integer benchmarks of the CompCert test suite and OpenSSL's big-number multiplication, and it serves as the equivalence checker of an extended STOKE whose loop optimizations are competitive with GCC -O3. Its limits: invariants are conjunctions of equalities, so relations such as `i ≤ n` are inexpressible and some proofs need adjusted test predicates, while transformations that reorder an unbounded number of memory writes (loop fusion, tiling) and floating point are out of scope.

## Illustrative example: strength reduction

**The two loops.** A compiler removes the multiplication from inside the loop by maintaining the running value 3k in a register. Both programs are x86 loops with the arithmetic abstracted to register assignments:

```text
target T                             rewrite R
L1: if r1 == rn goto L4              K1: if r1' == rn' goto K4
L2: r2 = r2 + 3*r3                   K2: r2' = r2' + r3'
L3: r3 = r3 + 1; r1 = r1 + 1         K3: r3' = r3' + 3; r1' = r1' + 1
    goto L1                              goto K1
L4: return r2                        K4: return r2'
```

where r1 is the loop counter and rn holds n. T maintains k (in r3) and R maintains 3k (in r3').

**Cutpoint and test data.** The loop heads form the cutpoint (L1, K1) [1], and the pair satisfies the paper's cutpoint condition: the number of visits per test is an affine function of the other program's visit count (here exactly equal, since both iterate the same way). A test run with n = 3 records the following values on each visit of the pair:

| visit | r1 | r2 | r3 | r1' | r2' | r3' |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 1 | 0 | 1 | 1 | 0 | 3 |
| 3 | 2 | 3 | 2 | 2 | 3 | 6 |
| 4 | 3 | 9 | 3 | 3 | 9 | 9 |

Walking the two traces in parallel between visits of the cutpoint also gives the corresponding paths [2]: the loop bodies correspond to each other, and the exit segments correspond to each other.

**Learned equalities.** Each visit is a row of a matrix whose columns are the live features [3]. The nullspace of that matrix contains r1 - r1' = 0, r2 - r2' = 0, and 3*r3 - r3' = 0, so the candidate invariant at the cutpoint is `r1 = r1' ∧ r2 = r2' ∧ 3*r3 = r3'` (the equality r3 = r3' is correctly not inferred, since it already fails at the second visit). Heap locations outside the finite set of tracked features are implicitly required to have equal values in the two programs.

**Proof obligations.** The entry obligation says that starting both programs from equal states establishes the invariant (all three equalities hold at zero). The transition obligation [4] says that one iteration of each preserves it: r1+1 = r1'+1, r2 + 3*r3 = r2' + r3', and 3*(r3+1) = 3*r3 + 3 = r3' + 3. The exit obligation says the exit path conditions r1 == rn and r1' == rn' agree (because r1 = r1' and rn = rn'), so both return the same r2 = r2'. Obligations for the untested static paths assert that the target cannot take an unpaired path or that the unpaired path is infeasible.

**Counterexample feedback.** Suppose the data had implied the spurious equality r3 = r3' (for example if all tests stopped before the first update of both counters). The transition obligation would then fail, Z3 would return a concrete state refuting it, that state would be added as a row, and the recomputed nullspace would weaken the candidate invariant. A failed proof can only report failure, so bad data cannot turn into a wrong equivalence claim [5].

## Concepts and terms

**[1] Cutpoints, cutsets, and the contract.** A cutpoint is a pair of program points, one from each loop; a cutset must include at least one program point of every loop, so that the segments between cutpoints are loop-free, and transitions between cutpoints carry pairs of code paths. A proof is a simulation relation (a state relation under which every step of the target is matched by a step of the rewrite, in contrast to a bisimulation, which matches steps in both directions): equal input states at entry, an invariant at every cutpoint, and equal return values and memory at exit. The equivalence relation is asymmetric: if the target (the unoptimized program) terminates without aborting, the rewrite must terminate in exactly the same state, while a target that aborts (for example with a segmentation fault) imposes no requirement on the rewrite, matching how compilers exploit undefined behavior. A cutpoint candidate is accepted by brute force when its visit counts across all tests satisfy a linear relation `m_T = a*m_R + b` and its number of live heap locations matches; candidates are ordered by how similar the two observed heap states are, and a minimal subset that leaves the decomposition loop-free is kept.

**[2] Corresponding paths.** A code path t of the target corresponds to a path r of the rewrite when both are associated with the same transition and, whenever the target executes t, the rewrite executes r. The pairs are read off the traces: walk the two traces in parallel until both reach cutpoints and record the pair of segments. Because tests are an under-approximation, the obligations also cover untested static paths: each gets an arbitrary partner path plus a verification condition that the target cannot take a different path; failure means the data was insufficient.

**[3] Invariant learning from data.** At each cutpoint the observed states form a matrix whose columns are the live features (registers, subregisters sign- or zero-extended to a common width, and stack slots turned into named temporaries by liveness analysis). The equalities that hold on every row are exactly the nullspace of the matrix, computed with exact rational arithmetic; their conjunction is the candidate invariant. The heap is implicitly forced equal except for a finite set of locations that may differ. The nullspace never misses an equality that holds statically (missing rows only weaken the learned invariant) but can learn spurious equalities from uniform data, which counterexamples remove. Adding a column for every monomial up to degree d turns the same computation into polynomial equalities (for example `x^2 = y^2`, which is a disjunction of two linear equalities).

**[4] Proof obligations and their checking.** A relational Hoare triple `{P} <t, r> {Q}` says that if the target starts in a state satisfying P and executes its path t to completion without aborting, then the rewrite does not abort on path r and every final state satisfies Q. Three kinds are generated: entry triples `{E} <t, r> {Q}` with E the equality of initial states, transition triples `{P} <t, r> {Q}` between successive cutpoints, and exit triples `{P} <t, r> {F}` with F the equality of return values and memory. Obligations are encoded in quantifier-free bitvector arithmetic with arrays and uninterpreted functions for multiplication and division, aliasing between two memory accesses is constrained by `addr1 = addr2 implies val1 = val2`, and Z3 discharges them. The paper proves that if all obligations hold, the target is equivalent to the rewrite and the cutset together with the invariants is a simulation relation.

**[5] Counterexample feedback.** When an obligation fails, the model Z3 returns is inserted as an extra row of the cutpoint's matrix, the nullspace is recomputed, and the learned equalities weaken; this either lets the next proof succeed or removes enough conjuncts that the obligation fails for a real reason. The same mechanism removes spurious equalities such as `p = a` learned when every test placed a pointer at the same address.

**[6] Implementation and tracing.** The target is instrumented by a small JIT assembler that records after every instruction the general-purpose and SSE registers, the flags, and the address and value of each memory access. The rewrite runs in sandboxes derived from the target's observed stack size and heap footprint, with guards that turn out-of-range accesses, too many backward jumps, and ABI violations into safe failures. Tests are generated randomly for loops that only touch registers and stack, and otherwise come from user harnesses or existing project test suites; the prototype uses sixteen random tests, and on the CompCert-derived benchmarks two to eight tests sufficed. All run-time is dominated by Z3; the data analysis takes milliseconds.

**[7] Evaluation and applications.** Reported runtimes range from under a second to several hours. The micro-benchmarks include the two strength-reduction examples from equality saturation (which DDEC proves equivalent without needing the expert-written rewrite rules) and a loop unrolling case that equality saturation cannot handle, and a loop with an off-by-one error is rejected with a counterexample. Against CompCert 1.12, DDEC proves eleven target/rewrite pairs, including the integer benchmarks of the CompCert test suite, equivalent across CompCert and GCC -O2 -m32 code, which certifies GCC compilations against the verified compiler; sha1 takes 12,889 seconds because of its large constants. OpenSSL's big-number multiplication (GCC -O0 against -O3) is proven in about two hours, with the largest single obligation at ten minutes. As STOKE's equivalence checker, with added moves for cross-block swaps and block resizing, it verifies loop optimizations that the original STOKE could not produce, and slicing the verification conditions cuts the SAXPY verification from a four-hour timeout to 0.62 seconds.

**[8] Limitations.** The invariant language contains no inequalities, so a target loop `for (i = 0; i < n; i++)` cannot be related to a rewrite `for (i = 0; i != n; i++)`, which needs the invariant `i = i' ∧ n = n' ∧ i ≤ n`; for four benchmarks in the evaluation the test predicates had to be made identical by hand before the proof succeeded. Quantified heap invariants are out of reach, which rules out transformations that reorder an unbounded number of memory writes, such as loop fusion or a reordered array traversal. Floating-point instructions are not modeled because Z3 has no floating-point theory at the time, and success depends on test coverage: optimizations exercised only on rarely used paths cannot be proven.

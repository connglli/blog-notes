# Translation Validation for an Optimizing Compiler

**Author:**
- George C. Necula (University of California, Berkeley)<br/>

**Source:** PLDI 2000 (pages 83-95)

**Link:** https://doi.org/10.1145/349299.349314<br/>

## Key insight

An optimizing compiler can be checked one run at a time instead of being proved correct once: dump its intermediate representation after every pass, symbolically evaluate the "before" and "after" programs into loop-free transfer functions, and infer and check a simulation relation between them. The paper's message is that such an infrastructure costs about the effort of one compiler pass and isolates real bugs.

## Basic idea

Proving that an optimizing compiler always produces correct code is out of reach, but GCC can be told to dump its RTL intermediate representation after every pass, so a validator can compare the program before and after each transformation without modifying the compiler [1]. The correctness contract is observable equivalence: two executions are equivalent when they perform the same sequence of function calls and returns, with equal memory states, arguments, and return values, and spill slots are renamed to fresh temporaries first so that register-allocation traffic is invisible [2]. *The witness of equivalence is a simulation relation [3]: a set of triples (a source program point, a target program point, equalities between their live temporaries) such that executions started at related points in states satisfying the equalities are equivalent; the checker follows both programs in parallel, symbolically evaluating each basic block into a transfer function [4] and simplifying the collected expression, memory, and state constraints with arithmetic, memory, and aliasing rules that mirror the compiler's own rules [5].* Since GCC is not modified, the relation is inferred instead of supplied: a Scan component walks the two control-flow graphs in parallel, a Branch component decides by heuristic similarity scores whether each source branch was eliminated, kept, or reversed in the target, and a Solve component eliminates the generated constraints, with any leftover constraint reported as a possible compilation error, that is, as a false alarm when no real error exists [6]. The prototype (OCaml, 10,500 lines) validated the compilation of GCC 2.91 and the Linux kernel across GCC's passes with low false-alarm rates, at about four times the cost of compilation, and isolated a known GCC 2.7.2.2 bug in the register allocator [7]. Its limits: the branch heuristics do not handle loop unrolling, only equality constraints are inferred, reasoning stops at function calls, and most maintenance effort goes into keeping the algebraic and aliasing simplifiers as strong as the compiler's own reasoning [8].

## Illustrative example: strength reduction on a loop

**The loop pair.** The source writes `u*i` into `a[i]` for `i` in `0..n-1`, where `u` is the global `c`, and returns `i`. In IL notation (with `[&x]` a memory read and an assignment to `[E]` a memory write):

```text
source                                   target
S0: i <- 0                               T0: r0 <- 0
S1: i < [&n] ? jump(S2) : jump(S3)          r1 <- 0
S2: u <- [&c]                               r2 <- [&c]
    [&a + i] <- u * i                       r0 < [&n] ? jump(T1) : jump(T2)
    i <- i + 1                           T1: [&a + r0] <- r1
    jump(S1)                                r0 <- r0 + 1
S3: return i                                r1 <- r1 + r2
                                            r0 < [&n] ? jump(T1) : jump(T2)
                                         T2: return r0
```

The target is what GCC-like transformations produce here: the loop is inverted (the test is duplicated at the entry and the bottom), the computation `u*i` becomes the running value `r1 = u*i` (strength reduction, adding `u` each iteration), the global read `[&c]` is hoisted into a register `r2`, and temporaries are allocated to registers `r0`, `r1`, `r2`.

**The simulation relation** [3], with one implicit memory-equality condition in every element:

```text
1. (S0, T0):  (no constraints)
2. (S1, T1):  i = r0,  [&c]*i = r1,  [&c] = r2
3. (S3, T2):  i = r0
```

**Checking the entry.** Element 1 holds at start. The target's duplicated test at T0 corresponds to the source's test at S1 (both branch on `index < [&n]`); when the loop is entered, `i = r0 = 0`, `[&c]*0 = 0 = r1`, and `[&c] = r2` establish element 2, and when it is skipped, `i = r0 = 0` establishes element 3, whose equal returns follow from equal memory states.

**Checking the loop.** Assume element 2 at (S1, T1) and take the continue branch on both sides. The source reads `[&c]`, writes `[&c]*i` to `&a + i`, and increments `i`; the target writes `r1` to `&a + r0`, increments `r0`, and adds `r2` to `r1`. To re-establish element 2:
* `i + 1 = r0 + 1` follows from `i = r0`;
* the write cannot change `[&c]`, because `&a + i` and `&c` are addresses of two different globals (the same aliasing assumption GCC itself makes), so `[&c] = r2` is preserved and the source's read still yields the old value;
* the remaining goal, `[&c] * (i + 1) = r1 + r2`, distributes into `[&c]*i + [&c] = r1 + r2`, which follows from `[&c]*i = r1` and `[&c] = r2`.

The two branch conditions agree because `i = r0`, so the programs stay in lockstep.

**Checking the exit.** The failing test sends the source to S3 and the target to T2; both return the same value because `i = r0`, and the memory states are equal, so the returns are the same.

**A wrong rewrite.** If the target updated `r1 <- r1 + 1` instead (a wrong strength reduction), the goal `[&c] * (i + 1) = r1 + 1` would not simplify to an identity, TVI would report a residual constraint at this element, and a human would decide whether it is a real compiler bug or a limitation of the simplifier.

**Why syntax and register names do not matter.** The checker never compares the two programs instruction by instruction: symbolic evaluation turns each basic block into a transfer function over its live registers, so the target's use of `r1` where the source computes `u*i`, and any scheduling differences inside a block, disappear before the constraints are formed.

## Concepts and terms

**[1] Per-pass validation via RTL dumps.** Translation validation checks the result of each compilation instead of the compiler; the approach comes from Pnueli, Siegel, and Singerman, whose original translation validation checked a non-optimizing compilation from SIGNAL to C, and this paper advances it to full semantic equivalence on a realistic optimizing compiler. GCC is run with flags that dump its RTL intermediate language after each of up to thirteen passes, and a parser compares each pair of consecutive dumps; the prototype runs as a substitute for the C compiler when building GCC itself or the Linux kernel, and does not need any compiler modification. The validator's semantic coverage is strong by design (it checks full equivalence, not just type safety or some property), while its completeness is the weak side: every unexplained difference becomes a false alarm to be triaged by a human.

**[2] The intermediate language and the contract.** Functions are sequences of instructions assigning temporaries, reading and writing memory, calling, returning, jumping, and branching; the memory state is an explicit value, with `upd(M, E1, E2)` the result of writing `E2` at `E1` in `M`, `sel(M, E)` a read, and `updcall` the effect of a call. Two executions are equivalent when they perform the same sequence of calls and returns, where calls match on memory state, arguments, and the callee address, and returns match on memory state and return value (and, by the criterion, on termination). Spill slots do not count as observable memory: before checking, they are renamed to fresh temporaries, which undoes spilling, makes the non-aliasing of spill slots explicit, and lets the register allocator be validated. A C program that actually writes through a pointer into a spill slot has undefined behavior, the same undefined behavior that compilers already assume away. Volatile reads and writes are added to the observable events for GCC's back end.

**[3] Simulation relation.** A simulation relation between source `S` and target `T` is a set of elements `(PCS, PCT, equationals)`, where the equalities relate temporaries (and memory reads) live at the two points, with source expressions on the left and target expressions on the right. It is correct when for every element, all pairs of executions of `S` from `PCS` and of `T` from `PCT` that start in states satisfying the equalities are equivalent. Thus a correct relation is a witness of equivalence, and checking one element follows both programs until they reach a pair of points related by some (possibly other) element, which is why the set must contain "enough" elements for the check to terminate. The paper suggests a compiler could emit its relation as an explanation of the transformation; this work infers it instead.

**[4] Symbolic evaluation of basic blocks.** Each basic block is turned into a transfer function from the block's entry state (the memory and the live registers, treated as parameters) to a symbolic state, which is a return, a jump, or a conditional branch with symbolic arguments; the rules substitute assigned expressions for temporaries and update the memory parameter for loads, stores, and calls. The whole function becomes a system of mutually recursive, side-effect-free block definitions, so many syntactic differences vanish: two blocks that compute the same value through different orders, register names, or common subexpressions produce identical transfer functions. This abstraction is what makes equivalence tractable without knowing which optimization ran; all decisions about arithmetic and aliasing are postponed to constraint checking.

**[5] The equivalence-checking rules.** A pattern matcher applies rules that "must match the semantics of the intermediate language", and that are designed to cover all properties the compiler itself uses: assumptions may be used, additions commute, sums of literals collapse, equality is a congruence, and memory rules handle reads after writes, writes that do not alias, writes over a value already present, and don't-care locations. General memory equality is written `M = M'` except at a set of addresses, which is what lets the checker accept transformations that change the sequence of writes. The checker is much smaller than the compiler (it never decides which rule to use), so its operation can be inspected; its weakness is that the simplifiers must be at least as strong as the compiler's reasoning, and keeping them so is most of the maintenance effort.

**[6] Inferring the relation.** The inference has three components. Scan walks the source and target in parallel between pairs of blocks, following jumps and collecting constraints of three kinds (expression equalities, memory-state equalities, and symbolic-state equalities), and terminates because each pair of blocks is processed once. Branch is consulted at each source branch and returns one of four answers, eliminated with the true side kept, eliminated with the false side kept, kept in the same direction, or kept reversed, chosen by heuristic similarity scores between conditionals and instruction sequences; the scores use function-call sequences, whether the points are already known to be related, RTL instruction serial numbers (which survive transformations, so the fraction of shared numbers measures similarity), and source line numbers for duplicated code. Solve then eliminates the constraints: simple equalities `x = E` are substituted everywhere and propagated to predecessors (with a check that `E` does not contain `x`, an occurs check protecting soundness), arithmetic constraints are canonicalized as integer-weighted sums, memory updates are compared using the aliasing rules, and memory expressions are split at function calls. Any residual constraint is a reported mismatch, real or a false alarm. The inference is incomplete by design in two ways: every target branch must correspond to a source branch (so loop unrolling mostly fails), and all constraints must be equalities (no inequalities).

**[7] Evaluation.** The prototype (10,500 lines of OCaml: about 2,000 for parsing and utilities, 1,000 for symbolic evaluation, 3,000 for the solver, the rest auxiliary) validated the compilation of GCC 2.91 (5,909 functions, about 4 million RTL instructions) and the Linux 2.2 kernel. Per-pass numbers for GCC: branch heuristics fail on 0%-3% of cases and 0.01%-3.5% of constraints remain unsolved, depending on the pass (register allocation and scheduling are essentially clean, loop unrolling and common-subexpression elimination are the worst); validating one pass over the whole compiler takes 7-17 minutes on a 400 MHz Pentium Pro, about four times the cost of the compilation itself (twice that again if RTL dumping and parsing are counted). Running the validator on GCC 2.7.2.2 examples surfaced known bugs in the register allocator and in loop unrolling as residual constraints.

**[8] Limitations and directions.** The Branch heuristics are the most fragile part and the least portable to other compilers; the cleaner fix is compiler cooperation, that is, annotating branches (or emitting the entire simulation relation), which would remove the guesswork. Loop-heavy optimizations need better simplifiers before the false-alarm rate is acceptable; loop unrolling is the main current failure. The validator covers intermediate passes only, not the parser or the code generator, and does not yet handle exception handling or reason about memory across function calls. A further direction is to use inferred relations to translate assertions and proofs about the source into proofs about the target, turning an ordinary compiler into a certifying one.

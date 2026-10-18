# Equivalence Checking of ML GPU Kernels

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:** Benjamin Driscoll, Anjiang Wei, Alex Aiken (Stanford University); Kshitij Dubey, Neeraj Kayal (Microsoft Research India); Rahul Sharma (Google DeepMind; work done at Microsoft Research)

**Source:** OOPSLA 2026

**Link:** https://doi.org/10.1145/3839470

**Code and data:** [Volta](https://github.com/willtunnels/volta); benchmarks and Agda proof at https://doi.org/10.5281/zenodo.21529230; implementation snapshot at https://doi.org/10.5281/zenodo.21945204

## Key insight

Confluence makes one symbolic execution sufficient to represent all schedules of a structured thread block under the paper's checked semantics. Kernel equivalence then reduces to equality of symbolic real-valued outputs, with completeness conditional on a complete expression-equality procedure.

## Basic idea

Volta is the first equivalence checker for GPU kernels: prior equivalence checking handles single-threaded programs and high-level tensor graphs, while hundreds of threads with fine-grained synchronization [1] do not decompose into single-thread checks. Volta's contract is conditional on an assumption it checks during symbolic execution: the input must be a structured CTA [2], meaning the thread count, tensor sizes, branch targets, and memory addresses are all statically known, and any other kernel is rejected with an exception; under this assumption tensor elements are modeled as reals [3], and one CTA of the optimized kernel is checked against the matching CTA of the reference. It symbolically executes the threads under a round-robin schedule [4], running each thread until a barrier; a per-address race context [5] records the reads, the last writer, and the threads that have not synchronized with them, so data races and stalled barriers (deadlocks) surface while the symbolic state is built. A confluence lemma [6], proved in Agda, makes the one-schedule result schedule-independent, which yields race/deadlock guarantees and sound, complete equivalence checking relative to a procedure that decides symbolic equality [7]. That procedure [8] canonicalizes each pair of output expressions to ratios of polynomials with min/max and exponential factors, and the paper proves decidability of identities of the form `Σ p_i(x̄)e^{h_i(x̄)} = 0` over multivariate real polynomials [9]. The Rust implementation works on PTX [10] and verifies hand-written reductions, matrix multiplications, and attention kernels, LLM-generated kernels, and TileLang/CUTLASS-generated kernels, with identity solving under 3 minutes per pair; it reports races in the deprecated warp-synchronous reduction versions and in five OpenMM and Megatron-LM kernels that have bug-fix commits, and it decides attention identities that the Z3 baseline cannot.

## Illustrative example: two softmax kernels

**The kernels.** Our two-element example uses exactly two threads, initialized input `x`, disjoint output `y`, and a two-element shared buffer. The reference stores two exponentials, synchronizes, and divides. These handwritten PTX fragments illustrate the computation Volta analyzes; register declarations and parameter loading are omitted:

```ptx
// %rd10 = x, %rd11 = y; %r20 = address of shared buf[2]
mov.u32        %r1, %tid.x;
shl.b32        %r2, %r1, 2;             // tid * 4
mul.wide.u32   %rd1, %r1, 4;
add.s64        %rd2, %rd10, %rd1;
ld.global.f32  %f1, [%rd2];             // x[tid]
mul.f32        %f2, %f1, 0f3FB8AA3B;    // x[tid] * c; c approximates log2(e)
ex2.approx.f32 %f3, %f2;                // 2^(c * x[tid]), idealizing ex2
add.u32        %r3, %r20, %r2;          // address of buf[tid]
st.shared.f32  [%r3], %f3;
bar.sync       0;                       // __syncthreads()
ld.shared.f32  %f4, [%r20];             // buf[0]
ld.shared.f32  %f5, [%r20+4];           // buf[1]
add.f32        %f6, %f4, %f5;           // den
ld.shared.f32  %f7, [%r3];              // buf[tid]
div.rn.f32     %f8, %f7, %f6;
add.s64        %rd3, %rd11, %rd1;
st.global.f32  [%rd3], %f8;             // y[tid]
```

The optimized kernel recomputes the denominator per thread and drops both the shared buffer and the barrier:

```ptx
// %rd10 = x, %rd11 = y
mov.u32        %r1, %tid.x;
xor.b32        %r2, %r1, 1;             // 1 - tid
mul.wide.u32   %rd1, %r1, 4;
add.s64        %rd2, %rd10, %rd1;
ld.global.f32  %f1, [%rd2];             // x[tid]
mul.wide.u32   %rd3, %r2, 4;
add.s64        %rd4, %rd10, %rd3;
ld.global.f32  %f2, [%rd4];             // x[1 - tid]
sub.f32        %f3, %f2, %f1;
mul.f32        %f4, %f3, 0f3FB8AA3B;    // (x[1 - tid] - x[tid]) * c
ex2.approx.f32 %f5, %f4;                // 2^(c * (x[1 - tid] - x[tid]))
mov.f32        %f6, 0f3F800000;         // 1.0
add.f32        %f7, %f6, %f5;           // d
rcp.approx.f32 %f8, %f7;                // 1 / d
add.s64        %rd5, %rd11, %rd1;
st.global.f32  [%rd5], %f8;             // y[tid]
```

**Schedule and races.** The round-robin scheduler [4] runs thread 0 to the barrier (its write of buf[0] is recorded), then thread 1; the barrier releases when every thread in its wait set has arrived, the recorded accesses are cleared, and no race is reported between the write of buf[1] and thread 0's later read. Without the barrier, thread 1's write to buf[1] and thread 0's read of it are unsynchronized. In the formal race model [5], whichever access occurs second detects the conflict. Confluence [6] means this outcome holds for every schedule, not just the round-robin one.

**Equality proof.** Let `c` be the exact real value of the float literal `0f3FB8AA3B`, and let `α = c*ln(2)*x[0]` and `β = c*ln(2)*x[1]`. This accounts for the literal being an approximation to `log2(e)`. Under idealized real arithmetic, the reference computes `y[0] = e^α/(e^α + e^β)`; the optimized thread 0 computes `y[0] = 1/(1 + e^{β−α})`. The decision procedure [8] cross-multiplies the two ratios and merges the product of exponentials `e^{β−α}·e^{α}` into `e^{β}`, giving `e^α + e^β` on both sides. The two kernels are not bit-wise equal in floating point, since the formulas round differently; equality is proved over the reals [3], and more general exponential identities require the normalization in [9].

**Deadlock.** If all unfinished threads are blocked and no barrier satisfies its release condition [4], Volta reports a deadlock. Different barrier sets alone do not imply deadlock: disjoint sets, for example, can release independently.

## Concepts and terms

**[1] GPU execution model and barriers.** A grid of cooperative thread arrays (CTAs, or thread blocks) runs on streaming multiprocessors; the launch specifies each CTA's thread count, with threads grouped into 32-thread warps. Threads have private registers and share a CTA-wide shared memory; all CTAs share global memory. Threads execute independently unless synchronized: `syncthreads` (PTX `bar.sync`) is a CTA-wide barrier, `syncwarp` (PTX `bar.warp.sync`) subsets one warp, and tensor-core instructions such as `mma.sync` synchronize a warp. Missing synchronization causes data races; excess synchronization costs performance.

**[2] Structured CTA.** The class of kernels Volta analyzes: the number of CTAs and threads is known, tile sizes and tensor sizes are statically known, and for every thread, given its thread id, all branch targets and memory addresses are statically known, so each thread's execution reduces to a straight line of instructions. Kernels with data-dependent control flow (top-k, atomics) fall outside the class, and Volta checks the assumption and raises an exception instead of guessing. The implementation checks `blockIdx = 0` under a uniform-CTA assumption. This alone does not prove other block indices, especially boundary blocks; a whole-grid claim needs that assumption justified or additional CTA checks. Transformations that redistribute work between CTAs are outside the method.

**[3] Real-valued semantics.** Tensor elements are treated as exact real numbers because kernel optimizations reorder arithmetic. This is a mathematical abstraction, not IEEE floating-point semantics or the literal behavior of `--ffast-math`, whose operations still round; acceptance gives neither bitwise equivalence nor a bound on numerical error. Floating-point width conversions are the identity, saturation and ReLU are min/max, and square root and trigonometric functions are unsupported because they constrain their arguments.

**[4] The program language and its dynamics.** A kernel is modeled as a parallel composition of thread programs; statements assign constants, apply a pure binary operator (which can itself hide control flow, such as max), copy registers, read or write shared memory, or synchronize a set I of thread ids. The scheduling rule advances any thread not blocked at a barrier, and the synchronization rule releases the threads of I only when every thread in I either waits at I or has returned. A deadlock occurs when unfinished threads remain but neither a thread step nor a barrier release is possible; this models `syncthreads` as I = all threads and warp barriers as a subset of a warp.

**[5] Symbolic execution and the race context.** Registers and shared memory hold symbolic real expressions. For each address the context X stores, for every thread, the set of threads it has not synchronized with since its last read, together with the last writer and the set of threads not synchronized with that writer. A read races when its thread has not synchronized with the last writer, and a write races when its thread has not synchronized with the readers or the last writer; a racing access moves the execution to the error state ⊥. A release on I clears I from the unsynchronized sets of every thread in I, and from the last writer's set when the writer is in I. Since the round-robin run executes real schedules symbolically, races and deadlocks are found as the state is built.

**[6] Confluence.** The paper's core lemma, verified in Agda: any two schedules from one state extend to a common state, because the checked dynamics has a one-step diamond property up to reflexive closure and error or stuck states absorb. Hence all schedules either produce the same output state or all raise an error, one run represents every schedule, and the checked semantics agrees with a semantics without race checking on completed runs.

**[7] Guarantees.** Within the formal scheduling and memory model, successful checked execution establishes race and deadlock freedom, and reported errors have corresponding unchecked executions. If a program both races and deadlocks, the checked execution may report only one kind of error. The execution length is linear in the number of executed instructions, apart from the cost of maintaining contexts and symbolic expressions. Equivalence checking is sound and complete for structured CTAs relative to the expression-equality procedure: the kernels agree on all real inputs exactly when the procedure says the symbolic outputs are equal. The confluence lemma is the only part that was mechanically proved; the rest is on paper.

**[8] The decision procedure.** For each pair of corresponding output elements it checks whether the difference is identically zero. Expressions are canonicalized to a ratio of polynomials; a polynomial is a sorted list of terms with coefficients, a term is a sorted list of factors with exponents, optionally multiplied by `e^h` for a polynomial h, and a factor is a symbolic input, an uninterpreted function of rational functions, or a min/max of rational functions (sorted, deduplicated, and flattened when nested). Everything is hash-consed for a stable order; ratio equality is decided by a monomial-quotient test that handles softmax-style rescalings or by cross-multiplication; canonical forms are memoized for expressions referenced multiple times. Distributing multiplication over addition can blow up in principle, but the ML kernels verified have low multiplicative depth.

**[9] Decidability of identities with exponentials.** First remove each exponent's constant term: replace `p*exp(h)` by `(p*exp(h(0)))*exp(h-h(0))`, then merge terms with identical exponent polynomials. For the resulting pairwise distinct exponents with `h_i(0) = 0`, `Σ p_i(x̄)e^{h_i(x̄)} = 0` identically if and only if every coefficient polynomial p_i is zero. Distinctness without normalization is insufficient: `e^{x+1} - e*e^x` is identically zero. In one variable, dividing by the eventually largest exponential makes the other terms decay, forcing its polynomial coefficient to vanish; induction handles the rest. The multivariate proof restricts inputs to generic lines, using Schwartz-Zippel to preserve the needed polynomial distinctions. The theorem covers polynomial exponents, not arbitrary nested exponentials or identities involving min/max; the implementation's simplification of those larger classes is not a completeness proof.

**[10] Implementation.** Volta is written in Rust and reads PTX ISA 9.1 plus a specification of the grid dimensions, tensor locations and sizes, and which output tensors to compare. Constants are GMP arbitrary-precision rationals, constant folding simplifies min/max with infinities as expressions are built, and memory cells remember the width of the last store and require matching reads. Branches and addresses are resolved statically, and anything else makes Volta reject the program as not a structured CTA. Supported PTX includes `bar.sync`, `bar.warp.sync`, `shfl.sync`, `activemask`, `ldmatrix`, `mma.sync`, and `wmma`, and arithmetic including addition, multiplication, division, reciprocal, fused multiply-add, exponentiation, max, min, and float-width conversions. The simulator is single-threaded and emits one verification condition per output element.

**[11] Evaluation and comparisons.** Solved verification conditions for causal-masking attention drop under 0.2 s because both sides reduce to the same expression during symbolic evaluation and the cache is reused, while the FlashAttention pairs need about 154 s each to reconcile naive and online-softmax forms. The paper reports verification of an LLM-generated Conv2D kernel optimized over 13 rounds, and separately describes out-of-bounds shared-memory reads found during this work. Those reads returned zero without crashing on the tested Ampere, Hopper, and Blackwell GPUs and escaped Compute Sanitizer, but Volta rejects them; the paper fixes the example by moving the bounds guard before the load. Against FaialAA, the state-of-the-art race checker, Volta is more precise (symbolic evaluation resolves constant indices, so FaialAA's canonical spurious race is not reported) and finds every race FaialAA finds in the OpenMM and Megatron-LM test set, which Volta then proves absent in the bug-fix commits; FaialAA additionally covers kernels outside structured CTAs, which Volta rejects. Against Z3, Volta's median per-element solve times are far lower because canonical forms are memoized and reused across output elements, and Z3 fails on the attention identities even when given the axiom `e^x·e^y = e^{x+y}`; the first query of a run pays a one-time analysis of expression reference counts.

# Sound and Complete Solving for Multi-width Parametric Bitvectors via Principled Reductions

**Summary by:** GPT 6 Astra

**Author:** Siddharth Bhat, Léo Stefanesco, George Rennie, John Regehr, Tobias Grosser

**Source:** OOPSLA 2026, Proceedings of the ACM on Programming Languages 10, article 379

**Link:** https://doi.org/10.1145/3839511

**Code:** [Lean-MLIR / Blase](https://github.com/opencompl/lean-mlir/tree/main/Blase), [paper artifact](https://doi.org/10.5281/zenodo.21764865)

## Key insight

Represent a value's logical width with a mask so that values of different symbolic widths can be processed in a common representation. This gives one solver query for all widths within a bound, and a finite-state decision procedure for an unbounded linear-bitwise fragment.

## Basic idea

Parametric bitvector formulas [1] quantify over widths as well as values, making enumeration of all bounded width combinations expensive. The paper reduces multiple widths to one carrier width using binary-encoded widths and masks that constrain each value to its logical width [2]. Fixing the carrier produces a single ordinary bitvector query covering the bounded domain [3]. For unbounded solving, a linear-bitwise fragment [4] instead represents widths directly as mask streams and translates operations into finite-state transducers [5]. Model checking [6] proves the resulting property for all widths, with different trust guarantees for the verified and unverified solver paths [7].

## Illustrative example

**The identity.** Sign-extending a word and truncating it back should recover the original word: `truncate(sext(x, small, large), small) = x`, provided `1 ≤ small ≤ large`. Sign extension repeats the original top bit, while truncation keeps only the low bits. For example, the 3-bit word `101` becomes `11101` at width 5, then returns to `101`. It denotes -3 under signed interpretation, but the theorem compares bit patterns.

**Choose a bounded carrier.** To cover every logical width in this example through 8, use a 9-bit carrier. The formal reduction requires the carrier to be strictly wider than every logical width, including intermediate width expressions. Represent `small`, `large`, and `x` as 9-bit variables, assert `1 ≤ small ≤ large ≤ 8`, and define `M(k) = (1 << k) - 1`. Also assert `x & M(small) = x`, excluding values with nonzero bits above their declared width.

**Translate the operations.** The sign bit is `x & (1 << (small - 1)) != 0`. Let `fill` be the carrier-width complement of `M(small)` when that bit is set, and zero otherwise. The sign-extended result is `extended = (x | fill) & M(large)`, and the truncated result is `back = extended & M(small)`. All shifts, complements, and arithmetic here operate at the carrier width. At `small = 3`, `large = 5`, and `x = 5`, the two masks are 7 and 31, `extended = 29`, and `back = 5`.

**Make one query.** Conjoin the input constraints with `back != x` and ask a fixed-width solver whether the result is satisfiable. It is unsatisfiable: the fill has no bits in `M(small)`, and `small ≤ large` means the final masking cannot remove any original bit. The width variables remain symbolic within this one query; there is no external loop issuing a query for each pair of widths. This establishes the identity only within the stated bound.

**Remove the bound for this fragment.** The same identity uses only supported width-changing and bitwise operations, so the unbounded route applies. Read bits least-significant first. Width 3 is represented by the mask stream `1,1,1,0,0,...`; width 5 by `1,1,1,1,1,0,...`. A sign-extension transducer remembers the last original bit and repeats it through the extension positions; truncation masks those positions away. An equality transducer records whether any relevant output bit differs. Compose these machines with the width constraints and check that no valid input can reach a mismatch. The machine has finitely many states even though its input streams can encode arbitrarily large widths.

## Concepts and terms

**[1] Parametric bitvectors (PBV).** A word of width `w` contains `w` bits and arithmetic at that width wraps modulo `2^w`. PBV formulas allow width variables ranging over natural numbers; a bitvector's type depends on its width expression. `PBV_n` has `n` width variables; with no width variables, `PBV_0` is ordinary fixed-width reasoning. Operations such as addition require compatible operand widths. Zero-width words have one empty value; the example assumes positive widths so its sign-bit expression is defined without a special case.

**[2] Common-carrier encoding.** Choose a carrier width `o` greater than the largest logical width expression under consideration. Store each width as an `o`-bit binary number and each value as its zero-padded `o`-bit representation. A width-`w` input satisfies `x & M(w) = x`. Translate an operation at the carrier width and mask its result back to its logical width, restoring the intended modular arithmetic. For example, width-`w` addition becomes `(a + b) & M(w)`. Width expressions themselves must fit without overflow; bounding input widths alone is insufficient if an intermediate concatenation adds their widths.

**[3] Bounded solving and equisatisfiability.** Translate the negation of the desired theorem into QF_BV, the quantifier-free theory of fixed-width bitvectors. Free variables in this satisfiability query include the encoded widths, so one solver invocation searches all allowed width assignments. Equisatisfiability means that a counterexample exists in the original bounded problem exactly when one exists in the translated problem. The translation has linear formula-size growth, avoiding enumeration's exponential number of queries; this does not make the remaining solver query polynomial-time. A result for a finite bound is not an unbounded-width proof.

**[4] Linear-bitwise fragment.** The unbounded procedure handles the supported combination of addition, subtraction, multiplication by constants, bitwise operations, comparisons, and zero/sign extension or truncation. It is not a decision procedure for the full unbounded theory with arbitrary multiplication, variable shifts, and all width expressions. In particular, the bounded translation's variable shift for constructing `M(w)` cannot simply be sent to the automata solver. Width masks supply an alternative representation: a finite word is a low-ones mask exactly when `m & (m + 1) = 0`, with arithmetic at that word's width.

**[5] Mask streams and finite-state transducers.** A width `w` becomes a stream whose bit `i` is 1 exactly when `i < w`; ordinary values retain their binary bits. A finite-state transducer consumes a tuple of input bits at each position, updates a finite state, and emits an output bit. Bitwise AND needs no remembered state; addition remembers a carry; equality remembers whether a mismatch has occurred. Operations are composed into a machine for the whole predicate. Results are masked to their logical widths, and width constraints restrict which encodings represent admissible inputs. This construction does not enumerate concrete widths.

**[6] Model checking and k-induction.** Model checking asks whether the predicate machine can produce false in a reachable state. The verified path uses k-induction: check initial executions through a finite depth, then check that a sufficiently long safe sequence cannot step into failure. Cycle-breaking constraints remove repeated-state paths that would otherwise obstruct completeness. For the finite-state encoding, the paper proves a sound and complete procedure; resource limits can still make an actual run inconclusive. The induction depth counts positions in a machine proof, not a chosen maximum bitvector width.

**[7] Mechanization and trust boundaries.** The unbounded `bv_multi_width` tactic reflects a Lean goal into typed syntax, constructs its transducer, and connects checked certificates to a proof about the original goal. Its verified k-induction path calls the SAT solver CaDiCaL and checks its LRAT certificates, clause-based proofs of unsatisfiability, using `bv_decide`'s verified checker. Native checker execution trusts Lean's compiler as well as its kernel. The alternative rIC3 backend is unverified in the paper. The bounded solver also ends in `bv_decide`, but its preceding multi-width reduction pipeline is unverified (Section 6.3). A verified last-stage solver therefore does not make every frontend or backend verified. Applying these bitvector procedures to compiler rewrites additionally requires a correct encoding of the language's semantics.

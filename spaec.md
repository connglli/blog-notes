# Semantic Program Alignment for Equivalence Checking

**Author:**
- Berkeley Churchill, Oded Padon, Alex Aiken (Stanford University)
- Rahul Sharma (Microsoft Research India)<br/>

**Source:** PLDI 2019 (pages 1027-1040)

**Link:** https://doi.org/10.1145/3314221.3314596<br/>

**Code:** [pldi19-equivalence-checker](https://github.com/bchurchill/pldi19-equivalence-checker); release at https://doi.org/10.5281/zenodo.2646657

## Key insight

Syntactic alignments that pair loop iteration i of one program with iteration i of the other break under vectorization, unrolling, and peeling. What is needed is "a semantically guided alignment that relates the two programs in a way that is designed to make the final proof of equivalence as simple as possible": guess a weak relation on machine states, run both programs on test inputs, pair the states that satisfy it, and lift the resulting trace alignment into a product program that SMT can check.

## Basic idea

Product-program equivalence checking needs an alignment that pairs the transitions of one program with transitions of the other, and syntax-based alignments fail when optimizations such as vectorization, unrolling, and peeling make loop iterations correspond many-to-many. SPA aligns executions instead: the user supplies test cases, SPA guesses a weak alignment predicate [2] over pairs of machine states, runs both x86-64 functions on each test, and pairs the states that satisfy the predicate to obtain a trace alignment [3]. The paired prefixes lift back to syntax as a program alignment automaton [4], whose nodes are pairs of program points and whose transitions are labeled with one path in each program; the automaton is simplified, and a held-out test set rejects automata that overfit the training traces. Each node carries an invariant learned from the observed states [5], and equivalence reduces to relational Hoare triples discharged by an SMT solver: every transition preserves the invariants, every pair of feasible paths from a node is covered by some transition (uncovered pairs must be infeasible), no cycle lets one program never advance, and the exit invariant implies equal return registers and heaps [6]. Because the alignment is built from behavior, the same automaton can pair one target iteration with several rewrite iterations or with a fragment of an iteration, which is what makes vectorized loops provable; a soundness lemma and its corollary show that automata passing all proof obligations imply equivalence for all inputs. SPA verified the hand-vectorized glibc strlen against the simple reference and 55 of 56 vectorization benchmarks derived from TSVC (the one failure was a solver timeout), including warm-up loops whose trip counts depend on pointer alignment.

## Illustrative example: doubling an array

**The functions.** The target processes one element per iteration; the rewrite peels one element when the length is odd and then handles pairs. (In the tool these are x86-64 functions; the loop structure is what matters here.)

```text
T:  for (i = 0; i < n; i++) a[i] *= 2;

R:  if (n % 2 == 1) { a[0] *= 2; a++; n--; }
    while (n) { a[0] *= 2; a[1] *= 2; a += 2; n -= 2; }
```

**Traces and the alignment predicate.** With the test input n = 5 and a = [1, 2, 3, 4, 5], the target's trace visits its loop head with i = 0, 1, 2, 3, 4, 5, and the rewrite's trace, after the peel, visits its loop head with remaining lengths 4, 2, 0 and passes mid-body states after processing elements 1 and 3. The guessed alignment predicate is `base + 4i = p`, where base is the array start, i is the target's index, and p is the rewrite's pointer. It holds on the pairs (target i=0, rewrite entry), (i=1, rewrite at element 1), (i=2, rewrite mid-body after element 1), (i=3, rewrite at element 3), (i=4, rewrite mid-body after element 3), and (i=5, rewrite exit). A trace alignment [3] is the set of such prefix pairs collected over all test cases.

**The automaton.** Lifting consecutive aligned pairs to syntax gives a program alignment automaton [4] with nodes (q1, q1') for the entries, (q2, q2') for the loop heads, and (q3, q3') for the exits, and three kinds of transitions:

```text
(q1, q1') -> (q2, q2')   ab ; a'    when n is odd   (T: init plus one iteration; R: the peel)
(q1, q1') -> (q2, q2')   a  ; b'    when n is even  (R: the skipped peel)
(q2, q2') -> (q2, q2')   bb ; c'                    (T: two iterations; R: one pair body)
(q2, q2') -> (q3, q3')   c  ; d'                    (both exit tests)
```

where b is the target's loop body, a' the peel, b' the skip, c' the pair body, and c, d' the failing guards. Simplification deletes nodes and transitions the training traces do not need; in the paper's experiments it reduces the node count by about 3.9 times and the edge count by about 3.7 times.

**Invariants.** The observed states at (q2, q2') satisfy `p - 4i = base`, `n - i = n'`, `i <= n`, and heap equality (the elements already processed have been doubled in both arrays). The entry node gets the equality of input states, and the exit node the equality of the final heaps, which is the observable output here since both functions write only memory.

**Checks.** The self-loop obligation [6] says: assume the invariants at (q2, q2'); the target doubles a[i] and a[i+1] and advances i by 2, while the rewrite doubles the two elements at its pointer and advances p by 2 and decreases n' by 2; all the invariants are restored. The coverage obligations say that from (q2, q2') the pair (target continues, rewrite exits) is infeasible, since n' = 0 contradicts i < n through `n - i = n'`, and symmetrically for (target exits, rewrite continues); the pairs that stay feasible are exactly those matched by the two transitions above. At the exit the invariants imply the heaps are equal, which is what the equivalence claim needs. All of these go to the SMT solver as relational Hoare triples.

**Why the predicate matters.** If the alignment predicate were true only at the trace endpoints, every test would create a fresh start-to-exit transition covering its whole trace, which is an overfitting automaton and is rejected by the held-out tests. If the predicate were too strong, required pairs such as the target's mid-loop states with the rewrite's mid-body states would be missed and no proof would be found. SPA searches a small grammar of predicates (linear relations between a register or stack slot of each side with coefficients 1, 2, 4, 8, or 16, conjoined with heap equality) and tries them until one yields a viable automaton.

## Concepts and terms

**[1] Product programs and the two-stage view.** Equivalence checking is commonly split into aligning the two programs into a product program, then proving invariants of the product; effort moved into one stage is saved in the other. A sequential composition of the whole functions gives no help (the loops must be summarized), while pairing the loops' iterations one-to-one only works when the iterations correspond, which vectorization, unrolling, and peeling destroy. SPA's product program is implicit in the automaton. Equivalence means: run the two functions from identical machine states, and either both terminate with identical heaps and output registers, or each program either errors or loops forever.

**[2] Alignment predicate.** A weak predicate over pairs of machine states guessed before any proof attempt, used to decide which states of the two traces should be paired. The grammar used is `(c1*v1 - c2*v2 = k) ∧ (omega = omega')`, where v1, v2 are registers or stack slots of the two programs, c1, c2 are from {1, 2, 4, 8, 16} with one of them equal to 1, k is chosen by looking for differences that recur across traces, and omega = omega' asserts equal heaps. Successful predicates typically match a pointer or counter of one function with a pointer or counter of the other; the powers of two appear because byte-addressed array indexing multiplies counters by element sizes.

**[3] Trace alignment.** For each test case both functions are executed, and every pair of prefixes whose final states satisfy the alignment predicate (plus the beginning and the end, which are always aligned) is added to the alignment. The relation can be many-to-many and the pairing edges may cross. Consecutive pairs of alignment edges that do not cross delimit one path in each program, and these pairs are the corresponding paths that label the automaton's transitions.

**[4] Program alignment automaton (PAA).** An automaton whose nodes are pairs of program points with an invariant each, and whose transitions from (u, u') to (v, v') are labeled with a path P in the first program from u to v and a path Q in the second from u' to v', at least one of which is nonempty. It accepts a pair of traces when the concatenation of the transition labels matches the paths the traces take, so the automaton is an NFA over pairs of paths. Construction adds a transition per aligned pair of segments; simplification removes nodes without self-loops (splicing their transitions) and transitions whose labels are extensions of another transition's labels, while keeping the training traces accepted. A membership check on a held-out test set rejects overfitting automata cheaply, before any SMT queries.

**[5] Invariant learning.** For each node, the observed machine-state pairs are mined for conjectures: linear equalities via the nullspace of a matrix over the ring of 64-bit bitvectors (computed with SageMath, with a pre-pass and 25 sampled rows for speed, then validated on the rest of the data), inequalities by finding the strongest bounds that hold, modulo equalities via the greatest common divisor of the observed differences, and heap equality excluding a minimal set of locations. A Houdini-style fixed point then removes every conjunct that cannot be proven by induction on the transitions, leaving the invariants that the final proof uses.

**[6] Proof obligations.** Four properties make a PAA a valid equivalence proof: (1) each transition s -> t satisfies `{phi_s} P ; Q {phi_t}` in relational Hoare logic; (2) coverage, meaning that any pair of feasible paths from a node not matched by a prefix pair of some transition is infeasible (`{phi_s} P ; Q {false}`); (3) no cycle of transitions in which every target-side path is empty, and symmetrically for the rewrite side, so no cycle lets one program never advance; and (4) the final node's invariant implies equal output registers and identical heaps. A lemma shows that if a node's invariant holds on a pair of states and the first function terminates within m basic blocks, then the second terminates too and reaches the final node's invariant, by induction on m; its corollary is soundness of the checker. Obligations go to Z3 and CVC4 (the tool uses whichever of two memory models and two solvers finishes first, with a 30-minute timeout per obligation).

**[7] Evaluation.** The benchmark suite is 28 TSVC functions with integer types (floating point systematically replaced), each checked in two pairs: GCC -O1 against GCC -O3 and against clang -O3, for 56 benchmarks. SPA proves 55; the failure is a solver timeout on s351 compiled by GCC, a loop with five multiplications and ten memory dereferences per iteration. The generated automata have 3 or 4 nodes and 4 to 254 edges; discharging all proof obligations takes a median of 45 CPU hours (minimum 2.5, maximum 1166 for s351-clang, whose end-to-end cloud cost was $11.66 against $0.45 for a typical problem). The glibc strlen case study, the hand-vectorized implementation shipped since 2.10.1 against the obvious one-byte-at-a-time reference, takes 3.3 minutes end to end; it is the first fully automatic black-box proof of a real hand-vectorized library routine, and the alignment predicate pairs the two pointers into the string. The paper also verifies the loop benchmark of a prior black-box checker in 34.4 minutes. Between 182 and 3318 alignment predicates are tried per benchmark, 3.1% on average lead to viable automata, and every benchmark has at least 8 viable automata.

**[8] Limitations.** The only heap invariants are equalities except for a finite set of locations, so transformations that reorder an unbounded number of memory writes (loop splitting, fusion, interchange, tiling) are out of scope, and so are reordered traversals. A correspondence that depends on an unbounded input cannot be represented: the paper's example aligns an inner loop of m iterations with one iteration of the other program, which would require summarizing the inner loop before alignment (a variant with m restricted to finitely many values works, one PAA transition per value). Page faults are not modeled, so the checker ignores out-of-bounds reads when the write sets still agree, which is exactly what allows the strlen verification, since the vectorized code deliberately reads past the null terminator within a memory page. Floating-point operations are treated as uninterpreted functions.

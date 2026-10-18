# Interactive Bitvector Reasoning using Verified Bit-Blasting

**Summary by:** GPT 6 Astra

**Author:** Henrik Böving, Siddharth Bhat, Luisa Cicolini, Alex Keizer, Léon Frenot, Abdalrhman Mohamed, Léo Stefanesco, Harun Khan, Joshua Clune, Clark Barrett, Tobias Grosser

**Source:** OOPSLA 2025, Proceedings of the ACM on Programming Languages 9, article 389

**Link:** https://doi.org/10.1145/3763167

**Code:** [Lean, including `bv_decide`](https://github.com/leanprover/lean4), [Lean-MLIR](https://github.com/opencompl/lean-mlir), [paper artifact](https://doi.org/10.5281/zenodo.15762083)

## Key insight

Use an external SAT solver to find a proof, but verify the reduction to SAT and the solver's certificate inside Lean's proof infrastructure. A shared bitvector library connects that procedure to ordinary integer code, interactive proofs, and width-generic simplification lemmas.

## Basic idea

`bv_decide` proves propositions about fixed-width bitvectors [1] within Lean, including goals expressed using its machine-integer types. It negates the goal, simplifies the hypotheses, and bit-blasts [2] the remaining expressions into an and-inverter graph [3]. A verified conversion produces a conjunctive-normal-form formula for a SAT solver [4], whose unsatisfiability certificate is checked rather than trusted [5]. Boolean reflection [6] connects the successful checker computation to the original theorem; native execution adds Lean's compiler to the trusted base. Developers can combine this procedure with induction and other proofs, but fixed-width bit-blasting alone does not prove a theorem for every possible width [7].

## Illustrative example

**State the property.** A byte counter advances until it reaches its ceiling, then resets to zero. This is a smaller state machine than the paper's elevator example:

```lean
import Std.Tactic.BVDecide

def advanceCounter (position ceiling : UInt8) : UInt8 :=
  if position = ceiling then 0 else position + 1

example (position ceiling : UInt8) (h : position ≤ ceiling) :
    advanceCounter position ceiling ≤ ceiling := by
  simp only [advanceCounter]
  bv_decide
```

`UInt8` values range from 0 to 255 and addition wraps modulo 256. The hypothesis matters: with position 4 and ceiling 2, the function returns 5, outside the claimed bound.

**Reduce to a counterexample search.** After unfolding the function and translating `UInt8` operations to their bitvector representation, the solver searches for bytes `p` and `c` satisfying `p ≤ c` and `(if p = c then 0 else (p + 1) mod 256) > c`. This is unsatisfiable: equality selects zero; otherwise `p < c ≤ 255`, so incrementing `p` cannot wrap and cannot exceed `c`.

**Build the circuit.** Represent `p` and `c` by eight Boolean inputs each. Equality compares their bits; unsigned comparison orders them by their highest differing bit. Incrementing `p` uses a carry chain: start with carry 1, emit `p_i XOR carry_i`, and propagate `p_i AND carry_i`. Conditional gates select zero or the incremented value. The complete circuit outputs true exactly for a counterexample. Shared input bits and subexpressions are represented once in the AIG.

**Solve and check.** Give each circuit gate a Boolean variable and constrain its value. For example, a gate `z = x AND y` contributes the clauses `(NOT z OR x)`, `(NOT z OR y)`, and `(z OR NOT x OR NOT y)`. Assert that the counterexample output is true. CaDiCaL searches this CNF and, for an unsatisfiable query, supplies an LRAT certificate deriving a contradiction. Lean's verified checker validates the certificate against the generated CNF; the proved correctness of the translations carries that result back to the counter theorem. Simplification may remove parts of this work before SAT solving is needed.

**Reuse the theorem.** Ordinary induction on the number of counter updates can use this one-step result to preserve the bound for arbitrarily many updates. That unbounded number of updates does not change the fact that each state contains fixed 8-bit values. Proving the same statement with a symbolic bitwidth is a different task.

## Concepts and terms

**[1] Bitvectors and machine integers.** `BitVec w` is a natural number below `2^w`, paired with evidence of that bound. Ordinary arithmetic wraps modulo `2^w`; signed operations interpret the same bits in two's complement. Lean's `UInt` and signed-integer families are connected to this representation by proved rewrite rules. The representation is a bounded number, not an explicit list of bits, permitting efficient execution while supporting bit-level proofs.

**[2] Bit-blasting and preprocessing.** Replace a finite-width operation with a Boolean circuit implementing its exact semantics. Bitwise operations act independently on corresponding bits; arithmetic operations use circuits such as ripple-carry adders. Before building those circuits, proved rewrites canonicalize operations, simplify expressions, and use known hypotheses. For instance, arithmetic negation can become complement plus one. The library's circuit-correctness lemmas are proved for arbitrary widths even though a particular SAT query has concrete widths.

**[3] And-inverter graph (AIG).** An acyclic circuit built from inputs, constants, AND gates, and complemented connections. Other Boolean operations can be expressed using these primitives. The implementation stores nodes in an array, with proofs that every gate refers only to earlier nodes. Verified caches reuse existing gates and previously translated bitvector expressions. Adding a circuit preserves existing nodes, allowing a proof about an earlier subcircuit to remain valid. Lean can update uniquely owned arrays in place while retaining functional semantics.

**[4] CNF, SAT, and equisatisfiability.** A literal is a Boolean variable or its negation; a clause is a disjunction of literals; CNF is a conjunction of clauses. SAT asks whether an assignment makes the formula true. The Tseitin translation introduces gate variables and local defining clauses, avoiding expansion into a potentially exponential formula. The CNF is equisatisfiable with the asserted circuit: one has a satisfying assignment exactly when the other does, allowing assignments to the additional gate variables.

**[5] LRAT certificates.** LRAT is a proof format recording clause-inference steps with hints that make them efficient to check, ending with the empty clause, which is false under every assignment. CaDiCaL and certificate parsing or trimming are not trusted to establish unsatisfiability; a verified checker decides whether the supplied certificate proves it for the actual input CNF. A bad solver answer or malformed certificate cannot establish the theorem through a successful check unless a trusted component is wrong.

**[6] Boolean reflection and trust.** A proved theorem connects a Boolean program's result to a logical proposition: if the complete verification function returns true, the bitvector counterexample formula is unsatisfiable. The practical tactic evaluates that function as compiled Lean code and uses `ofReduceBool` to accept the computation result. Consequently it trusts Lean's compiler as well as its kernel, rather than replaying every certificate step through kernel reduction. This is distinct from trusting the external SAT solver's verdict.

**[7] Scope and interactive use.** Bit-blasting requires concrete widths and can still exhaust time or memory. Unsupported subterms may be abstracted as unconstrained bitvector symbols, so a reported countermodel involving them can be spurious; unfolding or proving additional facts can resolve it. Separate library techniques handle width-generic bitwise identities, algebraic normalization, and ordinary inductive proofs. The paper does not turn all symbolic-width bitvector reasoning into a single complete bit-blasting procedure, nor does a bitvector theorem alone establish LLVM's poison or undefined-behavior semantics.

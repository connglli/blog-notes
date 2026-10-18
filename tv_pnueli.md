# Translation Validation

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:**

* Amir Pnueli, Michael Siegel, Eli Singerman (Weizmann Institute of Science)<br/>

**Source:** TACAS 1998 (LNCS 1384, pages 151-166)

**Link:** https://doi.org/10.1007/BFb0054170<br/>

## Key insight

Translation validation checks each generated program against its source rather than proving the compiler correct for every input. The proposed architecture separates an analyzer that constructs a refinement proof from a small checker that validates the proof.

## Basic idea

Translation validation checks the result of each compiler run, independently of how the code generator produced it. The proposed tool separates an analyzer that seeks a proof or counterexample from a small proof checker [1]; this is not a decision procedure for arbitrary programs. Source and target share one semantic framework, synchronous transition systems [2]: typed variables, some volatile (their domains contain an "absent" value, modeling signals) and some persistent (memorization variables for the previous-value operator), an initial condition, a transition relation, and a set of observable variables; correct implementation is refinement [3], a clocked mapping that carries every concrete computation to an abstract computation agreeing on observables. Refinement is proved by an inductive clocked refinement mapping [4], a generalization of simulation with refinement mappings: it maps concrete states to abstract states, agrees with the initial conditions, and maps every concrete transition to an abstract transition; made syntactic, it becomes a substitution that replaces each abstract variable by an expression over concrete variables, plus an invariant over the concrete system, which rule REF turns into five verification conditions [5]. The novel part is that the substitution and the invariant need not be invented for the SIGNAL-to-C case: strong assumptions about the structure of the generated iteration function (calculate clock expressions, read inputs, compute and write outputs, update previous-value variables) let an algorithm compute the clock expression of each variable, the observation point, the substitution (a variable is visible only at the observation point and only when its clock is on), and the accumulating invariant [6]. The authors illustrate the whole process on the MUX example and report that all premises of rule REF were verified with the TLV proof system; the approach is expected to apply whenever one source iteration corresponds to one target iteration, as in most code generators for synchronous languages [7].

## Illustrative example: validating a gated counter

**The two systems.** The source is described by an abstract STS `A` and the generated C code by a concrete STS `C`, over the shared variables `x` (an integer input signal), `y` (an integer output signal), and `m`, a persistent memorization variable holding the previous output. One abstract step: when the previous output `m` is at most 2, a new input is present in `x`; the new output is `x` when it is present and `m + 1` otherwise; and `m` remembers the new output. The alternative, a stutter step, makes every signal absent and leaves `m` unchanged, letting the environment idle between steps. Formally, with `⊥` denoting absence and primed variables the successor state:

```text
A:  V = {x, y, m},  E = {x, y}
    initial:  m = 1 /\ x = ⊥ /\ y = ⊥
    step:     y' != ⊥ /\ (m <= 2 -> x' != ⊥) /\ (m > 2 -> x' = ⊥)
              /\ y' = (if x' != ⊥ then x' else m + 1) /\ m' = y'
         \/   x' = ⊥ /\ y' = ⊥ /\ m' = m          (stutter)
```

The generated iteration function reads the input only when the clock expression `h` is true, computes the output, updates the previous-value variable, and then loops:

```text
c0:  h = (m <= 2);            // compute the clock expression
c1:  if (h) read(x);          // read the input when its clock is on
c2:  y = (h ? x : m + 1);     // compute the output
     m = y;                   // update the previous-value variable
c3:  /* one abstract step has been computed; the observation point */
     goto c0;
```

The concrete STS `C` has variables `{x, y, m, h, pc}` and observable set `{x, y}`; its initial condition is `pc = c0 /\ h = false /\ m = 1 /\ x = ⊥ /\ y = ⊥`, and it has one transition per program point, where `pres(U)` means that the variables in `U` do not change and the read at `c1` sets `x` to an arbitrary non-bottom value.

**The refinement substitution.** The clock expressions come from the loop's structure: `clk(y) = true` since `y` is assigned on every iteration, and `clk(x) = h` since the read of `x` is guarded by `h`. The substitution `σ` maps the memorization variable by identity and every other abstract variable to "visible at the observation point and only while its clock is on":

```text
m |-> m,   y |-> (if pc = c3 then y else ⊥),   x |-> (if pc = c3 /\ h then x else ⊥)
```

**The invariant.** A sufficient concrete invariant is `inv = (pc = c1 \/ pc = c2 -> h = (m <= 2)) /\ (pc = c2 /\ h -> x != ⊥)`: `h` is current once computed, and a successful read has left `x` non-bottom.

**Checking the obligations.** Initiation (R3): at `pc = c0` the substitution makes `x` and `y` absent and `m = 1`, which is the abstract initial state. Propagation (R4): the interesting transition is `c2 -> c3`, which publishes one step. Before it the substitution makes `x` and `y` absent and `m` the previous output; after it `y` is the computed output, `x` is the input when `h` (present) and absent otherwise, and `m = y`. This is the progress disjunct: if `h`, then `y = x` and the input is present; if not `h`, then `inv` gives `m > 2` and `y = m + 1`; and `m' = y'` holds in both cases. The other transitions (`c0 -> c1`, `c1 -> c2`, `c3 -> c0`) change only invisible state, so they satisfy the stutter disjunct. Clockedness (R5): at `c3`, `y` keeps its concrete value and `x` keeps its value only if `h` is true; otherwise the substitution declares the observable absent. R1 and R2 are the standard invariant checks. Hence `C` refines `A`, and every run of the generated code implements the source program.

**The point of the structure.** Nothing in the substitution had to be guessed: the observation point is the point where one abstract step has been completed, each variable's clock expression is read off the guards on the paths that assign it, and the invariant accumulates the effects of the intervening actions. This fixed shape of generated synchronous code is what makes the process fully automatic.

## Concepts and terms

**[1] Translation validation.** The approach: instead of proving that a compiler always produces correct code, run the compiler and then verify that this particular target program correctly implements the submitted source program. The analyzer does the hard work (generating a proof script or a counterexample, a scenario where the target's behavior differs from the source's), and the separate, rudimentary proof checker re-verifies the script and provides the last seal of approval, which keeps the trusted component small. The paper is set in the Esprit SACRES project (safety-critical embedded systems), where the tool is expected to validate every run of the translator.

**[2] Synchronous transition systems (STS).** The common model for both languages: `A = (V, O, p, E)` with a set of typed variables `V`, an initial condition `O`, a transition relation `p(V, V')`, and a subset `E` of externally observable variables. A computation is an infinite state sequence whose first state satisfies `O` and whose consecutive pairs satisfy `p`. Variables are persistent or volatile; volatile variables model signals and their domains include a distinguished value `⊥` (absence). The SIGNAL encoding keeps the program variables as volatile variables and adds persistent memorization variables for subexpressions with the previous-value operator (`$`); a stutter disjunct in `p` lets the system idle at any step (all signals `⊥`, memorization unchanged), which makes the abstract system robust to being sampled at any asynchronous time. The C encoding adds a program counter `pc`, uses `pres(U)` predicates to say which variables a transition leaves unchanged, lets a read transition choose an arbitrary non-bottom input value, and models output writing by copying output variables into their memorization counterparts right before the observation point.

**[3] Refinement.** With abstract system `A`, concrete system `C`, and `E_A ⊆ E_C`, an interface mapping `I` maps each concrete state to an abstract state over the observables; it is clocked when each observable shared by the two systems either keeps its concrete value or is declared absent by `I`. `C` refines `A` relative to `I` when applying `I` to every concrete computation (pointwise, and restricted to the observable variables) yields an abstract computation; `C ⊑ A` holds when some clocked interface mapping works. The relation is meant to be as liberal as possible so that legitimate implementations (including ones that stutter) are admitted.

**[4] Refinement mapping and inductiveness.** A refinement mapping `f` maps concrete states to full abstract states (it extends an interface mapping), and is clocked when it preserves observables up to absence. It is inductive when (initiation) every initial concrete state maps to an initial abstract state, and (propagation) the image of every concrete transition is an abstract transition; an inductive clocked refinement mapping proves `C ⊑ A`. This is a generalization of the classical simulation-with-refinement-mapping technique (Abadi and Lamport); its semantic formulation needs the reachable concrete states, which motivates the syntactic form below.

**[5] Rule REF.** A substitution `σ` replaces each abstract variable by an expression over concrete variables and thus defines the state mapping syntactically; substituting into a formula replaces each abstract variable and handles primed variables by priming the replacement expressions. Rule REF proves `C ⊑ A` from an invariant `inv` over the concrete system and such a substitution, with five premises: R1 `O_C -> inv` (the invariant holds initially); R2 `inv /\ p_C -> inv'` (it is propagated); R3 `O_C -> O_A[σ]` (initiation); R4 `inv /\ p_C -> p_A[σ]` (propagation); and R5 `inv -> (σ-value = value \/ σ-value = ⊥)` for every observable variable (the mapping is clocked). The rule hides two existential quantifications ("find `inv` and `σ`"), normally left to the verifier's ingenuity; the invariant strengthens the induction to compensate for not knowing the reachable states. The paper checked the premises of its example with the TLV proof system.

**[6] Generating `inv` and `σ`.** There is no general algorithm for arbitrary systems, but translation validation knows the target came from one particular code generator, and the paper's generator produces a loop with fixed stages: calculate clock expressions, read inputs (conditioned on clocks), compute outputs, write outputs, update previous-value variables, with a designated observation point. Viewing the loop as a graph whose edges carry guards and actions, the clock expression for a variable is the disjunction of the guards on the paths that lead to assignments to it, and the substitution maps memorization variables to themselves and every other abstract variable `v` to "if `pc` is the observation point and `clk(v)` holds then `v` else `⊥`". The invariant accumulates facts about the initial values and the effects of the actions along the paths. For the paper's MUX example this yields `clk(FB) = h2`, `clk(N) = clk(ZN) = true`, the corresponding substitution, and an invariant that makes all premises provable. The full algorithm behind the clock expressions and the invariant, and the details of the proof checker and decision procedures, are deferred to the full version of the paper.

**[7] Scope and expectations.** The method as presented targets systems that are each a repeated execution of one loop body with a single source iteration corresponding to a single target iteration, which the authors expect of most code generators for synchronous languages (Esterel, Lustre, Statecharts, and also languages such as Unity). A translation validation tool-set must be tailored to the particular translator by following and modifying the paper's guidelines; in some cases it may help to augment the translator so that observation points are easier to identify. The concept itself is meant to be general, not limited to SIGNAL-to-C; most of the authors' difficulties came from the gap between the synchronous source and the asynchronous target.

**[8] Positioning.** The closest prior work, Cimatti et al. (CAV 1997), validates a translation between similar languages with a much simpler technique. Relative to proof-carrying code (Necula and Lee), the paper argues that translation validation is more general, thanks to its abstract computational model and refinement notion, and fully automatic, whereas proof-carrying code leaves the generation of the crucial verification condition to manual effort.

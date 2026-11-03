# A Hardware Design Language for Timing-Sensitive Information-Flow Security

**Summary by:** GPT 6 Astra

**Author:** Danfeng Zhang, Yao Wang, G. Edward Suh, Andrew C. Myers

**Source:** ASPLOS 2015; ASPLOS Influential Paper Award 2026

**Link:** https://doi.org/10.1145/2694344.2694372

**Code:** [SecVerilog](https://github.com/aferr/secverilog)

## Key insight

A secret can leak through when hardware finishes, not only through the value it returns. SecVerilog checks the information flow of control signals as well as data, using value-dependent security labels to permit carefully controlled hardware sharing.

## Basic idea

SecVerilog annotates Verilog wires and registers with information-flow labels [1]. Dependent labels [2] let a shared signal's permitted security level vary with the hardware's operating mode. A static type checker uses path conditions [3] to verify both explicit data flow and secret-dependent control. Its guarantee is timing-sensitive noninterference [4] for the modeled synchronous circuit and observation policy, not protection against every physical side channel.

## Illustrative example

**Set the policy.** A small controller serves either public or secret requests. Its public mode bit `mode` is 0 for public requests and 1 for secret requests. Two separate cache-status signals, `public_hit` and `secret_hit`, have labels `L` and `H`, respectively. Information may flow from `L` to `H`, but not from `H` to `L`.

**Share a signal carefully.** Give the controller's selected-hit signal the label `Class(mode)`, where `Class(0) = L` and `Class(1) = H`. In public mode, select only `public_hit`; in secret mode, select `secret_hit`. Under the path condition `mode = 0`, the public assignment requires `L <= Class(0)`; under `mode = 1`, the secret assignment requires `H <= Class(1)`. Both obligations hold.

**Check timing, not only payloads.** The controller's stall signal depends on the selected hit. It must therefore have the appropriate dependent label too. If a public request instead tests `public_hit OR secret_hit`, changing secret cache state can change whether that public request stalls. The checker encounters the impossible public-mode obligation `H <= L`, even if the returned public data is identical.

**Respect state transitions.** The example's selected hit is a combinational signal. A stored register reused across modes needs additional care: changing its label must not expose a secret value left from an earlier mode. Dependent labels are checked invariants, not permission to relabel arbitrary stored data as public.

## Concepts and terms

**[1] Information-flow label.** A security lattice specifies which flows are allowed. In the two-level example, a low observer may see public information but must not learn secret information through data or control. A conditional assignment can leak through its guard even when its assigned constant is public.

**[2] Dependent label.** A label expression can depend on program values, such as a selected cache partition or operating mode. The type system checks that assignments and changes to those values preserve the intended information-flow invariants. This permits more sharing than assigning every shared resource a fixed secret label.

**[3] Path-conditioned checking.** Generate security obligations under facts known on the current branch and discharge them with automated reasoning. The analysis also accounts for Verilog's blocking and nonblocking assignments and for dependencies introduced by control flow. Removing annotations yields ordinary synthesizable Verilog; labels need not become runtime tags.

**[4] Timing-sensitive noninterference.** For executions with the same permitted low inputs and appropriately equivalent initial state, changes to secrets do not change the low-observable behavior, including its cycle-level timing. The model assumes a fixed-frequency synchronous clock. Power analysis, physical probing, and unmodeled analog effects are outside the threat model; whole-system security also requires the software's timing policy to be respected.

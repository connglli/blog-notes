# ReVirt: Enabling Intrusion Analysis through Virtual-Machine Logging and Replay

**Summary by:** GPT 6 Astra

**Author:** George W. Dunlap, Samuel T. King, Sukru Cinar, Murtaza A. Basrai, and Peter M. Chen

**Source:** OSDI 2002; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/844128.844148

## Key insight

Record the nondeterministic inputs to a machine beneath its operating system, then reconstruct its detailed execution by replay. An attacker who compromises the guest kernel cannot thereby rewrite a logger protected outside that guest.

## Basic idea

ReVirt runs the target system in a virtual machine [1] and records the nondeterministic events [2] that affect its architectural state. A checkpoint [3] supplies the starting disk state, while logged input values and precise interrupt positions drive deterministic replay [4]. Ordinary instructions and reproducible disk activity are re-executed instead of being logged individually. The paper's scope is a uniprocessor guest; arbitrary shared-memory multiprocessor interleavings require additional recording and are outside its mechanism.

## Illustrative example

**Record.** A server starts from a powered-off virtual-machine disk image. It receives a packet containing an exploit, executes a loop, and takes a virtual timer interrupt during the loop's seventh iteration. ReVirt records the packet bytes and the information needed to inject the interrupt at the same execution point.

A program counter alone is insufficient because the loop visits the same instruction repeatedly. ReVirt also records the number of executed branches since the preceding interrupt. For an interruptible repeated-string instruction on x86, the remaining-iteration register value disambiguates progress within that instruction.

**Replay.** Start another execution from the saved disk image. Suppress fresh asynchronous virtual interrupts and supply the recorded packet rather than accepting arbitrary new input. Hardware branch counters bring execution near the recorded interruption point; breakpoints and checks locate the exact point because counter-triggered interrupts can arrive late. Inject the original virtual interrupt there.

Reads from the reconstructed virtual hard disk need not be logged as independent external input: their contents follow from the initial disk and replayed writes. Clock reads and other genuinely external results do require control. The prototype traps or substitutes relevant nondeterministic processor operations rather than assuming ordinary arithmetic replay covers them.

**Inspect.** An investigator can examine the guest's registers, memory, and kernel state before and after the exploit, using repeated replay to ask questions not anticipated when logging began. The log need not have contained a bespoke event such as "attacker changed this function pointer" if that change can be reconstructed from the recorded execution.

**Trust boundary.** Compromising the guest is different from compromising the host, virtual-machine monitor, or log storage. ReVirt relies on those lower layers remaining protected and on every relevant nondeterministic input being captured. The result is reproducibility under that boundary, not a proof that the entire host is immune to attack.

## Concepts and terms

**[1] Virtual machine.** An execution environment whose privileged operations and external interactions are mediated by a lower software layer. ReVirt's UMLinux-based structure places logging outside the target operating system.

**[2] Nondeterministic event.** An input or timing decision not determined by the saved initial state and preceding modeled computation, such as packet data or delivery of an asynchronous interrupt.

**[3] Checkpoint.** A saved starting state for replay. The paper's implementation begins from a powered-off guest, so a copy of its virtual disk supplies that state.

**[4] Deterministic replay.** Re-execution that reproduces the original architectural behavior by supplying identical external values at identical execution points, rather than attempting to reproduce every microarchitectural cache event.

# A VLIW Architecture for a Trace Scheduling Compiler

**Summary by:** GPT 6 Astra

**Author:** Robert P. Colwell, Robert P. Nix, John J. O'Donnell, David B. Papworth, Paul K. Rodman

**Source:** ASPLOS 1987; ASPLOS Influential Paper Award 2021

**Link:** https://doi.org/10.1145/36206.36201

## Key insight

A compiler can schedule independent operations into wide instructions across likely branch paths, allowing hardware to execute the resulting schedule with much less dynamic scheduling machinery. Correct execution still requires explicit handling of paths that leave the chosen trace.

## Basic idea

The Multiflow TRACE architecture exposes multiple functional units and their resource constraints through very long instruction words, or VLIW [1]. Its compiler selects likely traces [2] and schedules operations across their basic-block boundaries while respecting dependencies and machine resources [3]. Compensation code [4] repairs the effects of code motion on other paths. The paper presents a compiler-and-hardware co-design, not a claim that arbitrary sequential instructions can execute in parallel.

## Illustrative example

**Choose a trace.** A routine computes `base = x + y`, then takes a frequent branch that uses `base` along with the independent product `u*v`. A rare branch also uses `base`, but does not need that product. Assume the arithmetic in this example has no observable side effects or trapping behavior.

**Schedule the common path.** Consider moving the addition from before the branch into the frequent successor. On a toy machine with an available adder and multiplier, the compiler can place the addition and independent multiplication in the same instruction word. Their results can be consumed only after the required operation latencies have elapsed; a dependent multiplication cannot simply be packed alongside its unfinished input producer.

**Repair the uncommon path.** Moving the addition removed the definition needed by the rare successor. Insert `base = x + y` on that path before its use. This compensation restores the computation that the original program performed. A profitable trace schedule must account for the added code and the cost paid when the uncommon branch is taken.

**Honor the machine.** If operands reside in different register-file clusters, needed transfers and communication resources also enter the schedule. Having enough arithmetic units does not imply enough register ports, buses, or memory bandwidth for every proposed instruction word.

## Concepts and terms

**[1] VLIW.** One instruction word explicitly encodes multiple operations assigned to functional units. The compiler determines much of the execution schedule rather than asking hardware to discover it dynamically. Actual parallelism depends on available independent operations and the particular machine organization.

**[2] Trace.** A selected likely path through the control-flow graph, based on profiling or heuristics. Treating it as a larger scheduling region exposes opportunities hidden by individual basic blocks. Other paths remain part of the program and must retain their semantics.

**[3] Resource-constrained scheduling.** Place operations according to data dependencies, operation latencies, register availability, memory accesses, and communication resources. The TRACE design organizes resources to make such compilation feasible; the compiler does not assume an infinitely ported central register file.

**[4] Compensation.** Additional operations on off-trace edges preserve values and effects disrupted by scheduling across branches. It is not a general license to speculate unsafe loads, exceptions, or externally visible writes. Trace selection, scheduling, and compensation repeat until the remaining program paths have also been compiled.

# A Comparison of Software and Hardware Techniques for x86 Virtualization

**Summary by:** GPT 6 Astra

**Author:** Keith Adams, Ole Agesen

**Source:** ASPLOS 2006; ASPLOS Influential Paper Award 2020

**Link:** https://doi.org/10.1145/1168857.1168860

## Key insight

Hardware virtualization support does not automatically make every virtual-machine operation cheaper. Software translation can replace frequently trapping operations with specialized code, while hardware execution can still pay heavily for virtual-memory management.

## Basic idea

The paper compares VMware's software virtual machine monitor with the first-generation hardware support evaluated in 2006 [1]. Software binary translation [2] rewrites guest-kernel instructions while permitting suitable user code to execute directly. Both approaches maintain shadow page tables [3], and adaptive translation [4] can avoid repeatedly faulting on guest accesses to sensitive memory. The comparison isolates event costs and workload behavior rather than treating virtualization as one constant overhead.

## Illustrative example

**Change an address mapping.** A guest kernel updates one of its page-table entries. That entry describes a guest-virtual-to-guest-physical mapping, but the real processor must ultimately access a machine page permitted by the monitor. The monitor therefore maintains a corresponding shadow mapping.

**Keep the shadow coherent.** Write-protecting guest page-table memory makes an ordinary guest store fault. The monitor examines the write and updates its shadow structures. Without this interception, the guest could change its mapping while the processor continued using stale or unauthorized translation state.

**Adapt the software path.** If a translated instruction repeatedly triggers this fault, the software monitor replaces its direct translation with a specialized simulation or helper path. Subsequent executions update the virtualized state without paying the same hardware-fault path each time. If the instruction's behavior changes, the translation can adapt again.

**Compare the hardware path.** In the evaluated hardware-assisted design, the guest executes instructions natively in guest mode, but its page-table update can still require an exit and monitor work. Native instruction execution therefore does not eliminate the cost of maintaining shadow translations. A workload dominated by ordinary user arithmetic can behave very differently from one frequently switching address spaces or modifying mappings.

## Concepts and terms

**[1] Virtual machine monitor.** Software that presents a guest with a virtual processor and resources while enforcing isolation from the host and other guests. Hardware virtualization supplies execution modes and interception controls; it does not replace all monitor functionality. The paper's results concern specific early implementations, not a timeless ranking of all software and hardware-assisted designs.

**[2] Binary translation.** Translate guest instruction sequences into cached executable code that preserves guest-visible behavior. Ordinary instructions can remain similar, while privileged operations and control transfers require rewriting or helpers. Guest user-mode code often runs directly, so the software approach is not instruction-by-instruction interpretation of the entire workload.

**[3] Shadow page table.** A monitor-controlled mapping from guest virtual addresses to machine memory, derived from guest mappings and the monitor's resource assignments. The monitor distinguishes genuine guest faults from faults caused by missing shadow state or write protection used for tracking.

**[4] Adaptive translation.** Specialize translated instructions after observing repeated expensive behavior, such as stores to traced page-table memory. Patching the cached translation avoids repeated traps while preserving the required emulation. The evaluated hardware lacks equivalent hardware support for the full memory-virtualization problem; later or different designs require their own comparison.

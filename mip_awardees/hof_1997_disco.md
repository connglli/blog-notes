# Disco: Running Commodity Operating Systems on Scalable Multiprocessors

**Summary by:** GPT 6 Astra

**Author:** Edouard Bugnion, Scott Devine, and Mendel Rosenblum

**Source:** SOSP 1997; SIGOPS Hall of Fame Award 2008

**Link:** https://doi.org/10.1145/268998.266672

## Key insight

A virtual-machine monitor can adapt existing operating systems to a large nonuniform-memory machine without making each kernel manage the whole machine. The monitor can improve locality and share redundant memory underneath those smaller systems.

## Basic idea

Disco runs multiple commodity operating-system instances in virtual machines [1] on a cache-coherent NUMA machine [2]. A physical-to-machine mapping [3] lets the monitor virtualize memory and move pages without changing guest-visible addresses. Page migration and replication [4] improve locality, while copy-on-write sharing [5] reduces duplicate code and file-buffer contents across guests. Guest systems cooperate using familiar distributed-system protocols rather than becoming one globally shared kernel. The prototype requires targeted guest adaptations, so it is not a claim of universal unmodified-guest compatibility.

## Illustrative example

**Partition management.** A machine has two processor nodes with separate local memories. VM A runs a small operating-system instance mainly on node 0, while VM B runs another mainly on node 1. Each guest sees physical memory starting at address zero, but Disco maps those guest pages to distinct machine frames as needed.

**Translate.** On the paper's MIPS platform, a guest tries to install a virtual-to-physical translation in the translation lookaside buffer. Disco intercepts that operation, substitutes the machine frame corresponding to the guest physical page, and preserves the relevant protection bits. Ordinary accesses then use hardware translation directly rather than trapping on every load.

**Improve locality.** A page mapped by VM A resides on node 1 but is heavily accessed from node 0. Hardware cache-miss information can justify moving it to node 0. Disco invalidates stale translations, copies the page, and updates its mapping. If a page is primarily read-shared across nodes, separate read-only copies can reduce remote traffic. Writes require the replication and protection protocol to restore the appropriate single writable state.

**Avoid duplicate buffers.** Both VMs read the same eligible read-only disk block. Disco can arrange for their apparent buffer pages to share one machine page, protected by copy-on-write. If A modifies its copy, a private frame preserves B's contents. This is inter-VM sharing of identical backing data, not permission for arbitrary guest writes to change another guest's private buffer.

**Limits.** Pages actively written by several nodes do not obtain the same benefit from read replication. Migration also has a cost, so the policy limits movement rather than chasing every access. The guests can communicate through virtual networking and file protocols, but that does not turn every application into a scalable parallel program or provide automatic recovery from all guest failures.

## Concepts and terms

**[1] Virtual machine.** A protected apparent processor, memory, and device environment managed by a lower monitor. Multiple guest kernels can divide the system-management load.

**[2] Cache-coherent NUMA.** A shared-memory machine whose access latency depends on memory location while hardware maintains cache coherence. Locality management improves performance rather than supplying missing coherence correctness.

**[3] Physical-to-machine mapping.** The monitor's translation from a guest's apparent physical pages to real hardware frames, composed with the guest's virtual-address translation.

**[4] Migration and replication.** Moving a page toward its main accessing node or making read-only copies near readers. Translation invalidation and write handling preserve the memory contract.

**[5] Copy-on-write sharing.** Several guest mappings share unchanged contents until a write requires a private copy, reducing memory duplication without merging their private modifications.

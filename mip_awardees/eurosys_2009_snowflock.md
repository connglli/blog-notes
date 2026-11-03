# SnowFlock: Rapid Virtual Machine Cloning for Cloud Computing

**Summary by:** GPT 6 Astra

**Author:** H. Andrés Lagar-Cavilla, Joseph Andrew Whitney, Adin Matthew Scannell, Philip Patchin, Stephen M. Rumble, Eyal de Lara, Michael Brudno, Mahadev Satyanarayanan

**Source:** EuroSys 2009; EuroSys Test-of-Time Award 2019

**Link:** https://doi.org/10.1145/1519065.1519067

**Code:** [SnowFlock](https://sourceforge.net/projects/snowflock/)

## Key insight

Cloning a running virtual machine need not copy all of its memory before the children start. Start them from a small execution descriptor, fetch snapshot pages only when needed, and distribute shared demand across the children together.

## Basic idea

SnowFlock implements virtual-machine fork [1] for rapidly creating stateful workers on different hosts. A compact descriptor [2] restores enough execution state to begin, while memory-on-demand [3] supplies missing pages from an immutable fork-time image. Guest-assisted fetch avoidance [4] skips pages whose inherited contents are unnecessary. Multicast distribution [5] lets a request by one child also populate other children, reducing repeated transfer from the parent.

## Illustrative example

**Fork a prepared service.** A parent VM has loaded a read-only search index and waits for a query. It forks three children to search different index partitions. Each child begins with the parent's logical state and a distinct child identifier; the application uses that identifier to choose its partition.

**Start cheaply.** The parent is briefly quiesced and a descriptor containing execution and mapping metadata is sent to the child hosts. The children can resume without having received every index page. This is fast startup with deferred work, not zero-cost copying of the entire state.

**Demand a page.** Child `one` first accesses an absent index page. The hypervisor traps the access, fetches the page from the preserved snapshot, installs it, and resumes the faulting virtual CPU. A multicast response can also place that page in children `two` and `three` before they request it.

**Avoid irrelevant transfers.** If a child allocates a fresh scratch page that will not use its inherited contents, guest allocation knowledge suppresses fetching the old page. This differs from arbitrarily ignoring a page on which a partial write would leave inherited bytes observable.

**Preserve the snapshot.** If the parent modifies an index page after the fork, copy-on-write preserves its old contents for children that have not fetched it yet. A child's private modifications are not merged into its siblings. Results must be communicated through an application protocol.

## Concepts and terms

**[1] VM fork.** Create multiple VMs with the parent's fork-time machine state, potentially on remote hosts. This extends process-fork-style worker creation to the whole VM. The application still needs a way to divide work and handle external resources whose identities cannot simply be duplicated.

**[2] Descriptor.** A small image of virtual-device metadata, selected shared pages, CPU register state, descriptor tables, and page tables. Host-specific addresses are converted into VM-relative identities and remapped at each destination. The descriptor is not the complete memory image.

**[3] Memory-on-demand.** Track which snapshot pages are present at a child. Trap first accesses to absent pages, transfer their contents, and update the mapping. The parent retains the fork-time image through copy-on-write. The scheme depends on continued availability of that image while children still need it.

**[4] Fetch avoidance.** Guest-kernel information identifies pages whose old bytes are unnecessary, such as freshly allocated storage or appropriate I/O destinations. Avoidance must respect initialization semantics; it is not a universal optimization for every write fault.

**[5] Multicast.** Deliver requested snapshot data to several clone hosts in one distribution operation. Similar access patterns turn another child's demand into useful prefetching. Independent execution remains possible: the distribution mechanism does not require all children to request pages in lockstep.

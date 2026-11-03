# Xen and the Art of Virtualization

**Summary by:** GPT 6 Astra

**Author:** Paul Barham, Boris Dragovic, Keir Fraser, Steven Hand, Tim Harris, Alex Ho, Rolf Neugebauer, Ian Pratt, and Andrew Warfield

**Source:** SOSP 2003; SIGOPS Hall of Fame Award 2023

**Link:** https://doi.org/10.1145/945445.945462

**Code:** [Xen source mirror](https://gitlab.com/xen-project/xen)

## Key insight

An operating system can explicitly cooperate with a virtual-machine monitor while leaving its applications unchanged. This avoids expensive emulation of awkward x86 operations without giving the guest unrestricted access to hardware.

## Basic idea

Xen uses paravirtualization [1]: guest kernels are modified to call a privileged monitor, while ordinary applications retain their binary interface. The monitor isolates domains [2] and validates sensitive operations such as page-table changes through hypercalls [3]. Shared descriptor rings [4] carry asynchronous disk and network requests, with events notifying guests of completion. Keeping resource management beneath the guest kernels allows several operating systems to share one machine without trusting each other's privileged code.

## Illustrative example

**Setup.** Domains A and B each run a modified operating-system kernel and an unmodified text editor. In the paper's 32-bit x86 design, Xen executes at privilege ring 0, guest kernels at ring 1, and applications at ring 3. A owns machine-memory frame 70; B owns frame 91.

**Map memory.** A wants to map frame 70 into an editor process. It prepares a page table in its own memory and registers that table with Xen. The registered page-table memory cannot remain directly writable by A. A requests subsequent updates through Xen, which validates ownership and protection constraints before modifying the hardware-visible table. A request to map B's frame 91 without authorization is rejected. Batching several valid updates amortizes entry into the monitor.

The editor still uses its usual virtual addresses and operating-system calls. It need not understand machine frames or hypercalls. The changed interface is between the guest kernel and Xen, not between the editor and its kernel.

**Issue I/O.** To write a file block, A places a disk-request descriptor in a shared ring. The descriptor identifies the request and refers to an out-of-band data buffer. A advances its producer position and notifies Xen, possibly after enqueuing several requests. Xen validates and schedules requests, places completions in the response portion of the ring, and sends an event. Request identifiers let A match results even when operations complete out of order.

**Isolation boundary.** A malicious guest cannot bypass validation by editing a registered page table directly or by executing ring-0 instructions. Resource scheduling and accounting are still necessary: memory protection alone does not keep A from consuming the CPU time or I/O bandwidth that B needs. This is the paper's paravirtualized interface, not a claim that its 2003 design runs arbitrary unmodified guest kernels.

## Concepts and terms

**[1] Paravirtualization.** Exposing an explicitly virtualized machine interface that differs from the physical machine in selected operations. Guest operating systems are ported to it; the ordinary application interface can remain compatible.

**[2] Domain.** Xen's resource and protection container for a guest operating system and its applications. Xen controls the domain's physical-memory access and allocation of shared hardware resources.

**[3] Hypercall.** A synchronous call from a guest into the monitor, analogous to an application's system call into its kernel. Validation prevents guest-supplied arguments from granting forbidden access.

**[4] Descriptor ring.** A bounded circular communication structure with producer and consumer positions. Descriptors refer to buffers rather than embedding their contents; asynchronous notification can be batched separately from queue updates.

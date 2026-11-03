# Machine-Independent Virtual Memory Management for Paged Uniprocessor and Multiprocessor Architectures

**Summary by:** GPT 6 Astra

**Author:** Richard Rashid, Avadis Tevanian, Michael Young, David Golub, Robert Baron, David Black, William Bolosky, and Jonathan Chew

**Source:** ASPLOS 1987; SIGOPS Hall of Fame Award 2008

**Link:** https://doi.org/10.1145/36206.36181

## Key insight

The authoritative description of virtual memory need not resemble any processor's page tables. A small machine-dependent layer can maintain hardware mappings as a reconstructible representation while portable structures retain the actual memory semantics.

## Basic idea

Mach describes a task's address space with an address map [1] referring to memory objects [2]. A resident-page table [3] tracks cached object contents, while a machine-specific pmap [4] supplies the hardware mappings needed for execution. External pagers [5] provide object backing through messages, and shadow objects [6] record private modifications for copy-on-write. Keeping these responsibilities separate permits different hardware page-table organizations without rewriting the higher-level mapping and sharing policies.

## Illustrative example

**Map an object.** A process maps a file-backed object O at virtual addresses `0x10000` through `0x11fff`, corresponding to object offsets 0 through 8191. Its portable address-map entry records that relationship and the allowed protections. It does not itself need the exact format of a VAX hardware page-table entry.

**Resolve a fault.** A read at `0x10020` maps to byte offset 32 in O. The kernel looks for the relevant resident object page. If absent, it asks O's pager for the contents. Once supplied, the machine-dependent pmap installs an appropriate translation, and the instruction can resume. Physical memory is treated as a cache of object contents rather than as the complete definition of the address space.

**Copy privately.** A child receives a copy-on-write view of the region. Initially the original object supplies unchanged bytes. When the child writes at offset 32, the kernel creates a private page in a shadow object and directs the child's access there. Reads of unchanged pages can follow the shadow's reference to O instead of copying the entire region eagerly.

Repeated copying can create shadow chains. The kernel removes unnecessary intermediate objects when safe, rather than allowing every lookup to traverse an indefinitely growing history. Shared writable mappings require separate care: they must preserve shared changes, not accidentally acquire private-copy semantics.

**Change hardware.** On another processor, the pmap module might use different tables or registers. It can discard nonessential hardware mappings and reconstruct them on faults from the portable state. It cannot discard correctness: protection reductions and invalidations must take effect before execution could use stale permission. Kernel mappings are an important exception to the general ability to retain only a partial hardware map.

The separation does not make every architecture assumption disappear. The implementation requires appropriate fault recovery and must handle machine-specific protection, translation, and multiprocessor synchronization.

## Concepts and terms

**[1] Address map.** A portable description of virtual-address ranges, their protections and inheritance, and the object regions to which they refer.

**[2] Memory object.** A byte-indexed backing entity representing data independently of its current resident pages or hardware mappings.

**[3] Resident-page table.** Metadata locating physical pages by object and offset and tracking state needed for allocation and paging.

**[4] Pmap.** The machine-dependent representation and operations for hardware address translation. It need not retain every logically valid user mapping if reconstruction remains correct.

**[5] External pager.** A user-level service that supplies and manages a memory object's backing contents through kernel messages.

**[6] Shadow object.** An object holding pages changed through copy-on-write and referring to an underlying object for unchanged data.

# Memory Resource Management in VMware ESX Server

**Summary by:** GPT 6 Astra

**Author:** Carl A. Waldspurger

**Source:** OSDI 2002; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/844128.844146

## Key insight

A hypervisor can reclaim memory more intelligently by making the guest choose which pages to surrender. It can separately remove duplication and adjust allocation according to measured activity without requiring a rewritten guest memory manager.

## Basic idea

ESX separates guest physical pages from machine pages [1], allowing transparent remapping. Ballooning [2] creates memory pressure inside a guest so its own operating system selects pages for reclamation. Content-based sharing [3] merges identical pages with copy-on-write protection, while sampled activity estimates and an idle-memory tax [4] influence allocation among virtual machines. These mechanisms support overcommitment [5], but do not eliminate the cost of paging when active demand exceeds available memory.

## Illustrative example

**Create pressure.** A host has 12 machine pages available for two small guests, each configured with 8 guest physical pages. Guest A uses four actively and caches expendable data in the rest; guest B needs six actively. The example omits hypervisor metadata and uses tiny counts only to expose the mechanism.

The hypervisor asks A's balloon driver to allocate and pin two guest pages. A's operating system satisfies the request from free memory or by reclaiming pages using its own policy. The driver reports the allocated guest page numbers to ESX, which can remove their machine backing. A sees memory consumed by its driver, while the host can reuse the corresponding frames for B.

**Share duplicates.** Suppose A and B also contain identical read-only library pages. ESX hashes candidate contents to find possible matches, then compares complete pages before merging them. Both guest mappings can point to one protected machine page. A later write traps, and the writer receives a private copy. A hash collision alone must never authorize merging unequal data.

**Allocate by use.** Activity sampling identifies that A has a larger idle fraction. The idle-memory tax discounts the effective benefit of retaining unused pages in the sharing policy, while configured shares and reservation constraints still matter. The tax changes allocation incentives; it is not a monetary charge or permission to ignore every reservation.

**Limit.** If the balloon driver is unavailable or cannot reclaim enough, ESX can fall back to swapping. That may interact poorly with guest paging because the hypervisor lacks the guest's knowledge of page value. Even with working ballooning and sharing, two guests simultaneously needing all 16 distinct pages cannot both keep them resident in 12 frames. Overcommitment exploits unused or duplicate memory, not extra physical capacity.

## Concepts and terms

**[1] Guest physical and machine pages.** A guest's physical address names an apparent hardware page. The hypervisor translates it to actual host memory and can change that backing while preserving the guest-visible address.

**[2] Ballooning.** A guest driver allocates pinned memory on hypervisor request, causing the guest's own memory policy to free useful backing capacity for the host. Deflation releases those guest allocations.

**[3] Content-based sharing.** Deduplication after comparing page contents, followed by write protection and private copying on modification. It can share pages regardless of how the guests obtained them.

**[4] Idle-memory tax.** An allocation-policy adjustment based on estimated inactive memory, intended to reclaim idle capacity rather than let a guest retain it solely through its configured shares.

**[5] Overcommitment.** Configuring more apparent guest memory than the host can back simultaneously, relying on changing demand, sharing, or paging to manage the difference.

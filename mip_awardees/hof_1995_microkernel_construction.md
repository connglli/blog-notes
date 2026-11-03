# On micro-kernel construction

**Summary by:** GPT 6 Astra

**Author:** Jochen Liedtke

**Source:** SOSP 1995; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/224056.224075

**Documentation:** [Original L4/x86 availability and development resources](https://os.inf.tu-dresden.de/L4/l4down.html)

## Key insight

A mechanism belongs in the kernel only when moving it outside would prevent required functionality, particularly protection. Fast interprocess communication and hardware-specific implementation make this small interface practical rather than forcing services back into the kernel.

## Basic idea

The paper derives a minimal microkernel [1] around address spaces [2], threads [3], and interprocess communication [4]. Protected mapping operations let user-level services construct memory-management policies while the kernel enforces which pages they may transfer or share. Page faults are communicated to user-level pagers [5], so allocation and backing-store choices need not be built into the kernel. The L4 design also treats processor architecture, cache behavior, and address-space switching costs as constraints on implementation, not details a portable kernel core can always ignore.

## Illustrative example

**Allocate through a pager.** A process P accesses an unmapped virtual page. The kernel stops the faulting thread and sends the fault information to P's designated pager Q. Q decides whether the access is permitted and where its contents should come from. Suppose Q already has access to a suitable initialized page.

**Map.** Q replies using the kernel's mapping mechanism, placing the page into P's address space at an agreed location. Q retains its own mapping, while P can resume the faulting instruction. Q cannot map an arbitrary physical page merely by naming it: it can delegate only pages accessible to itself, and the recipient participates in the transfer.

**Grant through an intermediary.** Suppose a service R mediates between Q and P without wanting to retain every forwarded mapping. Q maps a page to R; R grants its received mapping to P. Granting removes the page from R's address space while installing it in P's. This lets R act as a transient intermediary instead of maintaining a permanent mapping for every page passed through it.

**Revoke.** The paper's flush operation removes mappings derived directly or indirectly from the caller's mapping while retaining the caller's own access. If Q flushes the delegated page, P loses that derived access. The kernel must track enough mapping relationships to enforce this revocation; a user-level pager cannot safely reconstruct protection merely by trusting P to forget an address.

The example combines fault handling, communication, and memory delegation without putting a file system or replacement policy inside the kernel. Its efficiency depends heavily on the communication path. Short messages, scheduling interactions, and processor-specific translation costs must be designed together; simply moving an existing slow kernel's services into processes does not establish a fast microkernel.

## Concepts and terms

**[1] Microkernel.** A privileged core limited to mechanisms necessary to build protected subsystems. Minimality is a criterion about required functionality, not just counting source lines.

**[2] Address space.** A mapping from virtual pages to accessible memory frames, including protection information. Mapping shares access, granting transfers a mapping, and flushing revokes derived mappings.

**[3] Thread.** A schedulable execution context associated with an address space. Several threads can use the same address space without each requiring separate memory ownership.

**[4] Interprocess communication.** A protected transfer of messages between execution contexts, including synchronization of sender and receiver. It is the basis for interaction with user-level services.

**[5] Pager.** A service responsible for responding to a thread's page faults and deciding which mappings to supply. The kernel enforces mapping authority while the pager chooses policy.

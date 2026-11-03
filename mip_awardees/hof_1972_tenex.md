# TENEX, a Paged Time Sharing System for the PDP-10

**Summary by:** GPT 6 Astra

**Author:** Daniel G. Bobrow, Jerry D. Burchfiel, Daniel L. Murphy, and Raymond S. Tomlinson

**Source:** Communications of the ACM 15(3), 1972; SIGOPS Hall of Fame Award 2013

**Link:** https://doi.org/10.1145/361268.361271

## Key insight

Page-level mapping can provide private memory, shared program images, shared data, and file access through one coherent mechanism. Copy-on-write lets programs start from shared initialized state while allocating private copies only where they modify it.

## Basic idea

TENEX combines paging hardware [1] with operating-system interfaces for controlling page mappings. Its maps can describe private pages, shared pages, indirect references to another process's page, and pages backed by files [2]. Copy-on-write [3] preserves sharing until a write requires a private copy. A page fault [4] brings in absent data or handles protection conditions, while process and file interfaces build on these memory mechanisms. The paper also integrates interactive command processing and file protection into the time-sharing environment.

## Illustrative example

**Load an image.** Two users start the same editor. In a simplified image, virtual page 6 contains executable code and page 7 contains initialized tables. Both processes map the same underlying image pages rather than immediately copying all of them into separate memory.

**Read and share.** Reads of page 7 see its initialized values. The mapping hardware resolves a shared entry through the shared page's location information, so moving the backing page between physical and secondary storage does not require independent copies of that location in every process map. An application can also deliberately map a writable shared page for communication, but that has different semantics from private-on-write image state.

**Write privately.** User A changes a table on page 7. A copy-on-write status bit causes the write to trap. The system creates a private page containing the old contents, changes A's mapping to refer to it, and permits the write. B continues using the original page. The code page remains shared because neither process modifies it.

**Map another process or file.** An indirect map entry can refer to a page-table entry belonging to another process. Access follows that entry, including changes made to the owner's mapping. A file-backed map instead supplies page contents from a file. These alternatives are explicit mapping choices; an indirect writable mapping is not automatically isolated by copy-on-write.

**Handle absence and protection.** If a required page is not resident, the system resolves the fault by obtaining its contents before execution continues. If the requested access is prohibited, a fault indicates a protection problem rather than authorizing it. Mapping flexibility therefore depends on access control and correctly maintained page state, not simply on exposing raw physical addresses to users.

The example isolates TENEX's memory mechanism. Its user-facing file model also supplies named, versioned byte streams and access checks; memory mapping does not remove the need to authorize access to the underlying file.

## Concepts and terms

**[1] Paging hardware.** The BBN pager translates virtual addresses and checks read, write, and execute permissions using page tables and cached mapping entries. TENEX pages contain 512 words.

**[2] File-backed page.** A virtual-memory page whose contents are associated with a file rather than only anonymous private storage. Mapping makes the bytes addressable through memory operations.

**[3] Copy-on-write.** Sharing a page until one mapping attempts a write, then replacing that mapping with a private copy. It preserves independent modifications without eager duplication.

**[4] Page fault.** A trap caused by an absent, nonexistent, or insufficiently permitted mapping. Handling depends on the cause; not every fault is a request to read a disk page.

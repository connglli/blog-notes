# The Multics Virtual Memory: Concepts and Design

**Summary by:** GPT 6 Astra

**Author:** André Bensoussan, Charles T. Clingen, and Robert C. Daley

**Source:** Communications of the ACM 15(5), 1972; SIGOPS Hall of Fame Award 2008

**Link:** https://doi.org/10.1145/355602.361306

## Key insight

Segments express meaningful named objects and their access rights; pages manage physical storage efficiently. Combining them lets programs share and directly address large persistent objects without requiring each object to be loaded contiguously into memory.

## Basic idea

Multics presents an idealized segmented memory [1] whose objects have names, lengths, and access permissions. A process's segment descriptors [2] connect its segment numbers to those objects and their permitted uses. Paging [3] divides each segment into fixed-size units that can move independently between primary and secondary storage. Fault handling [4] supplies missing descriptors or pages and enforces protection. Segmentation therefore defines the program-visible organization and sharing, while paging implements its physical realization.

## Illustrative example

**Name and share an object.** Two programs use the same library segment L. Program A refers to L through its segment number 7, while B uses segment number 12. The symbolic object is shared even though its short numeric name differs between their descriptor tables. The descriptor for each process specifies that process's allowed access.

**Translate an address.** A references offset 1500 in L. Using the paper's 1024-word page size, the offset selects page 1 and word 476 within that page. Hardware first uses A's segment descriptor to check the segment's validity, bounds, and permissions, then uses the segment's page table to locate the selected physical frame. Page 0 need not be adjacent to page 1 in physical memory.

**Resolve absence.** If the descriptor or page is not present, a fault transfers control to the supervisor. It resolves the segment reference or loads the missing page, establishes the required translation, and permits the access to be retried if authorized. A protection failure is not permission to fetch and use the data anyway.

**Keep sharing meaningful.** If A has read and execute access while B has only execute access, both may refer to the same stored procedure without receiving identical authority. A writable shared data segment can similarly communicate updates among authorized users. Mapping separate private copies would lose that immediate shared-object meaning.

**Manage storage.** A very large segment can be used while only its currently needed pages are resident. Fixed-size page allocation avoids finding a single contiguous hole for the entire variable-length segment. It still consumes tables and can waste part of a final page; paging does not eliminate all space or translation overhead.

The system aims to let named information be directly addressed rather than requiring applications to maintain a separate explicit read/write staging scheme for every file. Symbolic naming, protection, and storage management still have to agree on which object a reference denotes.

## Concepts and terms

**[1] Segmented memory.** An address space organized as distinct variable-length information objects, accessed by segment identity and offset. Segments support independent sharing and protection.

**[2] Segment descriptor.** Process-relevant metadata used to interpret a segment number, check access and bounds, and reach the segment's storage mapping.

**[3] Paging.** Dividing a segment into equal-size transfer and allocation units. A page table translates a page's position within a segment into its current resident location.

**[4] Fault handling.** Supervisor processing triggered when translation or access cannot proceed directly. Missing information may be installed; unauthorized references must be rejected or handled according to the protection contract.

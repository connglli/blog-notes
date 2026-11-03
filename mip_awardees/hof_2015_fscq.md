# Using Crash Hoare Logic for Certifying the FSCQ File System

**Summary by:** GPT 6 Astra

**Author:** Haogang Chen, Daniel Ziegler, Tej Chajed, Adam Chlipala, M. Frans Kaashoek, and Nickolai Zeldovich

**Source:** SOSP 2015; SIGOPS Hall of Fame Award 2025

**Link:** https://doi.org/10.1145/2815400.2815402

**Code:** [FSCQ SOSP 2015 source](https://github.com/mit-pdos/fscq/tree/sosp15)

## Key insight

Storage correctness must describe intermediate crash states and recovery, not just successful calls. A verified logging layer can hide those intermediate states behind an all-or-nothing interface for higher file-system layers.

## Basic idea

Crash Hoare logic [1] extends preconditions and postconditions with a crash condition and recovery semantics. It models asynchronous disk writes [2], so a crash can preserve only some issued writes unless synchronization constrains them. FSCQ verifies a write-ahead log [3], then reasons about file-system operations using the log's atomic interface. Logical address spaces [4] let specifications describe physical blocks, logical blocks, and files separately. The proofs also cover repeated crashes during recovery, conditional on the modeled disk and trusted execution components behaving as assumed.

## Illustrative example

**Setup.** A tiny file system creates `memo` by setting an inode-allocation bit in block 11 and adding a directory entry in block 24. Initially both changes are absent. The desired recovered state is either that initial state or the state containing both changes, never a directory entry pointing to an unallocated inode.

**Record and commit.** Buffer both new block images in memory. Write their contents and destination addresses to the log, then synchronize the disk. Write a commit header describing the transaction and synchronize again. Copy the logged images to blocks 11 and 24, synchronize, clear the commit header, and synchronize once more. These ordering boundaries prevent the commit header from becoming durable before its data or disappearing before the installed data is durable.

**Recover.** A crash before a durable commit header leaves the old home blocks authoritative. With a committed header, recovery copies both logged images to their destinations, synchronizes them, and clears the header durably. If recovery crashes after copying only block 11, the header still directs the next recovery attempt to repeat both copies. Repeating a complete block-image write produces the same value.

**Prove the interface.** The log's crash condition describes all persistent states reachable during those phases. Recovery must transform any such state into a valid old-or-new logical block map; a crash during recovery must again leave an allowed crash state. The inode and directory proofs use that logical map rather than enumerating each physical log state. Their representation relation connects allocated inodes and directory entries to the higher-level file tree.

The example assumes atomic writes of the commit block and that disk synchronization really persists preceding writes. The paper's proof does not establish that arbitrary hardware, the Haskell compiler and runtime, or its disk and FUSE bindings satisfy those assumptions.

## Concepts and terms

**[1] Crash Hoare logic.** A specification associates a procedure with an initial-state predicate, a successful-result predicate, and a predicate covering persistent states after interrupted execution. Recovery has its own proof obligations, including interruption and re-execution.

**[2] Asynchronous disk writes.** Issuing a write need not make it durable immediately. The model tracks possible on-disk values and pending writes; synchronization restricts the values a subsequent crash can leave.

**[3] Write-ahead log.** A reserved disk region records a transaction's new data before the data replaces its home locations. A durable commit record determines whether recovery installs that data.

**[4] Logical address space.** An abstract collection of addressable objects related to a lower-level representation. It lets one layer specify its own objects without exposing all storage details to clients.

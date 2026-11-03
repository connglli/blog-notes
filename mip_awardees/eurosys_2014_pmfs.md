# System Software for Persistent Memory

**Summary by:** GPT 6 Astra

**Author:** Subramanya R. Dulloor, Sanjay Kumar, Anil Keshavamurthy, Philip Lantz, Dheeraj Reddy, Rajesh Sankaran, Jeff Jackson

**Source:** EuroSys 2014; EuroSys Test-of-Time Award 2024

**Link:** https://doi.org/10.1145/2592798.2592814

**Code:** [PMFS](https://github.com/linux-pmfs/pmfs)

## Key insight

Byte-addressable persistent memory needs a file system designed around memory accesses, not a simulated disk. Removing the block-storage path is useful only if the system also controls which updates survive a crash and in what order.

## Basic idea

PMFS provides file access and direct memory mappings [1] over persistent memory. It combines fine-grained undo logging [2], suitable atomic updates, and copy-on-write for different update sizes. A proposed persistence barrier [3] distinguishes durable data from data merely visible through CPU caches or memory-controller buffers. Temporary kernel write windows [4] reduce accidental corruption of the persistent mappings without changing page tables for every write.

## Illustrative example

**Setup.** A metadata operation must change both a file's length and its allocation-root pointer. Suppose the original pair is `(length = 16, root = old_tree)` and the desired pair is `(length = 24, root = new_tree)`. Seeing only one new field after recovery would leave inconsistent metadata. Assume any newly referenced data has already been made durable.

**Protect the old state.** Before changing a metadata field, append its old contents and address to the transaction's undo log and make that log entry durable. Only then may the field be overwritten. Repeat this order for each changed field; a CPU store followed merely by a normal memory fence is not the paper's durability guarantee.

**Commit.** After updating both fields, flush their cache lines and issue the persistence barrier. Append and persist the transaction's commit record. With this fully durable commit sequence, recovery can retain the new pair. If a crash occurs before a durable commit record exists, recovery restores the logged old values instead.

**Map and protect.** An application can map file data directly from persistent memory, avoiding a separate DRAM page-cache copy. Kernel mappings remain read-only except during short, controlled update windows. The prototype disables interrupts while temporarily relaxing kernel write protection, then restores protection immediately after the stores. These windows address stray kernel writes; they do not turn arbitrary application stores into logged transactions.

## Concepts and terms

**[1] Direct persistent mapping.** Persistent memory supports processor loads and stores and retains data across power loss. PMFS maps this storage directly rather than routing every access through a block device. Memory mapping changes the access path, not the need for application synchronization or crash-consistency protocols.

**[2] Undo logging and recovery.** A transaction records old bytes before replacing them. Recovery discards logs of durably committed transactions and rolls back incomplete ones. PMFS uses cache-line-sized log entries, transaction identifiers, and generation information to recognize valid entries. Small updates may use the paper's assumed atomic-write facilities; larger data updates use copy-on-write. These mechanisms are selected according to the update, not applied indiscriminately.

**[3] Persistence barrier.** The proposed `pm_wbarrier` guarantees durability of writes already flushed from CPU caches. A cache flush and ordering fence alone need not drain volatile memory-controller buffers. The paper's correctness argument depends on this hardware contract. Its optional optimization that delays persisting the commit record allows the latest transaction to roll back after a crash, so it must not be described as strict commit durability.

**[4] Temporal write protection.** PMFS maps persistent pages read-only and briefly clears the processor's kernel write-protection control for authorized writes. Disabling interrupts keeps the update code in control during that window. This is a prototype reliability measure against accidental writes, not isolation from a malicious privileged kernel.

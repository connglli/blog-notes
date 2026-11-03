# A Case for Redundant Arrays of Inexpensive Disks (RAID)

**Summary by:** GPT 6 Astra

**Author:** David A. Patterson, Garth Gibson, and Randy H. Katz

**Source:** SIGMOD 1988; SIGOPS Hall of Fame Award 2011

**Link:** https://doi.org/10.1145/50202.50214

## Key insight

Many small disks can provide parallel bandwidth, but an unprotected array also creates more opportunities for data loss. Redundant layouts recover failed-disk data while making different capacity and performance tradeoffs for large transfers and small updates.

## Basic idea

The paper compares RAID organizations that distribute data across disks through striping [1] and protect it with mirroring or error-checking information [2]. Parity [3] can reconstruct a missing disk block without storing a complete duplicate of every block. Block-level striping permits independent small reads, but small writes must update parity consistently. Distributing parity across disks [4] removes the single parity disk as a universal write bottleneck. Reliability calculations depend on the failure and repair assumptions, not solely on the number of redundant disks.

## Illustrative example

**Build one stripe.** Four disks store three data blocks and one parity block for each stripe. For a tiny one-byte illustration, let data be `6`, `10`, and `12`. Their bitwise XOR is `0`, so parity is `0`. Across later stripes, rotate which disk stores parity instead of assigning all parity blocks to one disk.

**Recover a failure.** If the disk holding value `10` fails, reconstruct that block as `6 XOR 12 XOR 0 = 10`. The calculation works because XOR cancels each surviving data contribution from the parity equation. It assumes the remaining blocks are valid and that the failed location is identified; one parity equation cannot recover two independently missing values in the stripe.

**Update a block.** Change the first value from `6` to `7`. Without reading the entire stripe, compute `new_parity = old_parity XOR old_data XOR new_data`, which gives `1`. A small read-modify-write therefore reads old data and parity, then writes new data and parity. If they are not cached, that entails four disk accesses, although accesses to separate disks can overlap.

**Distribute contention.** In a dedicated-parity layout, every small write in the group touches the same parity disk. Rotating parity means writes to different stripes can use different data/parity disk pairs. This improves available concurrency but does not make two conflicting updates to the same stripe independent.

**Interpret fault tolerance.** Redundancy must be rebuilt after failure, and a second failure during that vulnerable interval can lose data under this single-parity scheme. Correlated failures weaken calculations based on independence. Keeping data and parity crash-consistent also requires appropriate update and recovery mechanisms; the XOR equation alone is not a complete power-failure protocol.

## Concepts and terms

**[1] Striping.** Dividing logical data among multiple disks so accesses can exploit several devices. Stripe granularity affects whether a request engages all disks or only selected ones.

**[2] Mirroring and redundancy.** Mirroring stores another full copy; coding stores less direct recovery information. Both consume capacity to tolerate specified failures, but have different update and repair costs.

**[3] Parity.** The bitwise XOR of data units in a group. With exactly one known missing unit, XOR of parity and the remaining units reconstructs it.

**[4] Distributed parity.** Placing different stripes' parity on different disks, as in the paper's fifth RAID level, so all small writes need not contend for one dedicated check disk.

# The Design and Implementation of a Log-Structured File System

**Summary by:** GPT 6 Astra

**Author:** Mendel Rosenblum and John K. Ousterhout

**Source:** ACM Transactions on Computer Systems 10(1), 1992; SIGOPS Hall of Fame Award 2012

**Link:** https://doi.org/10.1145/146941.146943

## Key insight

Buffering modifications and writing them together into a sequential log can avoid many small random disk writes. Efficient reuse then depends on identifying obsolete versions and cleaning segments without repeatedly copying too much live data.

## Basic idea

Sprite LFS writes new file data and metadata into a segmented log [1] rather than overwriting their old locations. An inode map [2] locates each file's current metadata despite its changing disk address. Segment summaries [3] identify logged blocks so a cleaner [4] can retain live versions and reclaim obsolete ones. A cost-benefit cleaning policy [5] weighs free space against copying work and the expected lifetime of retained data. Checkpoints [6] provide a recovery starting point, with later log records supporting roll-forward recovery.

## Illustrative example

**Append a modification.** File `draft` has two data blocks. An edit replaces its second block. LFS appends the replacement data, a new inode pointing to the unchanged first block and the replacement second block, and the necessary inode-map update. The old second block and inode remain physically present but are no longer current.

**Read by indirection.** To open `draft`, use its inode number to consult the inode map, then follow the current inode's pointers. Searching the entire log for the newest copy on every read is unnecessary. Recently used index information can remain cached in memory.

**Clean.** Consider a four-block segment containing one current data block and three obsolete versions. Its summary identifies each block's file and position. The cleaner checks current metadata to distinguish the live block from old versions, writes the live block into a new log segment, and updates its pointers. Once the relocation is safely represented, the old segment can be reused. Reclaiming its four blocks cost copying one live block, yielding three blocks of net free capacity in this simplified accounting.

**Choose segments.** A segment full of long-lived data is expensive to clean for little immediate space. A lightly occupied segment containing old surviving data may be attractive because the space recovered is large and unlikely to disappear quickly through repeated rewrites. The paper's cost-benefit policy combines utilization and age, and groups live data to separate hotter from colder contents.

**Recover.** A checkpoint records where the current inode-map and related structures can be found. Recovery loads the last completed checkpoint and scans later log material to recover additional valid changes. Directory operations need their own consistency bookkeeping; appending bytes alone does not prove that every namespace operation survives a crash correctly.

Cleaning cost depends on the live fraction of selected segments, not simply total disk occupancy. When nearly all candidate segments contain mostly live data, copying overhead can erode the sequential-write advantage.

## Concepts and terms

**[1] Segmented log.** Disk space divided into large regions that are filled sequentially with new versions of data and metadata. Obsolete versions remain until their regions are reclaimed.

**[2] Inode map.** An index from stable inode numbers to the current disk locations of inodes. Inodes themselves contain the file's data-block pointers.

**[3] Segment summary.** Metadata recording which file and logical block each stored block belongs to, used to locate its current owner and determine liveness.

**[4] Cleaner.** A component that reads selected segments, relocates their live contents, and releases the old regions for sequential reuse.

**[5] Cost-benefit cleaning.** Selecting segments using the space recovered, work required, and age of surviving data rather than choosing solely by the smallest live fraction.

**[6] Checkpoint.** A consistently recorded set of locations describing a recoverable file-system state. Roll-forward examines valid later log records instead of restarting from the beginning of the disk.

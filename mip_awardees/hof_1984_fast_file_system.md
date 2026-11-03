# A Fast File System for UNIX

**Summary by:** GPT 6 Astra

**Author:** Marshall K. McKusick, William N. Joy, Samuel J. Leffler, and Robert S. Fabry

**Source:** ACM Transactions on Computer Systems 2(3), 1984; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/989.990

## Key insight

Disk layout should reflect which data is accessed together and the cost of moving a disk head. Large transfer blocks and small allocation fragments can improve throughput without wasting a full large block on every small file.

## Basic idea

The Fast File System groups nearby disk cylinders into cylinder groups [1], each with allocation metadata, inodes [2], and data space. Allocation policies try to keep related files and their data near one another while spreading directories and large files enough to avoid exhausting a group. Large blocks [3] reduce per-transfer overhead; fragments [4] allocate small files and partial tails more economically. Rotational placement [5] and free-space reserves preserve useful placement choices on the rotating disks targeted by the paper.

## Illustrative example

**Choose a layout.** Consider a simplified disk with four cylinder groups, 8 KiB blocks, and 1 KiB fragments. A directory `notes` has its inode in group 1. When creating a small file inside it, the allocator prefers an inode in that group and nearby data space, assuming enough space remains.

**Allocate efficiently.** A 10 KiB file needs one full 8 KiB block and a 2 KiB tail occupying two contiguous fragments within another block. Reserving two full blocks would consume 16 KiB; the fragment arrangement consumes 10 KiB in this idealized allocation, excluding metadata. The remaining fragments can serve other tails or small files.

**Grow and place.** If the tail grows beyond one block, the file system allocates a full block and moves the tail's contents as required, then allocates space for the new final tail. Full blocks must be properly aligned; free fragments straddling a block boundary do not constitute a free full block.

Sequential blocks are placed nearby, but the next block need not be physically adjacent. On a rotating disk, controller and software processing may make an immediately adjacent sector pass before the next transfer can start. Choosing an appropriate rotational gap can avoid waiting a full rotation. Large files eventually spread into additional groups so one file does not consume all the local space needed by its neighbors.

**Preserve choices.** If nearly every block is allocated, finding well-placed runs becomes difficult. Reserving free space gives placement policies room to work; the reserve is a performance mechanism rather than usable capacity for ordinary users. The benefits depend on the storage device's geometry and access costs, so this example does not claim that explicit rotational scheduling is appropriate for a solid-state drive.

## Concepts and terms

**[1] Cylinder group.** A region of nearby disk cylinders with its own free-space bitmap, inode allocation, and related bookkeeping. Local placement reduces mechanical seek distance.

**[2] Inode.** A file's metadata record, including ownership, size, and pointers used to locate its contents. A directory associates names with inode identifiers.

**[3] Block.** The main unit used for allocating and transferring most file data. Larger blocks amortize overhead but would waste space for small files if no smaller allocation unit existed.

**[4] Fragment.** An addressable subdivision of a file-system block used for small files and final partial blocks. Allocation must respect the enclosing block's alignment.

**[5] Rotational placement.** Choosing a block's position on a track with transfer and processing delays in mind, so it reaches the head when the system can use it.

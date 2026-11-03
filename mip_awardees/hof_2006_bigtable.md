# Bigtable: A Distributed Storage System for Structured Data

**Summary by:** GPT 6 Astra

**Author:** Fay Chang, Jeffrey Dean, Sanjay Ghemawat, Wilson C. Hsieh, Deborah A. Wallach, Mike Burrows, Tushar Chandra, Andrew Fikes, and Robert E. Gruber

**Source:** OSDI 2006; SIGOPS Hall of Fame Award 2016

**Link:** https://www.usenix.org/legacy/event/osdi06/tech/chang.html

## Key insight

A sorted, versioned map gives applications control over locality without requiring a full relational database. Splitting contiguous row ranges across servers and buffering updates before writing sorted files supports large, sparse datasets.

## Basic idea

Bigtable stores values indexed by row, column, and timestamp in a sparse sorted map [1]. Consecutive row ranges form tablets [2], each served by one tablet server at a time. Updates enter a durable commit log [3] and an in-memory memtable [4]; older data resides in immutable SSTables [5]. Reads combine these representations, and compaction [6] bounds the number of files and removes obsolete entries. Atomicity is provided for operations on one row, not general transactions spanning arbitrary rows.

## Illustrative example

**Choose locality.** A sensor application uses row keys `station17/2026-10-01` and `station17/2026-10-02`, with column `reading:temperature`. Lexicographic order places a station's adjacent dates together. Column families, such as `reading`, are declared, while qualifiers within a family can vary. A cell can retain multiple timestamped values according to its configured retention policy.

**Write.** A client locates the tablet containing the first row and sends a mutation to its tablet server. The server records the update in its commit log and adds it to the sorted memtable. A mutation affecting several columns in this row can be atomic; updating a second station's row is a separate operation under this interface.

**Read and compact.** Suppose an old temperature value is in an SSTable while a newer timestamped value is in the memtable. A read must consider both sources and apply its timestamp/version selection. When the memtable grows beyond a threshold, the server freezes it, starts another, and writes the frozen contents as an SSTable. Background merging reduces the number of files that reads must examine.

A deletion entry must suppress an older value still present in another file. It cannot simply disappear during a partial merge. A major compaction that includes all of a tablet's SSTables can remove deleted data and the corresponding deletion information safely.

**Recover and distribute.** If the tablet server fails, a replacement reconstructs the tablet using its SSTables and committed updates after the recorded log replay points. Persistent files reside in GFS, rather than only on the failed tablet server. As a tablet grows, splitting its row range permits separate assignment and load balancing. Clients use cached tablet-location metadata and communicate directly with the serving tablet server.

## Concepts and terms

**[1] Sparse sorted map.** A mapping `(row, column, timestamp) -> bytes` in which absent cells consume no ordinary cell entry. Rows sort lexicographically; timestamps distinguish cell versions.

**[2] Tablet.** A contiguous range of rows and the unit of distribution and load balancing. Row-key design therefore affects which data is colocated.

**[3] Commit log.** A durable sequence of redo records that permits committed updates not yet incorporated into sorted files to be reconstructed after failure.

**[4] Memtable.** A sorted in-memory buffer containing recent updates, consulted together with persistent tables during reads.

**[5] SSTable.** An immutable sorted file with an index for locating blocks. Immutability simplifies sharing, caching, and concurrent reading.

**[6] Compaction.** Combining sorted representations into new files while respecting version-retention and deletion rules. Minor compaction flushes a memtable; merging compaction combines files; major compaction covers all tablet SSTables.

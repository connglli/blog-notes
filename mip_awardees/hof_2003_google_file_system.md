# The Google File System

**Summary by:** GPT 6 Astra

**Author:** Sanjay Ghemawat, Howard Gobioff, and Shun-Tak Leung

**Source:** SOSP 2003; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/945445.945450

## Key insight

A distributed file system can remain operational despite routine component failures by replicating large chunks and separating metadata coordination from bulk transfer. Its consistency contract should match the application's append-heavy workload rather than imitate every local-file-system guarantee.

## Basic idea

GFS divides files into large chunks [1] replicated on chunkservers, with a master [2] managing metadata and placement. Clients obtain chunk locations from the master and transfer data directly to chunkservers. A lease-selected primary [3] orders mutations, which secondary replicas apply in the same order. Record append [4] lets concurrent writers add complete records without choosing offsets, but can create duplicates or padding after retries. Applications must interpret that contract and handle failures instead of assuming general POSIX file semantics.

## Illustrative example

**Locate.** Several workers append result records to `measurements`. The client asks the master for the current chunk's primary and replica locations, then caches that metadata. The file contents do not flow through the master.

**Transfer and order.** For a record `sample-42`, the client pushes the data to all relevant replicas. After they have buffered it, the client sends the mutation request to the primary. The primary chooses the record's append offset and its position in the mutation order, applies it locally, and directs secondaries to apply it at that offset. The primary returns success after the required replica processing succeeds.

**Retry.** Suppose one replica writes the record but a communication failure prevents the client from learning a successful outcome. Retrying can append `sample-42` again. A successful record append promises that the record appears atomically at least once; it does not promise exactly one copy. Readers can use an application-level record identifier and checksum to recognize duplicates and reject incomplete or invalid material.

**Handle a boundary.** If the record does not fit within the current chunk, the primary can pad the remaining space and tell the client to retry in the next chunk. Readers therefore cannot treat every byte between valid records as another valid record. Ordinary writes have a different contract and must not inherit record append's all-or-nothing record guarantee by analogy.

**Repair.** The master monitors chunkservers and restores replica counts when machines fail. Chunk version numbers help identify stale replicas after lease changes, and checksums detect damaged data. These mechanisms need surviving valid copies and working communication; replication does not make simultaneous loss of all copies recoverable.

## Concepts and terms

**[1] Chunk.** A large fixed-size unit of file partitioning, identified by a stable handle. The paper uses 64 MiB chunks, reducing metadata and coordination overhead for its large-file workload.

**[2] Master.** A coordinator for namespace, file-to-chunk mapping, leases, placement, and recovery activity. Keeping bulk reads and writes off this path avoids centralizing data bandwidth.

**[3] Primary and lease.** The replica temporarily authorized by the master to choose mutation order for a chunk. Other replicas follow that order rather than independently ordering concurrent requests.

**[4] Record append.** An operation in which GFS chooses the offset and guarantees an entire successfully appended record appears at least once. Retries may leave duplicates, and unused chunk tails may contain padding.
